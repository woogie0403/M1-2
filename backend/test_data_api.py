import sys
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

print("=" * 60)
print("🚀 [FastAPI 데이터 CRUD & Summary API 5종 자동 테스트 시작]")
print("=" * 60)

# 1. 헬스체크
res = client.get("/")
assert res.status_code == 200
print(f"1. 헬스체크 GET / : {res.json()}")

# 2. 데이터 요약 조회 (GET /api/data/summary)
res = client.get("/api/data/summary")
assert res.status_code == 200
summary_data = res.json()
print("\n2. 데이터 요약 GET /api/data/summary :")
print(f"   - 기간: {summary_data['period']}")
print(f"   - 건수: {summary_data['count']}건")
print(f"   - 주요 지표: {summary_data['metrics']}")
print(f"   - 트렌드: {summary_data['trend']}")

# 3. 데이터 목록 조회 (GET /api/data)
res = client.get("/api/data?limit=3")
assert res.status_code == 200
items = res.json()
print(f"\n3. 데이터 목록 GET /api/data?limit=3 : {len(items)}개 조회 성공")
for it in items:
    print(f"   - [{it['date']}] 관객수: {it['value']:,}명 / {it['memo']} (ID: {it['id']})")

# 4. 새 데이터 추가 (POST /api/data)
new_item_payload = {
    "date": "2026-01-01",
    "value": 950000,
    "memo": "1위: 신작 블록버스터 (점유율 45.0%)"
}
res = client.post("/api/data", json=new_item_payload)
assert res.status_code == 201
created = res.json()
created_id = created["id"]
print(f"\n4. 데이터 생성 POST /api/data : 성공 (ID: {created_id})")
print(f"   - 생성 내용: {created}")

# 5. 데이터 수정 (PUT /api/data/{id})
update_payload = {
    "value": 1100000,
    "memo": "1위: 신작 블록버스터 (수정: 관객 110만 돌파)"
}
res = client.put(f"/api/data/{created_id}", json=update_payload)
assert res.status_code == 200
updated = res.json()
print(f"\n5. 데이터 수정 PUT /api/data/{created_id} : 성공")
print(f"   - 수정 내용: {updated}")

# 6. 데이터 삭제 (DELETE /api/data/{id})
res = client.delete(f"/api/data/{created_id}")
assert res.status_code == 200
print(f"\n6. 데이터 삭제 DELETE /api/data/{created_id} : 성공 ({res.json()})")

# 7. 삭제 확인 (존재하지 않는 ID 404 확인)
res = client.put(f"/api/data/{created_id}", json={"value": 100})
assert res.status_code == 404
print(f"7. 404 예외 처리 검증 : 정상 차단 확인 ({res.status_code})")

print("\n" + "=" * 60)
print("✨ [결과] 5개 엔드포인트(CRUD + Summary) 모두 100% 정상 작동 완료!")
print("=" * 60)
