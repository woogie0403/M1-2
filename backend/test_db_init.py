import sys
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from app.schemas.data import DataCreate, DataItem, DataSummaryResponse
from app.schemas.chat import ChatRequest, ChatResponse, ConversationItem
from app.database import init_firebase, is_mock_db

print("=" * 50)
print("[Pydantic DTO 스키마 테스트]")
sample_data = DataCreate(date="2024-01-01", value=730970, memo="1위: 노량: 죽음의 바다")
print(f"✅ DataCreate 스키마 검증 통과: {sample_data.model_dump()}")

sample_chat = ChatRequest(message="2024년 최고 흥행작이 뭐야?")
print(f"✅ ChatRequest 스키마 검증 통과: {sample_chat.model_dump()}")

print("\n[Database 초기화 테스트]")
init_firebase()
print(f"✅ Mock DB 여부: {is_mock_db()}")
print("=" * 50)
