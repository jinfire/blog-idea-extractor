import os
import re
import requests
from datetime import datetime, timezone
from dotenv import load_dotenv

from keywords import KEYWORDS
from storage import save_result

load_dotenv()

NAVER_CLIENT_ID = os.getenv("NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")
NAVER_API_URL = "https://openapi.naver.com/v1/search/cafearticle.json"


def search_cafe(keyword: str, display: int = 100) -> list[dict]:
    headers = {
        "X-Naver-Client-Id": NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": NAVER_CLIENT_SECRET,
    }
    params = {
        "query": keyword,
        "display": display,
        "sort": "date",
    }
    resp = requests.get(NAVER_API_URL, headers=headers, params=params, timeout=10)
    resp.raise_for_status()
    return resp.json().get("items", [])


def clean_html(text: str) -> str:
    return re.sub(r"<[^>]+>", "", text).strip()


def crawl_all():
    seen_urls = set()
    results = []

    for keyword in KEYWORDS:
        print(f"[검색] {keyword}")
        try:
            items = search_cafe(keyword)
        except Exception as e:
            print(f"  오류: {e}")
            continue

        for item in items:
            link = item.get("link", "")
            if link in seen_urls:
                continue
            seen_urls.add(link)

            row = {
                "title": clean_html(item.get("title", "")),
                "link": link,
                "description": clean_html(item.get("description", "")),
                "cafename": item.get("cafename", ""),
                "cafeurl": item.get("cafeurl", ""),
                "keyword": keyword,
                "crawled_at": datetime.now(timezone.utc).isoformat(),
            }
            results.append(row)
            save_result(row)

    print(f"\n완료: {len(results)}개 저장")


if __name__ == "__main__":
    crawl_all()
