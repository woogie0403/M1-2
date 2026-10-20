import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from fastapi import HTTPException
from app.database import get_db, is_mock_db, get_mock_storage
from app.schemas.chat import ChatMessage, ConversationCreate, ConversationItem

CONV_COLLECTION = "conversations"

class ConversationService:
    @staticmethod
    def get_all_conversations() -> List[Dict[str, Any]]:
        """대화 목록을 최신 수정일순으로 조회합니다."""
        db = get_db()
        items = []

        if db is not None:
            docs = db.collection(CONV_COLLECTION).order_by("updated_at", direction="DESCENDING").stream()
            for doc in docs:
                d = doc.to_dict()
                d["id"] = doc.id
                items.append(d)
        else:
            storage = get_mock_storage()
            items = list(storage[CONV_COLLECTION].values())
            items.sort(key=lambda x: str(x.get("updated_at", "")), reverse=True)

        return items

    @staticmethod
    def get_conversation_by_id(conv_id: str) -> Dict[str, Any]:
        """특정 대화의 전체 메시지 및 상세 정보를 조회합니다."""
        db = get_db()

        if db is not None:
            doc_ref = db.collection(CONV_COLLECTION).document(conv_id)
            doc = doc_ref.get()
            if not doc.exists:
                raise HTTPException(status_code=404, detail=f"대화 ID '{conv_id}'를 찾을 수 없습니다.")
            d = doc.to_dict()
            d["id"] = doc.id
            return d
        else:
            storage = get_mock_storage()
            if conv_id not in storage[CONV_COLLECTION]:
                raise HTTPException(status_code=404, detail=f"대화 ID '{conv_id}'를 찾을 수 없습니다.")
            return storage[CONV_COLLECTION][conv_id]

    @staticmethod
    def create_conversation(payload: ConversationCreate) -> Dict[str, Any]:
        """새 대화 세션을 생성합니다."""
        db = get_db()
        now_str = datetime.now().isoformat()
        conv_title = payload.title or "새 대화"

        messages_data = [m.model_dump() for m in payload.messages]
        conv_data = {
            "title": conv_title,
            "created_at": now_str,
            "updated_at": now_str,
            "messages": messages_data
        }

        if db is not None:
            doc_ref = db.collection(CONV_COLLECTION).document()
            doc_ref.set(conv_data)
            conv_data["id"] = doc_ref.id
        else:
            doc_id = str(uuid.uuid4())[:8]
            conv_data["id"] = doc_id
            storage = get_mock_storage()
            storage[CONV_COLLECTION][doc_id] = conv_data

        return conv_data

    @staticmethod
    def save_chat_turn(conv_id: Optional[str], user_content: str, assistant_content: str) -> Dict[str, Any]:
        """
        AI 대화 1턴(사용자 질문 + AI 답변)을 대화 기록에 추가하거나 새 대화를 생성하여 저장합니다.
        """
        now_str = datetime.now().isoformat()
        db = get_db()

        user_msg = {"role": "user", "content": user_content, "timestamp": now_str}
        assistant_msg = {"role": "assistant", "content": assistant_content, "timestamp": now_str}

        # 기존 대화 세션이 지정된 경우
        if conv_id:
            try:
                conv = ConversationService.get_conversation_by_id(conv_id)
            except HTTPException:
                conv = None
        else:
            conv = None

        if conv:
            # 기존 대화에 메시지 추가
            messages = conv.get("messages", [])
            messages.append(user_msg)
            messages.append(assistant_msg)

            if db is not None:
                db.collection(CONV_COLLECTION).document(conv_id).update({
                    "messages": messages,
                    "updated_at": now_str
                })
            else:
                storage = get_mock_storage()
                storage[CONV_COLLECTION][conv_id]["messages"] = messages
                storage[CONV_COLLECTION][conv_id]["updated_at"] = now_str
            return {"id": conv_id, "messages": messages}
        else:
            # 새로운 대화 생성 (첫 질문 앞 20자로 제목 자동 생성)
            title = user_content[:20] + ("..." if len(user_content) > 20 else "")
            new_payload = ConversationCreate(
                title=title,
                messages=[ChatMessage(**user_msg), ChatMessage(**assistant_msg)]
            )
            return ConversationService.create_conversation(new_payload)

    @staticmethod
    def delete_conversation(conv_id: str) -> Dict[str, str]:
        """대화 기록을 삭제합니다."""
        db = get_db()

        if db is not None:
            doc_ref = db.collection(CONV_COLLECTION).document(conv_id)
            doc = doc_ref.get()
            if not doc.exists:
                raise HTTPException(status_code=404, detail=f"대화 ID '{conv_id}'를 찾을 수 없습니다.")
            doc_ref.delete()
        else:
            storage = get_mock_storage()
            if conv_id not in storage[CONV_COLLECTION]:
                raise HTTPException(status_code=404, detail=f"대화 ID '{conv_id}'를 찾을 수 없습니다.")
            del storage[CONV_COLLECTION][conv_id]

        return {"message": f"대화 '{conv_id}'가 성공적으로 삭제되었습니다."}
