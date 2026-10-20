from datetime import datetime
from typing import List, Dict, Any, Optional

def calculate_summary(items: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    시계열 데이터 목록(date, value, memo)을 분석하여
    기간, 데이터 개수, 핵심 통계 지표(합계, 평균, 최대, 최소), 추세(Trend)를 계산합니다.
    """
    if not items:
        return {
            "period": "데이터 없음",
            "count": 0,
            "metrics": {
                "total": 0,
                "average": 0,
                "max": 0,
                "min": 0
            },
            "trend": "데이터 없음"
        }

    # 날짜 오름차순 정렬
    sorted_items = sorted(items, key=lambda x: str(x.get("date", "")))

    dates = [x.get("date") for x in sorted_items if x.get("date")]
    values = [float(x.get("value", 0)) for x in sorted_items]

    count = len(values)
    total_val = sum(values)
    avg_val = total_val / count if count > 0 else 0
    max_val = max(values) if values else 0
    min_val = min(values) if values else 0

    period_str = f"{dates[0]} ~ {dates[-1]}" if dates else "기간 미상"

    # 추세(Trend) 판정: 최근 30개(또는 후반부)와 이전 데이터 비교
    if count < 10:
        trend_str = "데이터 표본 부족 (10개 미만)"
    else:
        half = count // 2
        first_half = values[:half]
        second_half = values[half:]

        avg_first = sum(first_half) / len(first_half) if first_half else 0
        avg_second = sum(second_half) / len(second_half) if second_half else 0

        if avg_first > 0:
            diff_pct = ((avg_second - avg_first) / avg_first) * 100
            if diff_pct > 3.0:
                trend_str = f"상승 (전반 대비 최근 +{diff_pct:.1f}%)"
            elif diff_pct < -3.0:
                trend_str = f"하강 (전반 대비 최근 {diff_pct:.1f}%)"
            else:
                trend_str = f"유지 (변동폭 ±3% 이내, {diff_pct:+.1f}%)"
        else:
            trend_str = "판정 불가"

    return {
        "period": period_str,
        "count": count,
        "metrics": {
            "total": round(total_val, 2),
            "average": round(avg_val, 2),
            "max": round(max_val, 2),
            "min": round(min_val, 2)
        },
        "trend": trend_str
    }
