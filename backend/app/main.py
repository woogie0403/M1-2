from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import init_firebase
from app.routers import data as data_router
from app.routers import conversations as conv_router
from app.routers import chat as chat_router

# FastAPI 앱 생성
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="2024-2025 대한민국 영화 박스오피스 시계열 데이터 기반 AI 비서 API",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS 미들웨어 등록
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    init_firebase()

@app.get("/", tags=["Health"])
def health_check():
    return {
        "status": "online",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "ai_model": settings.ACTIVE_MODEL,
        "docs": "/docs"
    }

# 라우터 등록 (과제 명세 엔드포인트 100% 충족)
app.include_router(data_router.router, prefix="/api/data", tags=["Data CRUD & Summary"])
app.include_router(conv_router.router, prefix="/api/conversations", tags=["Conversations"])
app.include_router(chat_router.router, prefix="/api/chat", tags=["AI Chatbot"])
