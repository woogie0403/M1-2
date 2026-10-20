# 🎬 K-BoxOffice AI Assistant (나만의 박스오피스 AI 비서)

> **2024~2025 대한민국 영화 박스오피스 시계열 데이터 기반 지능형 의사결정 비서**  
> 사용자의 731일치 실제 극장가 관객 데이터를 실시간으로 요약·분석하여 시스템 프롬프트에 주입(Context Injection)하고, 맞춤형 브리핑을 제공하는 Full-Stack AI Agent 웹 서비스입니다.

---

## 1. 📌 서비스 소개 (무엇을 해결하는가?)

### 배경 및 문제 정의
- 기존의 ChatGPT나 범용 LLM은 사용자의 고유 데이터나 최신 로컬 데이터를 알지 못합니다. 예를 들어 *"2024년 최저 관객수 영화는?"*, *"우리 극장가 트렌드가 어때?"*라고 질문하면 일반적이거나 부정확한 답변(Hallucination)만 돌아옵니다.
- KOBIS(영화관입장권통합전산망)의 일별 박스오피스 표는 방대하여, 일반 사용자가 최고/최저 흥행 시기, 누적 통계, 전반기 대비 성장률 추세를 한눈에 파악하기 어렵습니다.

### 해결 솔루션: K-BoxOffice AI
- **시계열 데이터 통계 요약 엔진**: 731일간의 일별 관객 수(`value`)와 1위 영화(`memo`) 데이터를 실시간으로 집계(누적 2.14억 명, 일평균 29.3만 명, 최고/최저일, 트렌드 판정)합니다.
- **컨텍스트 주입 (Context Injection)**: 요약 통계를 시스템 프롬프트에 실시간 바인딩하여, AI가 실제 내 데이터를 근거로 정확한 수치와 영화명을 인용하며 답변합니다.
- **영속적 대화 및 데이터 관리 (CRUD)**: Firestore NoSQL DB를 기반으로 대화 이력을 자동 저장·불러오기하며, 사용자가 새로운 일별 데이터를 추가/수정/삭제할 수 있습니다.
- **바닐라 웹 대시보드**: React 등의 무거운 프레임워크 없이 순수 바닐라 HTML/CSS/JS로 제작되어 초고속 로딩을 지원하며 다크모드, CSV 내보내기, 시각화 차트를 제공합니다.

---

## 2. 🛠 기술 스택 (Tech Stack)

| 계층 | 기술 스택 | 설명 |
| :--- | :--- | :--- |
| **Backend** | **Python 3.10+**, **FastAPI**, **Uvicorn** | 모던 비동기 고성능 REST API 서버 구축 |
| **Data & Validation** | **Pydantic v2** | 엄격한 입출력 DTO 데이터 유효성 검증 |
| **Database** | **Firebase Admin SDK (Firestore)** | NoSQL 클라우드 DB 연동 (`data`, `conversations`) 및 Fallback 로컬 DB |
| **AI / LLM** | **OpenAI SDK**, **Google Gemini API** (`gemini-3.5-flash-lite`) | OpenAI 호환 엔드포인트를 통한 컨텍스트 주입 대화 |
| **Frontend** | **Vanilla HTML5**, **Vanilla CSS3**, **Vanilla JavaScript (ES6+)** | 프레임워크 없는 순수 정적 웹 대시보드 |
| **Visualization** | **Chart.js (CDN)** | 시계열 관객 추이 꺾은선 차트 시각화 (보너스 과제) |
| **Deployment** | **Render** (백엔드), **Vercel** (프론트엔드) | 클라우드 자동 배포 파이프라인 |

---

## 3. 🌐 배포 URL (Deployment Links)

- **프론트엔드 웹 서비스 URL (Vercel)**: `https://<your-project>.vercel.app` (Vercel 배포 후 기재)
- **백엔드 API 서버 URL (Render)**: https://m1-2-7jmb.onrender.com
- **대화형 Swagger API 문서**: https://m1-2-7jmb.onrender.com/docs

> ⚠️ **Render 무료 티어 안내**:  
> 무료 플랜 특성상 15분간 요청이 없을 시 인스턴스가 슬립 모드(Cold Start)에 들어갑니다. 첫 접속 시 서버가 깨어나는 데 약 30~50초 정도 소요될 수 있으며, 프론트엔드 상단 상태 배지에 로딩 안내가 표시됩니다.

