from fastapi import APIRouter
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.ai_service import AIService

router = APIRouter()

@router.post(
    "",
    response_model=ChatResponse,
    summary="AI 챗봇 대화 (컨텍스트 주입)",
    description="시계열 데이터 요약을 시스템 프롬프트에 주입하고 AI와 대화하며, 대화 내용은 conversations에 자동 저장됩니다."
)
def chat_with_ai(payload: ChatRequest):
    result = AIService.chat(
        user_message=payload.message,
        conv_id=payload.conversation_id
    )
    return ChatResponse(**result)
