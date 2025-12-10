import os
os.environ["HF_HOME"] = "./hf_models"
os.environ["HF_DATASETS_CACHE"] = "./hf_datasets"
print("--- 1단계: 환경 변수 설정 완료 ---") # <<< 이 줄을 추가합니다.

import json
import pandas as pd
import re
import numpy as np  
import torch
import faiss
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer
from transformers import AutoModelForCausalLM, AutoTokenizer, AutoTokenizer

# 1. 데이터 로딩
# 🚨 수정: 크롤링 결과 파일명 'documents.json'에 맞게 수정
data_file = "documents.json"
with open(data_file, 'r', encoding='utf-8') as f:
    # 🚨 product_data 구조가 [{'title': ..., 'text': ...}] 이므로, 
    # 실습 코드의 product/review 키에 맞게 수정하여 로딩합니다.
    loaded_data = json.load(f)
    product_data = []
    for item in loaded_data:
        # 크롤링 결과 키: 'title' -> 'product', 'text' -> 'review'로 변경하여 저장
        product_data.append({'product': item['title'], 'review': item['text']})


print(f"불러온 데이터 개수: {len(product_data)}")

# 2. 텍스트 정제 함수 (동일)
def clean_text(text):
    if not text:
        return ""
    text = re.sub(r'^의견', '', text)
    text = re.sub(r'^후기', '', text)
    text = re.sub(r'[\t\r\n]+', ' ', text)
    # text = re.sub(r'[!@#$%^&*(),\"\']', '', text) # 문장부호 유지하여 분석 정확도 높임
    text = re.sub(r'\s+', ' ', text).strip()
    return text

# 3. DataFrame 생성 및 전처리 (동일)
df = pd.DataFrame(product_data)  # [{'product': ..., 'review': ...}]
df.fillna("", inplace=True)
df['clean_review'] = df['review'].apply(clean_text)
df.drop('review', axis=1, inplace=True)


# 4. BM25 모델 구축 (동일)
tokenized_corpus = [doc.split() for doc in df['clean_review']]
bm25 = BM25Okapi(tokenized_corpus)

def bm25_search(query, top_n=5):
    query_tokens = query.split()
    scores = bm25.get_scores(query_tokens)
    sorted_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
    results = []
    for idx in sorted_indices[:top_n]:
        results.append({
            'index': idx,
            'product': df.iloc[idx]['product'],
            'clean_review': df.iloc[idx]['clean_review'],
            'score': scores[idx]
        })
    return results

# 5. Sentence-BERT 임베딩
# 🚨 주의: 이 단계는 시간이 오래 걸리며, CPU/RAM 사용량이 높습니다.
model_name = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
sbert = SentenceTransformer(model_name)

corpus_embeddings = sbert.encode(df['clean_review'].tolist(), convert_to_tensor=True)
corpus_embeddings = corpus_embeddings.cpu().detach().numpy().astype('float32')

# 6. FAISS 인덱스 생성
emb_dim = corpus_embeddings.shape[1]
# 🚨 CPU 환경이라면 IndexFlatIP 대신 IndexFlatL2를 고려
index = faiss.IndexFlatIP(emb_dim) 
index.add(corpus_embeddings)
print(f"FAISS에 {index.ntotal}개의 벡터가 등록되었습니다.")

# 7. Dense Search 함수 (동일)
def dense_search(query, top_n=5):
    query_emb = sbert.encode([query], convert_to_tensor=False).astype('float32')
    D, I = index.search(query_emb, top_n)
    results = []
    for idx, score in zip(I[0], D[0]):
        results.append({
            'index': idx,
            'product': df.iloc[idx]['product'],
            'clean_review': df.iloc[idx]['clean_review'],
            'score': float(score)
        })
    return results

# 8. LLM 모델 로딩 및 RAG 실행
# 🚨 LLM 로딩 전 GPU 메모리를 확보해야 합니다.
# 🚨 Qwen/Qwen3-4B 모델은 GPU 메모리 요구량이 높습니다.
model_name_or_path = "Qwen/Qwen3-4B"

print(f"\n>> LLM 모델 로딩 시작: {model_name_or_path}")
model = AutoModelForCausalLM.from_pretrained(
    model_name_or_path,
    torch_dtype=torch.bfloat16,     # bfloat16 사용
    device_map="auto",              # GPU 자동 할당
    trust_remote_code=True
)
print(">> LLM 모델 로딩 완료.")

tokenizer = AutoTokenizer.from_pretrained(model_name_or_path, use_fast=True)


def generate_answer_with_qwen(context_docs, user_question):
    # 문맥 구성
    context_str = "\n\n".join([
        f"[{i+1}] 제품명: {doc['product']}\n리뷰: {doc['clean_review']}"
        for i, doc in enumerate(context_docs)
    ])

    # 프롬프트 구성 (Qwen 채팅 포맷)
    system_prompt = "당신은 제품 리뷰 분석 및 추천 전문가입니다."
    user_prompt = (
        f"{context_str}\n\n"
        f"사용자 질문: {user_question}\n"
        "추천 제품과 그 이유를 한글로 간결하고 명확하게 서술해주세요."
    )

    prompt = (
        f"<|im_start|>system\n{system_prompt}<|im_end|>\n"
        f"<|im_start|>user\n{user_prompt}<|im_end|>\n"
        f"<|im_start|>assistant\n"
    )

    # Tokenize with attention mask
    inputs = tokenizer(prompt, return_tensors="pt", padding=True, truncation=True).to(model.device)

    # Generate
    output = model.generate(
        input_ids=inputs["input_ids"],
        attention_mask=inputs["attention_mask"],
        temperature=0.7,
        top_p=0.95,
        do_sample=True,
        max_new_tokens=768,      # 더 여유 있게 증가
        repetition_penalty=1.1
    )

    decoded = tokenizer.decode(output[0], skip_special_tokens=True)

    if "<|im_start|>assistant" in decoded:
        answer = decoded.split("<|im_start|>assistant")[-1].strip()
    else:
        answer = decoded.strip()
        
    # Qwen 모델의 Think 토큰 처리
    if "</think>" in answer:
        answer = answer.split("</think>")[-1].strip()
    elif "<think>" in answer:
        answer = answer.split("<think>")[-1].strip()

    return answer


# 9. RAG 실행
user_question = "배터리 오래가는 노트북 추천해줘" # 실제 질문
query = "배터리" # 검색용 키워드/질문

print(f"\n🔍 [Dense Search 실행] - 검색어: '{query}'")
dense_results = dense_search(query)

print("\n--- 검색된 문맥(Context) ---")
for i, r in enumerate(dense_results):
    print(f"[{i+1}] 제품: {r['product']} (Score: {r['score']:.4f})")
    print(f"   리뷰: {r['clean_review'][:50]}...\n")


print(f"\n🧠 [LLM 답변 생성 시작] - 질문: '{user_question}'")
answer = generate_answer_with_qwen(dense_results, user_question)
print("\n===============================")
print("[LLM 답변]")
print(answer)
print("===============================")