from pydantic import BaseModel, Field
from typing import List, Optional

class ChatMessage(BaseModel):
    role: str = Field(..., description="메시지 작성자 (user / assistant / system)")
    content: str = Field(..., description="메시지 내용")
    timestamp: Optional[str] = Field(None, description="기록 일시 (ISO 형식)")

class ChatRequest(BaseModel):
    message: str = Field(..., description="사용자 질문", example="2024년 여름에 박스오피스 실적이 어땠어?")
    conversation_id: Optional[str] = Field(None, description="기존 대화 이어하기 시 대화 ID")

class ChatResponse(BaseModel):
    response: str = Field(..., description="AI 답변")
    conversation_id: str = Field(..., description="대화 세션 ID")
    summary_applied: bool = Field(True, description="데이터 요약(컨텍스트 주입) 반영 여부")

class ConversationCreate(BaseModel):
    title: Optional[str] = Field(None, description="대화 주제명")
    messages: List[ChatMessage] = Field(default_factory=list, description="대화 메시지 목록")

class ConversationItem(BaseModel):
    id: str
    title: str
    created_at: str
    updated_at: str
    messages: Optional[List[ChatMessage]] = None
