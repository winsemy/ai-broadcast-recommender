from flask import Flask, jsonify, request
from flask_cors import CORS
from bs4 import BeautifulSoup  # (필수) 실제 크롤링 라이브러리
import requests              # (필수) 실제 크롤링 라이브러리
import time                      

# --- Flask 앱 생성 ---
app = Flask(__name__)
CORS(app)

# --- 0단계: AI의 '기억 장소' (글로벌 데이터베이스) ---
GLOBAL_PROGRAM_DB = []

# --- 1-A단계: AI의 '태그 생성' 기능 ---
def generate_tags_for_program(title):
    """
    (v2와 동일) AI가 프로그램 제목을 보고 '스스로' 태그를 추측합니다.
    """
    tags = set() 
    title_lower = title.lower() 

    # 키워드 규칙
    if '성서' in title_lower or '바이블' in title_lower or '말씀' in title_lower or '큐티' in title_lower or 'qt' in title_lower or '성경' in title_lower:
        tags.add('#성경공부')
        tags.add('#말씀묵상')
    if '새롭게 하소서' in title_lower or '간증' in title_lower or '힐링' in title_lower or '이야기' in title_lower:
        tags.add('#간증')
        tags.add('#힐링토크')
        tags.add('#삶의이야기')
    if '찬양' in title_lower or '예배' in title_lower or '워십' in title_lower or 'worship' in title_lower:
        tags.add('#찬양')
        tags.add('#예배실황')
    if '기도' in title_lower or 'calling' in title_lower:
        tags.add('#기도')
    if '시사' in title_lower or '뉴스' in title_lower or '특강' in title_lower or '세바시' in title_lower:
        tags.add('#시사교양')
        tags.add('#강연')
    if '어린이' in title_lower or '키즈' in title_lower or 'kids' in title_lower or '세대' in title_lower:
        tags.add('#다음세대')
        tags.add('#어린이')

    if not tags: tags.add('#기타')
    return list(tags) 

# --- 1-B단계: 5대 방송사 '진짜' 웹 크롤링 함수 ---

# (공통) 차단을 피하기 위한 User-Agent 헤더
HEADERS = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'}

def crawl_cbs_data():
    """ (v3) '진짜' CBS 웹 크롤링 - HTML 구조 추정치를 수정 """
    print("AI가 [진짜] CBS 사이트를 '공부'하는 중...")
    URL = "https://www.cbs.co.kr/tv/program"
    program_list = []
    try:
        response = requests.get(URL, headers=HEADERS, timeout=5)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # (v2) div.program_list ul li a -> (v3) ul.pro_list li a strong.title 로 추정치 변경
        program_elements = soup.select("ul.pro_list li a strong.title") 
        
        # 만약 v3 추정치도 실패하면, v2 추정치로 다시 시도
        if not program_elements:
            program_elements = soup.select("div.program_list ul li a strong.pr_title")

        if not program_elements: raise Exception("CBS 프로그램 목록을 찾는 데 실패했습니다 (HTML 구조 변경됨).")

        processed_titles = set()
        for item in program_elements:
            title_text = item.get_text(strip=True)
            if title_text and title_text not in processed_titles:
                processed_titles.add(title_text)
                tags = generate_tags_for_program(title_text)
                program_list.append({'방송사': 'CBS', '프로그램명': title_text, '태그': tags})
        
        print(f"  [성공] CBS에서 {len(program_list)}개의 '진짜' 프로그램을 찾았습니다.")
        return program_list
    except Exception as e:
        print(f"  [오류] CBS 크롤링 실패: {e}")
        print("  [대체] 시뮬레이션 데이터로 대신합니다.")
        return [{'방송사': 'CBS', '프로그램명': '새롭게 하소서 (시뮬레이션)', '태그': ['#간증', '#삶의이야기', '#힐링토크']}]

