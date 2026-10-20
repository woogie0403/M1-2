import sys
import os

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from dotenv import load_dotenv

load_dotenv()

print("=" * 50)
print(f"[Python Version] {sys.version.split()[0]}")

packages = ["fastapi", "uvicorn", "firebase_admin", "openai", "dotenv", "pydantic"]
for pkg in packages:
    try:
        mod = __import__(pkg)
        ver = getattr(mod, "__version__", "installed")
        print(f"[OK] {pkg}: {ver}")
    except ImportError as e:
        print(f"[FAIL] {pkg}: Import Error - {e}")

print("-" * 50)
openai_key = os.getenv("OPENAI_API_KEY")
firebase_key = os.getenv("FIREBASE_SERVICE_ACCOUNT_KEY") or os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")

if openai_key and not openai_key.startswith("your_"):
    print(f"[INFO] OPENAI_API_KEY: 설정됨 (앞 8자리: {openai_key[:8]}...)")
else:
    print("[WARN] OPENAI_API_KEY: 아직 설정되지 않음 (.env 파일에 입력 필요)")

if firebase_key:
    if os.path.exists(firebase_key):
        print(f"[INFO] FIREBASE_SERVICE_ACCOUNT_KEY: 파일 확인됨 ({firebase_key})")
    elif firebase_key.strip().startswith("{"):
        print("[INFO] FIREBASE_SERVICE_ACCOUNT_JSON: JSON 문자열 확인됨")
    else:
        print(f"[WARN] FIREBASE_SERVICE_ACCOUNT_KEY: 지정된 경로에 파일 없음 ({firebase_key})")
else:
    print("[WARN] FIREBASE_SERVICE_ACCOUNT_KEY: 아직 설정되지 않음 (.env 파일에 입력 필요)")

print("=" * 50)
