import os
import json
import logging
from typing import Optional, Dict, Any, List
import firebase_admin
from firebase_admin import credentials, firestore
from app.config import settings

logger = logging.getLogger("uvicorn.error")

_db = None
_is_mock = False
_mock_storage: Dict[str, Dict[str, Any]] = {
    "data": {},
    "conversations": {}
}

def init_firebase():
    """
    Firebase Admin SDK를 안전하게 초기화합니다.
    1순위: 파일 경로 (FIREBASE_SERVICE_ACCOUNT_KEY)
    2순위: JSON 문자열 (FIREBASE_SERVICE_ACCOUNT_JSON)
    없을 경우: 로컬 인메모리 Mock 저장소 모드로 자동 전환하여 개발 지속 가능 보장
    """
    global _db, _is_mock

    if _db is not None:
        return _db

    cred = None
    key_path = settings.FIREBASE_SERVICE_ACCOUNT_KEY

    # 1. 파일 경로 확인
    if key_path and os.path.exists(key_path):
        try:
            cred = credentials.Certificate(key_path)
            logger.info(f"[Firebase] 서비스 계정 파일 로드 성공: {key_path}")
        except Exception as e:
            logger.error(f"[Firebase] 키 파일 로드 실패: {e}")

    # 2. JSON 문자열 확인 (클라우드 배포용)
    if not cred and settings.FIREBASE_SERVICE_ACCOUNT_JSON:
        try:
            cert_dict = json.loads(settings.FIREBASE_SERVICE_ACCOUNT_JSON)
            cred = credentials.Certificate(cert_dict)
            logger.info("[Firebase] 서비스 계정 JSON 문자열 로드 성공")
        except Exception as e:
            logger.error(f"[Firebase] JSON 문자열 파싱 실패: {e}")

    # 3. Firebase 앱 초기화 시도
    if cred:
        try:
            if not firebase_admin._apps:
                firebase_admin.initialize_app(cred)
            _db = firestore.client()
            _is_mock = False
            logger.info("[Firebase] Firestore 클라이언트 연결 성공")
            return _db
        except Exception as e:
            logger.error(f"[Firebase] Firestore 초기화 실패: {e}")

    # 4. 키 미설정 시 Fallback 모드 (Mock 저장소)
    logger.warning("=" * 60)
    logger.warning("[안내] Firebase 서비스 계정 키가 감지되지 않아 로컬 인메모리 DB로 동작합니다.")
    logger.warning("Firebase 콘솔에서 다운로드받은 키를 serviceAccountKey.json 으로 저장하면")
    logger.warning("자동으로 실제 Firestore DB로 연동됩니다.")
    logger.warning("=" * 60)
    _is_mock = True
    return None

def get_db():
    global _db
    if _db is None and not _is_mock:
        init_firebase()
    return _db

def is_mock_db() -> bool:
    return _is_mock

def get_mock_storage() -> Dict[str, Dict[str, Any]]:
    return _mock_storage
