from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import init_firebase
from app.routers import data as data_router

# FastAPI 인스턴스 생성
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="2024-2025 대한민국 영화 박스오피스 시계열 데이터 기반 AI 비서 API",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 서버 시작 이벤트
@app.on_event("startup")
def startup_event():
    init_firebase()

# 헬스체크 엔드포인트
@app.get("/", tags=["Health"])
def health_check():
    return {
        "status": "online",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs": "/docs"
    }

# 라우터 등록
app.include_router(data_router.router, prefix="/api/data", tags=["Data CRUD & Summary"])
