import json
import os
import sys

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from app.database import init_firebase, get_db

def seed_data_to_firestore():
    """
    backend/seed_data.json의 시계열 데이터를 실제 Firebase Firestore의
    'data' 컬렉션에 일괄 업로드(Batch Write)합니다.
    """
    db = init_firebase()
    if db is None:
        print("[안내] Firebase 서비스 계정 키가 설정되지 않아 Firestore 일괄 업로드를 건너뜁니다.")
        print("      serviceAccountKey.json 파일을 등록한 뒤 이 스크립트를 실행하면 클라우드로 즉시 업로드됩니다.")
        return False

    seed_path = os.path.join(os.path.dirname(__file__), "seed_data.json")
    if not os.path.exists(seed_path):
        print(f"[오류] seed_data.json을 찾을 수 없습니다: {seed_path}")
        return False

    with open(seed_path, "r", encoding="utf-8") as f:
        records = json.load(f)

    total_records = len(records)
    print(f"🔥 Firebase Firestore 'data' 컬렉션에 {total_records}개 데이터 시딩을 시작합니다...")

    # Firestore는 한 번의 batch 작업당 최대 500개 제한이 있으므로 400개씩 분할 커밋
    batch_size = 400
    collection_ref = db.collection("data")

    for i in range(0, total_records, batch_size):
        chunk = records[i:i + batch_size]
        batch = db.batch()
        for item in chunk:
            doc_ref = collection_ref.document()
            batch.set(doc_ref, {
                "date": item["date"],
                "value": float(item["value"]),
                "memo": item.get("memo", "")
            })
        batch.commit()
        print(f"   - {min(i + batch_size, total_records)} / {total_records} 개 업로드 완료...")

    print("🎉 [성공] Firestore 데이터 시딩이 모두 완료되었습니다!")
    return True

if __name__ == "__main__":
    seed_data_to_firestore()
