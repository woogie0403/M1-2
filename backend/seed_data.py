import csv
import json
import os
import sys

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from app.services.summary_service import calculate_summary

def load_and_convert_boxoffice_data(csv_path: str = None) -> list:
    """
    M1-1의 실제 KOBIS 일별 박스오피스 시계열 데이터(2024-2025)를 읽어와
    M1-2 과제 표준 형식 (date, value, memo)으로 변환합니다.
    """
    if csv_path is None:
        local_csv = os.path.join(os.path.dirname(__file__), "data", "daily_boxoffice_2024_2025.csv")
        if os.path.exists(local_csv):
            csv_path = local_csv
        else:
            csv_path = r"C:\Users\Jaeuk\Desktop\M1-1\data\daily_boxoffice_2024_2025.csv"

    records = []
    with open(csv_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            date_str = row.get("date", "").strip()
            total_audi = int(row.get("total_audi", 0))
            top_movie = row.get("top_movie", "").strip()
            top1_share = float(row.get("top1_share", 0.0))

            memo = f"1위: {top_movie} (점유율 {top1_share:.1f}%)"

            records.append({
                "date": date_str,
                "value": total_audi,
                "memo": memo
            })

    return records

if __name__ == "__main__":
    records = load_and_convert_boxoffice_data()
    
    # backend/seed_data.json 파일로 저장
    out_path = os.path.join(os.path.dirname(__file__), "seed_data.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)

    print(f"[성공] 실제 박스오피스 {len(records)}개 시계열 데이터 변환 완료 -> {out_path}")

    # 요약 통계 계산 및 출력
    summary = calculate_summary(records)
    print("\n" + "=" * 50)
    print("[K-BoxOffice AI 데이터 요약 결과]")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print("=" * 50)