def crawl_cts_data():
    """ (v3) '진짜' CTS 웹 크롤링 - 신규 """
    print("AI가 [진짜] CTS 사이트를 '공부'하는 중...")
    URL = "https://www.cts.tv/program/list" # (CTS 프로그램 리스트 URL - 추정)
    program_list = []
    try:
        response = requests.get(URL, headers=HEADERS, timeout=5)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # (CTS HTML 구조 추정치 - 예: div.program-list-box li a strong)
        program_elements = soup.select("div.program-list-box li a strong") 
        if not program_elements: raise Exception("CTS 프로그램 목록을 찾는 데 실패했습니다 (HTML 구조 변경됨).")

        processed_titles = set()
        for item in program_elements:
            title_text = item.get_text(strip=True)
            if title_text and title_text not in processed_titles:
                processed_titles.add(title_text)
                tags = generate_tags_for_program(title_text)
                program_list.append({'방송사': 'CTS', '프로그램명': title_text, '태그': tags})
        
        print(f"  [성공] CTS에서 {len(program_list)}개의 '진짜' 프로그램을 찾았습니다.")
        return program_list
    except Exception as e:
        print(f"  [오류] CTS 크롤링 실패: {e}")
        print("  [대체] 시뮬레이션 데이터로 대신합니다.")
        return [{'방송사': 'CTS', '프로그램명': '내가 매일 기쁘게 (시뮬레이션)', '태그': ['#간증', '#삶의이야기', '#유명인']}]


def crawl_cgn_data():
    """ (v3) '진짜' CGNTV 웹 크롤링 - 신규 """
    print("AI가 [진짜] CGNTV 사이트를 '공부'하는 중...")
    URL = "https://www.cgnf.net/program/program_list.asp" # (CGNTV 프로그램 리스트 URL - 추정)
    program_list = []
    try:
        response = requests.get(URL, headers=HEADERS, timeout=5)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # (CGNTV HTML 구조 추정치 - 예: ul.program_list li a div.pro_title)
        program_elements = soup.select("ul.program_list li a div.pro_title") 
        if not program_elements: raise Exception("CGNTV 프로그램 목록을 찾는 데 실패했습니다 (HTML 구조 변경됨).")

        processed_titles = set()
        for item in program_elements:
            title_text = item.get_text(strip=True)
            if title_text and title_text not in processed_titles:
                processed_titles.add(title_text)
                tags = generate_tags_for_program(title_text)
                program_list.append({'방송사': 'CGNTV', '프로그램명': title_text, '태그': tags})
        
        print(f"  [성공] CGNTV에서 {len(program_list)}개의 '진짜' 프로그램을 찾았습니다.")
        return program_list
    except Exception as e:
        print(f"  [오류] CGNTV 크롤링 실패: {e}")
        print("  [대체] 시뮬레이션 데이터로 대신합니다.")
        return [{'방송사': 'CGNTV', '프로그램명': '생명의 삶 (QT) (시뮬레이션)', '태그': ['#말씀묵상', '#매일', '#조용한']}]

def crawl_goodtv_data():
    """ (v3) '진짜' GoodTV 웹 크롤링 - 신규 """
    print("AI가 [진짜] GoodTV 사이트를 '공부'하는 중...")
    URL = "https://www.goodtv.co.kr/program-list/" # (GoodTV 프로그램 리스트 URL - 추정)
    program_list = []
    try:
        response = requests.get(URL, headers=HEADERS, timeout=5)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # (GoodTV HTML 구조 추정치 - 예: div.program_txt_wrap strong.tit)
        program_elements = soup.select("div.program_txt_wrap strong.tit") 
        if not program_elements: raise Exception("GoodTV 프로그램 목록을 찾는 데 실패했습니다 (HTML 구조 변경됨).")

        processed_titles = set()
        for item in program_elements:
            title_text = item.get_text(strip=True)
            if title_text and title_text not in processed_titles:
                processed_titles.add(title_text)
                tags = generate_tags_for_program(title_text)
                program_list.append({'방송사': 'GoodTV', '프로그램명': title_text, '태그': tags})
        
        print(f"  [성공] GoodTV에서 {len(program_list)}개의 '진짜' 프로그램을 찾았습니다.")
        return program_list
    except Exception as e:
        print(f"  [오류] GoodTV 크롤링 실패: {e}")
        print("  [대체] 시뮬레이션 데이터로 대신합니다.")
        return [{'방송사': 'GoodTV', '프로그램명': '다니엘 기도회 (시뮬레이션)', '태그': ['#예배실황', '#뜨거운찬양', '#기도', '#연합']}]

