"""
Google Sheets에 분류 결과 업로드
- 내가_쓸_수_있는: can_i_solve=True (65개)
- 블로그_소재: is_blog_material=True, can_i_solve=False (60개)
"""
import csv
import json
import os
from dotenv import load_dotenv

load_dotenv()

INPUT_FILE = "classified_v3.csv"

# F->A->G->H->C->E->D->B 순서
COLUMNS = ["category", "title", "blog_angle", "desc_summary", "cafename", "crawled_at", "keyword", "link"]
HEADERS = ["카테고리",  "제목",   "블로그아이디어",  "한줄요약",    "카페명",   "수집일시",   "키워드",  "링크"]


def get_workbook():
    import gspread
    from google.oauth2.service_account import Credentials

    sheet_id = os.getenv("GOOGLE_SHEET_ID")
    creds_json = os.getenv("GOOGLE_CREDENTIALS_JSON")

    creds = Credentials.from_service_account_info(
        json.loads(creds_json),
        scopes=[
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ]
    )
    gc = gspread.authorize(creds)
    return gc.open_by_key(sheet_id)


def get_or_create_sheet(wb, name):
    try:
        return wb.worksheet(name)
    except Exception:
        ws = wb.add_worksheet(title=name, rows=1000, cols=20)
        return ws


def upload(ws, rows, clear=False):
    if clear:
        ws.clear()
        ws.append_row(HEADERS)
        existing_links = set()
    else:
        existing = ws.get_all_values()
        if not existing:
            ws.append_row(HEADERS)
            existing_links = set()
        else:
            link_col = COLUMNS.index("link")
            existing_links = {r[link_col] for r in existing[1:] if len(r) > link_col}

    new_rows = [
        [r.get(col, "") for col in COLUMNS]
        for r in rows if r["link"] not in existing_links
    ]
    if new_rows:
        ws.append_rows(new_rows, value_input_option="RAW")
    return len(new_rows)


def main():
    with open(INPUT_FILE, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    can_solve  = [r for r in rows if r["can_i_solve"] == "True"]
    blog_only  = [r for r in rows if r["is_blog_material"] == "True" and r["can_i_solve"] == "False"]

    print(f"내가_쓸_수_있는: {len(can_solve)}개")
    print(f"블로그_소재: {len(blog_only)}개")

    wb = get_workbook()
    print("Sheets 연결 성공")

    ws1 = get_or_create_sheet(wb, "내가_쓸_수_있는")
    ws2 = get_or_create_sheet(wb, "블로그_소재")

    n1 = upload(ws1, can_solve, clear=True)
    n2 = upload(ws2, blog_only, clear=True)

    print(f"내가_쓸_수_있는: {n1}개 추가")
    print(f"블로그_소재: {n2}개 추가")
    print(f"\nhttps://docs.google.com/spreadsheets/d/{os.getenv('GOOGLE_SHEET_ID')}")


if __name__ == "__main__":
    main()
