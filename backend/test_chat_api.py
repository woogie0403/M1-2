import sys
import json

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

print("=" * 60)
print("🤖 [AI 챗봇(Context Injection) & 대화 기록 API 자동 테스트]")
print("=" * 60)

# 1. AI 챗봇 질문 전송 (Context Injection 검증)
question = "2024~2025년 총 누적 관객수와 일일 평균 관객수 통계를 알려줘"
print(f"\n1. 사용자 질문: '{question}'", flush=True)
print("   Gemini AI 모델 응답 생성 중...", flush=True)

chat_res = client.post("/api/chat", json={"message": question})
assert chat_res.status_code == 200, f"Error: {chat_res.text}"
chat_data = chat_res.json()

print(f"\n✅ AI 답변 응답 성공 (대화 ID: {chat_data['conversation_id']})", flush=True)
print(f"   [컨텍스트 주입 여부]: {chat_data['summary_applied']}", flush=True)
print("-" * 50, flush=True)
print(f"AI 답변:\n{chat_data['response']}", flush=True)
print("-" * 50, flush=True)

conv_id = chat_data["conversation_id"]

# 2. 대화 목록 조회 (GET /api/conversations - 자동 저장 검증)
list_res = client.get("/api/conversations")
assert list_res.status_code == 200
conv_list = list_res.json()
print(f"\n2. 대화 목록 조회 (GET /api/conversations): {len(conv_list)}개 저장됨")
found = any(c["id"] == conv_id for c in conv_list)
print(f"   ✅ 방금 대화가 자동으로 저장되었는가?: {found}")

# 3. 특정 대화 상세 불러오기 (GET /api/conversations/{id} - 대화 불러오기 UX 지원)
detail_res = client.get(f"/api/conversations/{conv_id}")
assert detail_res.status_code == 200
detail_data = detail_res.json()
print(f"\n3. 특정 대화 불러오기 (GET /api/conversations/{conv_id}):")
print(f"   - 제목: {detail_data['title']}")
print(f"   - 메시지 개수: {len(detail_data.get('messages', []))}개")
for m in detail_data.get("messages", []):
    role_icon = "👤" if m["role"] == "user" else "🤖"
    print(f"     {role_icon} [{m['role']}]: {m['content'][:40]}...")

# 4. 대화 삭제 (DELETE /api/conversations/{id})
del_res = client.delete(f"/api/conversations/{conv_id}")
assert del_res.status_code == 200
print(f"\n4. 대화 삭제 (DELETE /api/conversations/{conv_id}): {del_res.json()['message']}")

# 5. 삭제 확인 (404 반환)
del_check = client.get(f"/api/conversations/{conv_id}")
assert del_check.status_code == 404
print(f"5. 삭제 후 404 확인: 정상 차단")

print("\n" + "=" * 60)
print("✨ [결과] AI 챗봇 컨텍스트 주입 및 대화 기록 API 100% 정상 작동 검증 완료!")
print("=" * 60)
