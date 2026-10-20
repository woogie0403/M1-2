import os
from typing import List, Optional
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROJECT_NAME: str = "K-BoxOffice AI Assistant"
    VERSION: str = "1.0.0"

    # Gemini API 설정
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_BASE_URL: str = os.getenv("GEMINI_BASE_URL", "https://generativelanguage.googleapis.com/v1beta/openai/")
    AI_MODEL: str = os.getenv("AI_MODEL", "gemini-3.8-flash")

    # (대체용) OpenAI 설정
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

    # Firebase 설정
    FIREBASE_SERVICE_ACCOUNT_KEY: str = os.getenv("FIREBASE_SERVICE_ACCOUNT_KEY", "./serviceAccountKey.json")
    FIREBASE_SERVICE_ACCOUNT_JSON: str = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON", "")

    # CORS 허용 도메인 목록
    ALLOWED_ORIGINS_RAW: str = os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:3000,http://127.0.0.1:5500,http://localhost:8000,http://127.0.0.1:8000"
    )

    @property
    def ALLOWED_ORIGINS(self) -> List[str]:
        origins = [x.strip() for x in self.ALLOWED_ORIGINS_RAW.split(",") if x.strip()]
        if "*" not in origins and "http://localhost:3000" not in origins:
            origins.append("http://localhost:3000")
        return origins

    @property
    def ACTIVE_AI_KEY(self) -> str:
        """우선순위: GEMINI_API_KEY > OPENAI_API_KEY"""
        return self.GEMINI_API_KEY if self.GEMINI_API_KEY else self.OPENAI_API_KEY

    @property
    def ACTIVE_BASE_URL(self) -> Optional[str]:
        """Gemini 사용 시 호환 URL 반환, OpenAI 단독 시 None"""
        if self.GEMINI_API_KEY:
            return self.GEMINI_BASE_URL
        return None

    @property
    def ACTIVE_MODEL(self) -> str:
        if self.GEMINI_API_KEY:
            return self.AI_MODEL
        return "gpt-4o-mini"

settings = Settings()
