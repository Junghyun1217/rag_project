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


죄송합니다. 제가 계속해서 문법 오류가 있는 텍스트를 제공하여 GitHub에 바로 올리시는 데 불편을 드렸습니다.

최종적으로 하나의 완전하고 깨끗한 Markdown 코드 블록으로 전체 README.md 내용을 다시 전달해 드립니다. 이 내용은 모든 문법 오류를 수정하고, 앞서 발생했던 모든 문제 해결 과정을 담고 있습니다.

이것을 그대로 복사하여 README.md 파일에 붙여넣기 하시면 됩니다.

Markdown
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

Bash
pip install pandas numpy torch faiss-cpu rank-bm25 sentence-transformers transformers accelerate
3. 데이터 준비
스크립트가 로드할 수 있도록 크롤링 결과 파일인 **documents.json**을 프로젝트 루트 디렉터리(rag 폴더)에 위치시켜야 합니다.

🚀 프로젝트 실행
모든 라이브러리 설치가 완료되었다면, 메인 스크립트 파일을 실행합니다.

Bash
python rag_system.py
⚠️ 실행 시 주의 사항 및 FAQ
Q1. 실행 후 아무 응답 없이 멈추거나 시간이 매우 오래 걸립니다. (가장 흔한 문제)
A. 이는 정상적인 과정입니다. 스크립트가 다음 두 가지 대용량 모델을 다운로드하고 메모리에 로드하는 데 시간이 필요합니다.

임베딩 모델 다운로드 (paraphrase-multilingual-MiniLM-L12-v2)

LLM 모델 다운로드 및 로드 (Qwen/Qwen3-4B - 약 8GB): 특히 첫 실행 시 이 단계에서 5분에서 10분 이상 소요될 수 있습니다. >> LLM 모델 로딩 시작 메시지가 보이면 인내심을 갖고 기다려 주십시오.

Q2. 스크립트가 실행되자마자 즉시 종료됩니다.
A. 다음 사항을 확인하십시오.

파일 경로: 실행 명령어 python rag_system.py를 입력한 터미널 경로와 .py 파일의 위치가 정확히 일치하는지 확인합니다.

파일 저장: VS Code에서 코드를 수정한 후 반드시 **저장(Ctrl+S)**했는지 확인합니다.

데이터 파일: documents.json 파일이 현재 디렉터리에 존재하는지 확인합니다.

Q3. GPU를 사용하고 싶은데 경고 메시지가 뜹니다.
A. 이 프로젝트는 device_map="auto" 설정을 사용하여 GPU 사용을 시도합니다.

GPU를 사용하려면 pip install torch 대신 CUDA 지원 버전을 설치해야 합니다.

CPU 환경에서 실행해도 작동하지만, LLM 추론 속도가 매우 느려질 수 있습니다.

🛠️ 테스트 질문 수정
rag_system.py 파일의 맨 끝 부분에서 user_question과 query를 수정하여 다양한 질문으로 시스템을 테스트할 수 있습니다.
# rag_system.py 파일 내 수정 부분
user_question = "배터리 오래가는 노트북 추천해줘" # 실제 질문
query = "배터리" # 검색용 키워드/질문