def crawl_cchannel_data():
    """ (v3) '진짜' C Channel 웹 크롤링 - 신규 """
    print("AI가 [진짜] C Channel 사이트를 '공부'하는 중...")
    URL = "https://www.cchannel.com/program" # (C Channel 프로그램 리스트 URL - 추정)
    program_list = []
    try:
        response = requests.get(URL, headers=HEADERS, timeout=5)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # (C Channel HTML 구조 추정치 - 예: div.program-list-box li .pro-title-box span.title)
        program_elements = soup.select("div.program-list-box li .pro-title-box span.title") 
        if not program_elements: raise Exception("C Channel 프로그램 목록을 찾는 데 실패했습니다 (HTML 구조 변경됨).")

        processed_titles = set()
        for item in program_elements:
            title_text = item.get_text(strip=True)
            if title_text and title_text not in processed_titles:
                processed_titles.add(title_text)
                tags = generate_tags_for_program(title_text)
                program_list.append({'방송사': 'C Channel', '프로그램명': title_text, '태그': tags})
        
        print(f"  [성공] C Channel에서 {len(program_list)}개의 '진짜' 프로그램을 찾았습니다.")
        return program_list
    except Exception as e:
        print(f"  [오류] C Channel 크롤링 실패: {e}")
        print("  [대체] 시뮬레이션 데이터로 대신합니다.")
        return [{'방송사': 'C Channel', '프로그램명': '성지가 좋다 (시뮬레이션)', '태그': ['#성경공부', '#시사교양', '#성지순례']}]


# --- (이하 코드는 v2와 동일) ---

def update_database_job():
    print("\n[AI 자동 실행] 5개 방송사 최신 프로그램 '공부'를 시작합니다...")
    global GLOBAL_PROGRAM_DB
    new_db = []
    
    # (중요!) 5개 모두 '진짜' 크롤링 함수로 교체
    new_db.extend(crawl_cbs_data()) 
    new_db.extend(crawl_cts_data())
    new_db.extend(crawl_cgn_data())
    new_db.extend(crawl_goodtv_data())
    new_db.extend(crawl_cchannel_data())
    
    GLOBAL_PROGRAM_DB = new_db
    print(f"\n[AI 자동 실행] '공부' 완료. 총 {len(GLOBAL_PROGRAM_DB)}개의 프로그램을 '기억'했습니다.\n")

# --- 2단계: AI 추천 엔진 (핵심 로직) ---
def recommend_programs(user_tags, db):
    recommendations = []
    for program in db:
        program_tags = program['태그']
        match_score = 0
        for tag in user_tags:
            if tag in program_tags:
                match_score += 1
        if match_score > 0:
            recommendations.append((match_score, program))
    recommendations.sort(key=lambda x: x[0], reverse=True)
    final_list = [program for score, program in recommendations]
    return final_list

# --- 3단계: '얼굴(HTML)'과 '두뇌(서버)'의 연결 통로 (API) ---
@app.route('/recommend', methods=['POST'])
def handle_recommendation():
    data = request.json
    user_tags = data.get('tags', [])
    if not user_tags:
        return jsonify({'error': '태그가 전송되지 않았습니다.'}), 400
    print(f"\n[요청 수신] 사용자 태그: {user_tags}")
    results = recommend_programs(user_tags, GLOBAL_PROGRAM_DB)
    print(f"[응답 전송] {len(results)}개 프로그램 추천 (기억에서 즉시 반환)")
    return jsonify(results)

# --- 서버 실행 ---
if __name__ == '__main__':
    update_database_job()
    # (포트 5001번으로 실행)
    print("--- AI 추천 서버가 5000번 포트에서 실행됩니다 ---") 
    app.run(host='0.0.0.0', port=5000)

