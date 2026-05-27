import csv
import re

INPUT_FILE = "results.csv"
OUTPUT_FILE = "classified.csv"

# 광고/스팸 패턴
AD_PATTERNS = [
    r'\*\*\*', r'\d{3}-\d{4}-\d{4}',
    '할인코드', '쿠폰', '후기 입문', '비교 추천', '최저가', '구매',
    '아고다', '호텔 ', '숙소 ', '이사청소', '업체', '서평단 모집',
    '공동구매', '판매', '분양', '광고', '협찬', '리뷰어 모집'
]

# 카테고리 키워드 매핑
CATEGORY_MAP = [
    ('육아', ['아이', '초등', '유아', '어린이', '아기', '엄마', '아빠', '육아', '임신', '출산',
              '유치원', '학교', '친구문제', '교우', '워킹맘', '워킹대디', '자녀']),
    ('재테크', ['주식', '부동산', 'ETF', '투자', '월세', '전세', '연금', '절세', '적금',
                '펀드', '코인', '청약', 'FIRE', '퇴사', '독립', '파이어', '경제적 자유']),
    ('개발자커리어', ['개발자', '프로그래밍', '코딩', '취업', '이직', 'IT', '스타트업',
                      '연봉', '면접', '포트폴리오', '개발', '엔지니어', '백엔드', '프론트',
                      'AWS', '클라우드', 'AI', '인공지능', '사이드프로젝트', '사이드 프로젝트']),
    ('영어/이민', ['영어', '이민', '해외취업', '비자', '캐나다', '호주', '미국', '싱가포르',
                   '해외', '영어공부', '외국계', '토익', '오픽']),
    ('건강', ['병원', '의사', '증상', '치료', '수술', '피부', '허리', '통증', '다이어트',
              '건강', '약', '몸', '두통', '소화', '불면', '기미', '탈모']),
    ('업무/생산성', ['업무', '직장', '회사', '일', '야근', '상사', '동료', '프리랜서',
                     '재택', '번아웃', '루틴', '시간관리', '생산성']),
    ('블로그/수익화', ['블로그', '수익화', '애드센스', '유튜브', '인스타', '콘텐츠',
                       '사이드 허슬', '부업', '온라인 강의', '전자책', '인디해킹']),
    ('부동산', ['아파트', '집', '청약', '전세', '월세', '인테리어', '이사', '등기']),
]

# 사용자 해결 가능 카테고리
CAN_SOLVE_CATEGORIES = ['개발자커리어', '영어/이민', '육아', '재테크', '블로그/수익화', '업무/생산성']


def is_ad(title, description):
    text = title + description
    for pattern in AD_PATTERNS:
        if re.search(pattern, text):
            return True
    return False


def is_real_post(title, description):
    """진짜 고민글인지 판단"""
    text = title + description
    # 광고 필터
    if is_ad(title, description):
        return False
    # 개인 고민/질문 신호
    personal_signals = ['저', '제가', '우리', '고민', '어떻게', '모르겠', '힘들', '막막',
                        '후회', '실패', '삽질', '처음', '궁금', '도움', '혹시', '질문']
    count = sum(1 for s in personal_signals if s in text)
    return count >= 2


def get_category(title, description):
    text = title + description
    for category, keywords in CATEGORY_MAP:
        if any(kw in text for kw in keywords):
            return category
    return '기타'


def get_blog_topic(title, description, category):
    """블로그 소재 한 줄 요약"""
    title = title.replace('어떻게 해야 해요', '').replace('어떻게 해야 하나요', '').strip()
    if len(title) > 30:
        title = title[:30] + '...'
    return title


def classify(row):
    title = row['title']
    desc = row['description']
    text = title + desc

    is_blog = is_real_post(title, desc)
    category = get_category(title, desc)
    can_solve = category in CAN_SOLVE_CATEGORIES and is_blog
    blog_topic = get_blog_topic(title, desc, category) if is_blog else ''

    return {
        **row,
        'is_blog_material': str(is_blog),
        'category': category,
        'blog_topic': blog_topic,
        'can_i_solve': str(can_solve),
    }


def main():
    with open(INPUT_FILE, encoding='utf-8') as f:
        rows = list(csv.DictReader(f))

    classified = [classify(r) for r in rows]

    blog_count = sum(1 for r in classified if r['is_blog_material'] == 'True')
    solvable = sum(1 for r in classified if r['can_i_solve'] == 'True')

    fieldnames = list(rows[0].keys()) + ['is_blog_material', 'category', 'blog_topic', 'can_i_solve']
    with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(classified)

    print(f'총 {len(classified)}개 분류 완료')
    print(f'블로그 소재: {blog_count}개')
    print(f'내가 해결 가능: {solvable}개')
    print(f'저장: {OUTPUT_FILE}')


if __name__ == '__main__':
    main()
