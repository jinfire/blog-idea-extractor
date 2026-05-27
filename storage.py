import os
import csv
import json
from pathlib import Path

GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID")
GOOGLE_CREDENTIALS_JSON = os.getenv("GOOGLE_CREDENTIALS_JSON")

CSV_PATH = Path("results.csv")

HEADERS = ["title", "link", "description", "cafename", "cafeurl", "keyword", "crawled_at"]


def _get_sheet():
    if not GOOGLE_SHEET_ID or not GOOGLE_CREDENTIALS_JSON:
        return None
    try:
        import gspread
        from google.oauth2.service_account import Credentials

        creds_dict = json.loads(GOOGLE_CREDENTIALS_JSON)
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ]
        creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        gc = gspread.authorize(creds)
        sh = gc.open_by_key(GOOGLE_SHEET_ID)

        try:
            ws = sh.worksheet("results")
        except gspread.WorksheetNotFound:
            ws = sh.add_worksheet(title="results", rows=10000, cols=20)
            ws.append_row(HEADERS)

        return ws
    except Exception as e:
        print(f"  Sheets 연결 실패: {e}")
        return None


def save_result(data: dict):
    ws = _get_sheet()
    row = [str(data.get(col, "")) for col in HEADERS]

    if ws:
        try:
            existing_links = ws.col_values(2)  # link 컬럼
            if data.get("link") in existing_links:
                print(f"  중복 스킵")
                return
            ws.append_row(row)
            print(f"  Sheets 저장")
            return
        except Exception as e:
            print(f"  Sheets 실패, CSV로: {e}")

    # CSV fallback
    file_exists = CSV_PATH.exists()
    with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=HEADERS, extrasaction="ignore")
        if not file_exists:
            writer.writeheader()
        writer.writerow(data)
    print(f"  CSV 저장")