---

## 4. 💻 로컬 실행 방법 (Local Getting Started)

### 1) 저장소 클론 및 가상환경 설정
```bash
git clone <repository-url>
cd M1-2

# 가상환경 생성 및 활성화 (Windows PowerShell 기준)
python -m venv venv
.\venv\Scripts\Activate.ps1

# 필수 패키지 설치
pip install -r requirements.txt
```

### 2) 환경 변수 설정
`.env.example` 파일을 복사하여 `.env` 파일을 생성하고 키를 입력합니다:
```bash
cp .env.example .env
```

### 3) 백엔드 서버 실행
```bash
$env:PYTHONPATH="backend"
.\venv\Scripts\uvicorn app.main:app --app-dir backend --reload --port 8000
```

### 4) 프론트엔드 접속
- 브라우저를 열고 **`http://localhost:8000/app/`** 로 접속합니다.
- Swagger API 문서는 **`http://localhost:8000/docs`** 에서 확인할 수 있습니다.

---

## 5. 🔑 필수 환경 변수 목록 (Minimum Environment Variables)

| 환경 변수명 | 필수 여부 | 설명 | 예시 값 |
| :--- | :---: | :--- | :--- |
| `GEMINI_API_KEY` | 필수 | Google AI Studio 무료 API Key | `AIzaSy...` 또는 `AQ.Ab8RN...` |
| `GEMINI_BASE_URL` | 필수 | Gemini OpenAI 호환 엔드포인트 URL | `https://generativelanguage.googleapis.com/v1beta/openai/` |
| `AI_MODEL` | 필수 | AI 모델 지정 | `gemini-3.5-flash-lite` |
| `ALLOWED_ORIGINS` | 필수 | CORS 허용 도메인 목록 | `http://localhost:3000,http://127.0.0.1:5500,http://localhost:8000` |
| `FIREBASE_SERVICE_ACCOUNT_KEY` | 선택 | 로컬 Firebase 서비스 계정 JSON 경로 | `./serviceAccountKey.json` |
| `FIREBASE_SERVICE_ACCOUNT_JSON`| 선택 | 클라우드 배포용 Firebase JSON 문자열 | `{"type": "service_account", ...}` |

---

## 6. 📸 과제 제출 필수 스크린샷 3종 증빙

### 1) 데이터 요약이 보이는 AI 채팅 화면
- 상단의 4개 요약 카드(집계 기간, 총 누적 관객 2.14억 명, 일평균 29.3만 명, 트렌드)와 함께, AI 비서가 내 박스오피스 데이터를 인용하여 맞춤형 답변을 제공하는 화면입니다.
- *(캡처 이미지 위치: `docs/screenshots/01_chat_summary.png`)*

### 2) 데이터 관리 화면 (CRUD 동작)
- 731개의 일별 박스오피스 데이터 테이블 목록이 표시되고, 새 데이터를 등록하거나 기존 데이터를 수정/삭제하는 동작 화면입니다.
- *(캡처 이미지 위치: `docs/screenshots/02_data_crud.png`)*

### 3) 대화 기록 화면 (대화 불러오기 동작)
- 좌측 사이드바의 "💬 대화 기록" 탭에 이전 대화 목록이 누적 표시되고, 특정 대화를 클릭하여 과거 주고받은 메시지들이 채팅창에 완벽히 복원되는 화면입니다.
- *(캡처 이미지 위치: `docs/screenshots/03_conversation_history.png`)*

---

## 7. 🎁 보너스 과제 구현 내역

1. **시계열 시각화 차트 (Chart.js)**:
   - 좌측 "📉 관객 추이 차트" 탭에서 일별 관객수 변화 추세를 부드러운 꺾은선 곡선 그래프로 실시간 렌더링
2. **원클릭 CSV 내보내기**:
   - 상단 "📥 CSV 내보내기" 버튼을 누르면 현재 데이터베이스의 모든 데이터를 UTF-8 인코딩의 CSV 파일로 즉시 다운로드
3. **다크 모드 (Dark Mode)**:
   - 상단 테마 토글 버튼(🌙/☀️)을 통해 세련된 다크 테마를 지원하며 `localStorage`에 상태 영구 저장
