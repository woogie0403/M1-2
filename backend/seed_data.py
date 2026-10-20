import json
import random
from datetime import datetime, timedelta
import sys

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from app.services.summary_service import calculate_summary

def generate_sample_dataset(days: int = 120) -> list:
    """
    최근 120일간의 일별 비즈니스 매출/실적 시계열 데이터를 현실적으로 생성합니다.
    (기본 상승 트렌드 + 요일별 변동성 + 이벤트성 메모 반영)
    """
    base_date = datetime.now() - timedelta(days=days)
    records = []
    base_value = 250000  # 기본 일매출 25만원 선

    memos = [
        "정기 프로모션 진행",
        "SNS 바이럴 광고 집행",
        "주말 주문량 급증",
        "신제품 런칭 이벤트",
        "재고 일시 품절로 인한 보합",
        "인플루언서 협업 리뷰 업로드",
        "평일 기본 주문 유지",
        "시즌 세일 오픈",
        "충성 고객 감사 쿠폰 발급",
        "시스템 점검 및 배송 마감"
    ]

    random.seed(42)  # 재현성을 위한 시드 고정

    for i in range(days):
        current_date = base_date + timedelta(days=i)
        date_str = current_date.strftime("%Y-%m-%d")

        # 전반부에서 후반부로 갈수록 완만하게 성장하는 현실적 추세 모델링
        growth_trend = i * 2000
        # 주말(토/일) 효과: 1.3배
        is_weekend = current_date.weekday() >= 5
        weekend_boost = 1.35 if is_weekend else 1.0

        noise = random.randint(-40000, 60000)
        daily_val = int((base_value + growth_trend + noise) * weekend_boost)
        daily_val = max(100000, daily_val)  # 최소 10만원 보장

        memo = random.choice(memos) if (i % 3 == 0 or daily_val > 450000) else "일반 정기 배송"

        records.append({
            "date": date_str,
            "value": daily_val,
            "memo": memo
        })

    return records

if __name__ == "__main__":
    data = generate_sample_dataset(120)
    
    # JSON 파일로 저장
    with open("backend/seed_data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"[성공] 120개의 시계열 샘플 데이터 생성 완료 -> backend/seed_data.json")

    # 요약 통계 엔진 테스트
    summary = calculate_summary(data)
    print("\n" + "=" * 50)
    print("[데이터 요약 엔진(calculate_summary) 테스트 결과]")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print("=" * 50)
