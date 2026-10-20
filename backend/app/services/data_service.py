import uuid
import json
import os
from typing import List, Dict, Any, Optional
from fastapi import HTTPException
from app.database import get_db, is_mock_db, get_mock_storage
from app.schemas.data import DataCreate, DataUpdate, DataItem, DataSummaryResponse
from app.services.summary_service import calculate_summary

DATA_COLLECTION = "data"

def _ensure_mock_data_loaded():
    """Mock 모드일 때 seed_data.json에서 데이터를 메모리로 적재합니다."""
    storage = get_mock_storage()
    if not storage[DATA_COLLECTION]:
        # data_service.py 위치 기준: backend/app/services -> backend/seed_data.json
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        seed_path = os.path.join(base_dir, "seed_data.json")
        if not os.path.exists(seed_path):
            seed_path = os.path.join(os.getcwd(), "backend", "seed_data.json")
        if not os.path.exists(seed_path):
            seed_path = os.path.join(os.getcwd(), "seed_data.json")

        if os.path.exists(seed_path):
            try:
                with open(seed_path, "r", encoding="utf-8") as f:
                    seeds = json.load(f)
                    for item in seeds:
                        doc_id = item.get("id") or str(uuid.uuid4())[:8]
                        storage[DATA_COLLECTION][doc_id] = {
                            "id": doc_id,
                            "date": str(item.get("date", "")),
                            "value": float(item.get("value", 0)),
                            "memo": str(item.get("memo", ""))
                        }
            except Exception as e:
                print(f"Mock 데이터 로드 실패: {e}")

class DataService:
    @staticmethod
    def get_all_data(limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """모든 시계열 데이터를 조회하여 날짜 오름차순으로 반환합니다."""
        db = get_db()
        items = []

        if db is not None:
            # Firestore 조회
            query = db.collection(DATA_COLLECTION).order_by("date")
            if limit:
                query = query.limit(limit)
            docs = query.stream()
            for doc in docs:
                d = doc.to_dict()
                d["id"] = doc.id
                items.append(d)
        else:
            # Mock DB 조회
            _ensure_mock_data_loaded()
            storage = get_mock_storage()
            items = list(storage[DATA_COLLECTION].values())
            items.sort(key=lambda x: str(x.get("date", "")))
            if limit:
                items = items[:limit]

        return items

    @staticmethod
    def add_data(payload: DataCreate) -> Dict[str, Any]:
        """새 시계열 데이터를 추가합니다."""
        db = get_db()
        data_dict = {
            "date": payload.date,
            "value": float(payload.value),
            "memo": payload.memo or ""
        }

        if db is not None:
            doc_ref = db.collection(DATA_COLLECTION).document()
            doc_ref.set(data_dict)
            data_dict["id"] = doc_ref.id
        else:
            _ensure_mock_data_loaded()
            doc_id = str(uuid.uuid4())[:8]
            data_dict["id"] = doc_id
            storage = get_mock_storage()
            storage[DATA_COLLECTION][doc_id] = data_dict

        return data_dict

    @staticmethod
    def update_data(doc_id: str, payload: DataUpdate) -> Dict[str, Any]:
        """기존 시계열 데이터를 수정합니다."""
        db = get_db()

        if db is not None:
            doc_ref = db.collection(DATA_COLLECTION).document(doc_id)
            doc = doc_ref.get()
            if not doc.exists:
                raise HTTPException(status_code=404, detail=f"데이터 ID '{doc_id}'를 찾을 수 없습니다.")

            updates = {k: v for k, v in payload.model_dump().items() if v is not None}
            if updates:
                doc_ref.update(updates)

            current = doc_ref.get().to_dict()
            current["id"] = doc_id
            return current
        else:
            _ensure_mock_data_loaded()
            storage = get_mock_storage()
            if doc_id not in storage[DATA_COLLECTION]:
                raise HTTPException(status_code=404, detail=f"데이터 ID '{doc_id}'를 찾을 수 없습니다.")

            current = storage[DATA_COLLECTION][doc_id]
            updates = {k: v for k, v in payload.model_dump().items() if v is not None}
            current.update(updates)
            return current

    @staticmethod
    def delete_data(doc_id: str) -> Dict[str, str]:
        """시계열 데이터를 삭제합니다."""
        db = get_db()

        if db is not None:
            doc_ref = db.collection(DATA_COLLECTION).document(doc_id)
            doc = doc_ref.get()
            if not doc.exists:
                raise HTTPException(status_code=404, detail=f"데이터 ID '{doc_id}'를 찾을 수 없습니다.")
            doc_ref.delete()
        else:
            _ensure_mock_data_loaded()
            storage = get_mock_storage()
            if doc_id not in storage[DATA_COLLECTION]:
                raise HTTPException(status_code=404, detail=f"데이터 ID '{doc_id}'를 찾을 수 없습니다.")
            del storage[DATA_COLLECTION][doc_id]

        return {"message": f"데이터 '{doc_id}'가 성공적으로 삭제되었습니다."}

    @staticmethod
    def get_summary() -> Dict[str, Any]:
        """전체 데이터를 집계하여 요약(기간, 개수, 지표, 추세)을 반환합니다."""
        items = DataService.get_all_data()
        return calculate_summary(items)
