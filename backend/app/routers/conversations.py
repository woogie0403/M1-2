from fastapi import APIRouter, HTTPException, status
from typing import List
from app.schemas.chat import ConversationItem, ConversationCreate
from app.services.conversation_service import ConversationService

router = APIRouter()

@router.get(
    "",
    response_model=List[ConversationItem],
    summary="대화 목록 조회",
    description="저장된 이전 대화 목록을 최신 수정일순으로 조회합니다."
)
def get_conversations():
    return ConversationService.get_all_conversations()

@router.get(
    "/{id}",
    response_model=ConversationItem,
    summary="특정 대화 상세 조회 (전체 메시지)",
    description="특정 대화의 전체 메시지 이력을 불러옵니다."
)
def get_conversation(id: str):
    return ConversationService.get_conversation_by_id(id)

@router.post(
    "",
    response_model=ConversationItem,
    status_code=status.HTTP_201_CREATED,
    summary="대화 저장",
    description="새로운 대화 세션 또는 메시지 목록을 저장합니다."
)
def create_conversation(payload: ConversationCreate):
    return ConversationService.create_conversation(payload)

@router.delete(
    "/{id}",
    summary="대화 삭제",
    description="ID에 해당하는 대화 기록을 영구 삭제합니다."
)
def delete_conversation(id: str):
    return ConversationService.delete_conversation(id)
