import os
from typing import List
from dotenv import load_dotenv

# .env 로드
load_dotenv()

class Settings:
    PROJECT_NAME: str = "K-BoxOffice AI Assistant"
    VERSION: str = "1.0.0"

    # OpenAI / Gemini 설정
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_BASE_URL: str = os.getenv("OPENAI_BASE_URL", "https://generativelanguage.googleapis.com/v1beta/openai/")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    AI_MODEL: str = os.getenv("AI_MODEL", "gemini-3.8-flash")

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

settings = Settings()
