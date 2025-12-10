# 💻 RAG 기반 제품 리뷰 분석 시스템 (Qwen-4B, FAISS)

이 프로젝트는 **검색 증강 생성(RAG, Retrieval-Augmented Generation)** 아키텍처를 사용하여 방대한 제품 리뷰 데이터에서 사용자의 질문에 가장 관련성 높은 정보를 검색하고, 대규모 언어 모델(LLM)인 **Qwen-4B**를 활용하여 최종적인 추천 답변을 생성하는 시스템입니다.

## ✨ 주요 기능

* **데이터 로딩 및 정제:** 크롤링된 JSON 데이터 (`documents.json`)를 로드하고 텍스트 정제 작업을 수행합니다.
* **검색 모델 구축:**
    * **Sparse Search (희소 검색) 대비:** BM25 모델 구축.
    * **Dense Search (밀집 검색):** 의미 기반 검색을 위한 Sentence Transformer 임베딩 및 **FAISS** 인덱스 구축.
* **LLM 기반 답변 생성:** 검색된 문맥(Context)을 Qwen/Qwen3-4B 모델에 전달하여 사용자의 구체적인 질문에 대한 맞춤형 추천 답변을 생성합니다.

## ⚙️ 환경 설정 및 설치

프로젝트 실행은 **Python 가상 환경** 내에서 진행하는 것을 권장합니다.

### 1. 가상 환경 생성 및 활성화

프로젝트 폴더(`C:\Users\darkz\rag`)에서 터미널을 열고 다음 명령어를 실행합니다.

```bash
# 가상 환경 생성 (vsc_env 이름으로 생성)
python -m venv vsc_env

# 가상 환경 활성화 (Windows 기준)
.\vsc_env\Scripts\Activate

✅ 확인: 터미널 프롬프트 앞에 (vsc_env)가 나타나야 합니다.

2. 필수 라이브러리 설치 (필수)
가상 환경이 활성화된 상태에서, 실행에 필요한 모든 라이브러리를 설치합니다. device_map="auto" 설정을 위해 accelerate 라이브러리가 반드시 포함되어야 합니다.
pip install pandas numpy torch faiss-cpu rank-bm25 sentence-transformers transformers accelerate

3. 데이터 준비
스크립트가 로드할 수 있도록 크롤링 결과 파일인 **documents.json**을 프로젝트 루트 디렉터리(rag 폴더)에 위치시켜야 합니다.

🚀 프로젝트 실행
모든 라이브러리 설치가 완료되었다면, 메인 스크립트 파일을 실행합니다.
python rag_system.py

