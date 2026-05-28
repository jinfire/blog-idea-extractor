"""
크롤링 결과를 results.csv에 저장
중복은 링크 기준으로 제거
Google Sheets 업로드는 push_to_sheets.py에서 별도 처리
"""
import csv
from pathlib import Path

CSV_PATH = Path("results.csv")
HEADERS = ["title", "link", "description", "cafename", "cafeurl", "keyword", "crawled_at"]

# 실행 시 한 번만 기존 링크 로드 (매번 파일 읽기 방지)
_existing_links: set | None = None


def _load_existing_links() -> set:
    global _existing_links
    if _existing_links is not None:
        return _existing_links
    _existing_links = set()
    if CSV_PATH.exists():
        with open(CSV_PATH, encoding="utf-8") as f:
            for row in csv.DictReader(f):
                if row.get("link"):
                    _existing_links.add(row["link"])
    return _existing_links


def save_result(data: dict):
    existing = _load_existing_links()
    link = data.get("link", "")

    if link in existing:
        return  # 중복 스킵

    existing.add(link)

    file_exists = CSV_PATH.exists()
    with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=HEADERS, extrasaction="ignore")
        if not file_exists:
            writer.writeheader()
        writer.writerow(data)
