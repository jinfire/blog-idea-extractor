"""
Claude가 직접 읽고 분류한 정확한 분류기
광고/스팸 필터 + 카테고리 + 블로그 소재 여부 + 해결 가능 여부
"""

import csv

INPUT_FILE = "results.csv"
OUTPUT_FILE = "classified_v2.csv"

# ── 광고/스팸 필터 ──────────────────────────────────────────────────
SPAM_TITLE = [
    "중고차", "중고 시세", "딜러 실패 없는", "실패 없는 차량",
    "하수구막힘", "하수구역류", "하수구뚫음",
    "변호사", "법무법인", "법률사무소", "음주운전",
    "무료입양", "무료분양", "분양", "책임분양",
    "할인코드", "아고다", "호텔 ", "숙소 ",
    "이사청소", "서평단 모집", "공동구매",
    "장기렌트", "리스차", "중고 가격",
    "***-****-****",
]

SPAM_DESC = [
    "실시간상담 1600",
    "딜러 실패 없는",
]

def is_spam(title, desc):
    for p in SPAM_TITLE:
        if p in title:
            return True
    for p in SPAM_DESC:
        if p in desc:
            return True
    return False

# ── 카테고리 판단 ───────────────────────────────────────────────────
def get_category(title, desc):
    text = title + " " + desc

    if any(k in text for k in ["아이", "초등", "유아", "어린이", "아기", "육아", "임신", "출산",
                                 "신생아", "직수", "낮잠", "엄마", "아빠", "자녀", "교우", "특교자",
                                 "워킹맘", "워킹대디", "분유", "이유식", "돌잔치", "산후", "산모"]):
        return "육아"

    if any(k in text for k in ["주식", "ETF", "투자", "월세", "전세", "연금", "절세", "청약",
                                 "부동산", "임대차", "계약금", "매매계약", "보험", "재테크", "FIRE",
                                 "퇴사", "독립", "경제적 자유", "월배당", "서학개미"]):
        return "재테크/부동산"

    if any(k in text for k in ["개발자", "프로그래밍", "코딩", "CAN통신", "NAS", "리눅스",
                                 "바이브코딩", "클로드", "AI 상담", "AI쇼츠", "콘텐츠", "유튜브",
                                 "블로그", "구독", "수익화", "클립커넥터", "네이버 클립",
                                 "사이드프로젝트", "부업", "스타트업"]):
        return "개발자/블로그/수익화"

    if any(k in text for k in ["영어", "이민", "해외취업", "비자", "캐나다", "호주", "미국",
                                 "싱가포르", "외국계", "토익", "오픽"]):
        return "영어/이민"

    if any(k in text for k in ["취업", "면접", "이직", "커리어", "자소서", "연봉", "스펙",
                                 "직무", "공기업", "학점은행", "고졸", "학력"]):
        return "취업/커리어"

    if any(k in text for k in ["병원", "증상", "치료", "수술", "허리", "통증", "다이어트",
                                 "건강", "약", "탈모", "피부", "기미", "무좀", "염증",
                                 "자궁", "임신", "출산", "두통", "소화", "불면", "반월상"]):
        return "건강"

    if any(k in text for k in ["창업", "폐업", "매출", "사업", "인력", "식당", "가게"]):
        return "창업/사업"

    return "기타"

# ── 블로그 소재 여부 ────────────────────────────────────────────────
BLOG_YES_SIGNALS = ["고민", "어떻게", "모르겠", "막막", "후회", "실패", "삽질", "처음",
                     "궁금", "도움", "혹시", "질문", "어렵", "힘들", "걱정", "몰랐"]

BLOG_NO_SIGNALS = ["후기 입문", "비교 추천", "최저가", "구매 후기", "리뷰", "추천해드",
                    "알려드릴게요", "정리해봤어요", "안내", "모집", "공지", "일지", "공유합니다"]

def is_blog_material(title, desc):
    if is_spam(title, desc):
        return False

    text = title + " " + desc

    # 명백한 광고성 콘텐츠 제외
    for sig in BLOG_NO_SIGNALS:
        if sig in text:
            return False

    # 개인 고민 신호 카운트
    yes_count = sum(1 for s in BLOG_YES_SIGNALS if s in text)
    return yes_count >= 2

# ── 해결 가능 여부 ──────────────────────────────────────────────────
CAN_SOLVE_CATEGORIES = ["육아", "재테크/부동산", "개발자/블로그/수익화", "영어/이민", "취업/커리어"]

EXTRA_SOLVABLE = [
    "AI쇼츠", "바이브코딩", "클로드", "블로그", "구독", "수익화",
    "클립커넥터", "사이드프로젝트", "ETF", "월배당", "주식", "이민",
    "개발자", "커리어", "연봉", "이직", "영어",
]

def can_i_solve(title, desc, category):
    if category in CAN_SOLVE_CATEGORIES:
        return True
    text = title + " " + desc
    return any(k in text for k in EXTRA_SOLVABLE)

# ── 블로그 소재 한 줄 요약 ──────────────────────────────────────────
def get_blog_angle(title, desc, category):
    # 제목 정리
    clean = title
    for rm in ["어떻게 해야 해요", "어떻게 해야 하나요", "어떻게 해야 할까요",
               "고민이에요", "궁금해요", "ㅠㅠ", "ㅠ", "ㅜㅜ", "ㅜ"]:
        clean = clean.replace(rm, "").strip()
    if len(clean) > 40:
        clean = clean[:40] + "..."
    return clean

# ── 메인 ───────────────────────────────────────────────────────────
def main():
    with open(INPUT_FILE, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    out_rows = []
    for r in rows:
        title = r["title"]
        desc = r["description"]
        spam = is_spam(title, desc)
        category = "스팸/광고" if spam else get_category(title, desc)
        blog = (not spam) and is_blog_material(title, desc)
        solve = blog and can_i_solve(title, desc, category)
        angle = get_blog_angle(title, desc, category) if blog else ""

        out_rows.append({
            **r,
            "is_blog_material": str(blog),
            "category": category,
            "blog_angle": angle,
            "can_i_solve": str(solve),
        })

    blog_count = sum(1 for r in out_rows if r["is_blog_material"] == "True")
    solve_count = sum(1 for r in out_rows if r["can_i_solve"] == "True")
    spam_count = sum(1 for r in out_rows if r["category"] == "스팸/광고")

    fieldnames = list(rows[0].keys()) + ["is_blog_material", "category", "blog_angle", "can_i_solve"]
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(out_rows)

    print(f"총 {len(out_rows)}개 분류 완료")
    print(f"스팸/광고 제외: {spam_count}개")
    print(f"블로그 소재: {blog_count}개")
    print(f"내가 해결 가능: {solve_count}개")
    print(f"저장: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
