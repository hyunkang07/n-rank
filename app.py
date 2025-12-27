import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import time
import hashlib
import hmac
import base64
import json
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

# 페이지 설정
st.set_page_config(
    page_title="네이버 키워드 분석 도구",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 커스텀 CSS - 밝은 테마
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&display=swap');
    
    * {
        font-family: 'Noto Sans KR', sans-serif;
    }
    
    .main {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
    }
    
    .stApp {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
    }
       
    .main-header {
        background: linear-gradient(90deg, #00c73c 0%, #00a032 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem;
        font-weight: 700;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    
    .sub-header {
        color: #475569;
        text-align: center;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 24px rgba(0, 199, 60, 0.15);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: #00a032;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .stButton > button {
        background: linear-gradient(90deg, #00c73c 0%, #00a032 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 2rem;
        font-size: 1rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(0, 199, 60, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0, 199, 60, 0.4);
    }
    
    .stTextInput > div > div > input {
        background: white;
        border: 2px solid #e2e8f0;
        border-radius: 12px;
        color: #1e293b;
        padding: 0.75rem 1rem;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #00c73c;
        box-shadow: 0 0 0 3px rgba(0, 199, 60, 0.15);
    }
    
    div[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #ffffff 0%, #f1f5f9 100%);
        border-right: 1px solid #e2e8f0;
    }
    
    div[data-testid="stSidebar"] .stMarkdown {
        color: #334155;
    }
    
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid #e2e8f0;
    }
    
    h1, h2, h3 {
        color: #1e293b !important;
    }
    
    .stMarkdown {
        color: #475569;
    }
    
    .stMetric {
        background: white;
        padding: 1rem;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    }
    
    .stMetric label {
        color: #64748b !important;
    }
    
    .stMetric [data-testid="stMetricValue"] {
        color: #00a032 !important;
    }
    
    .info-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
        margin: 0.5rem 0;
    }
    
    .info-card h3 {
        color: #00a032 !important;
        margin-bottom: 0.5rem;
    }
    
    .info-card p {
        color: #64748b;
        margin: 0;
    }
    
    .related-keyword-container {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        margin-top: 0.5rem;
    }
    
    .related-keyword-tag {
        background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
        color: #2e7d32;
        padding: 0.4rem 0.8rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 500;
        border: 1px solid #a5d6a7;
        cursor: pointer;
        transition: all 0.2s ease;
        text-decoration: none;
    }
    
    .related-keyword-tag:hover {
        background: linear-gradient(135deg, #c8e6c9 0%, #a5d6a7 100%);
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 199, 60, 0.2);
    }
    
    .related-section {
        background: white;
        padding: 1rem 1.5rem;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        margin-top: 1rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    }
    
    .related-title {
        color: #1e293b;
        font-size: 0.95rem;
        font-weight: 600;
        margin-bottom: 0.75rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)


# ==================== 검색광고 API 함수 ====================

class Signature:
    @staticmethod
    def generate(timestamp, method, uri, secret_key):
        message = "{}.{}.{}".format(timestamp, method, uri)
        hash = hmac.new(bytes(secret_key, "utf-8"), bytes(message, "utf-8"), hashlib.sha256)
        hash.hexdigest()
        return base64.b64encode(hash.digest())


def get_header(method, uri, api_key, secret_key, customer_id):
    timestamp = str(round(time.time() * 1000))
    signature = Signature.generate(timestamp, method, uri, secret_key)
    
    return {
        'Content-Type': 'application/json; charset=UTF-8',
        'X-Timestamp': timestamp,
        'X-API-KEY': api_key,
        'X-Customer': str(customer_id),
        'X-Signature': signature
    }


def get_keyword_results(hint_keywords, api_key, secret_key, customer_id):
    """키워드 분석 결과를 가져오는 함수"""
    BASE_URL = 'https://api.naver.com'
    uri = '/keywordstool'
    method = 'GET'
    
    params = {
        'hintKeywords': hint_keywords,
        'showDetail': '1'
    }
    
    try:
        response = requests.get(
            BASE_URL + uri,
            params=params,
            headers=get_header(method, uri, api_key, secret_key, customer_id)
        )
        
        if response.status_code == 200:
            data = response.json()
            if 'keywordList' in data:
                return pd.DataFrame(data['keywordList']), None
            else:
                return None, "키워드 데이터를 찾을 수 없습니다."
        else:
            return None, f"API 오류: {response.status_code} - {response.text}"
    except Exception as e:
        return None, f"요청 중 오류 발생: {str(e)}"


# ==================== 블로그 검색 API 함수 ====================

def get_blog_search_result(client_id, client_secret, query, display=100, start=1, sort='sim'):
    """네이버 블로그 검색 결과를 가져오는 함수"""
    url = "https://openapi.naver.com/v1/search/blog.json"
    
    headers = {
        "X-Naver-Client-Id": client_id,
        "X-Naver-Client-Secret": client_secret
    }
    
    params = {
        "query": query,
        "display": display,
        "start": start,
        "sort": sort
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            items = data.get('items', [])
            
            # HTML 태그 제거
            for item in items:
                item['title'] = item['title'].replace('<b>', '').replace('</b>', '')
                item['description'] = item['description'].replace('<b>', '').replace('</b>', '')
            
            return pd.DataFrame(items), None
        else:
            return None, f"API 오류: {response.status_code} - {response.text}"
    except Exception as e:
        return None, f"요청 중 오류 발생: {str(e)}"


def get_blog_rank_selenium(search_query, target_blog_link, max_scroll_attempts=7, progress_callback=None):
    """Selenium을 사용하여 네이버 블로그 순위를 찾는 함수"""
    driver = None
    try:
        # Chrome 옵션 설정
        options = Options()
        options.add_argument("--headless")  # 백그라운드 실행
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--log-level=3")
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        
        # WebDriver 초기화
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        # 검색 URL 생성
        search_link = f"https://search.naver.com/search.naver?where=view&sm=tab_jum&query={search_query}"
        driver.get(search_link)
        time.sleep(2)
        
        blog_found = False
        current_rank = -1
        link_selector = f'a[href^="{target_blog_link}"]'
        
        # 스크롤하며 블로그 찾기
        for attempt in range(max_scroll_attempts):
            if progress_callback:
                progress_callback((attempt + 1) / max_scroll_attempts, 
                                f"시도 {attempt + 1}/{max_scroll_attempts}: 블로그 검색 중...")
            
            try:
                # 타겟 블로그 링크 찾기
                element = driver.find_element(By.CSS_SELECTOR, link_selector)
                
                # 부모 요소를 거슬러 올라가며 순위 찾기
                while True:
                    try:
                        rank_text = element.get_attribute("data-cr-rank")
                        if rank_text is not None:
                            current_rank = int(rank_text)
                            blog_found = True
                            break
                        else:
                            element = element.find_element(By.XPATH, "./..")
                    except NoSuchElementException:
                        break
                
                if blog_found:
                    break
                    
            except NoSuchElementException:
                # 블로그를 찾지 못하면 스크롤
                driver.execute_script("window.scrollBy(0, 10000);")
                time.sleep(3)
        
        return current_rank if blog_found else None, None
        
    except Exception as e:
        return None, f"오류 발생: {str(e)}"
    finally:
        if driver:
            driver.quit()


def get_multiple_blog_ranks_selenium(search_queries, target_blog_links, max_scroll_attempts=7, progress_callback=None):
    """여러 키워드에 대한 블로그 순위를 Selenium으로 조회하는 함수"""
    results = []
    total_queries = len(search_queries)
    
    for idx, (search_query, target_blog_link) in enumerate(zip(search_queries, target_blog_links)):
        if progress_callback:
            progress_callback(idx / total_queries, f"키워드 {idx + 1}/{total_queries}: '{search_query}' 처리 중...")
        
        rank, error = get_blog_rank_selenium(search_query, target_blog_link, max_scroll_attempts)
        
        results.append({
            '검색어': search_query,
            'URL': target_blog_link,
            '순위': rank if rank else "순위권 밖",
            '상태': '성공' if rank else ('오류' if error else '순위권 밖')
        })
    
    if progress_callback:
        progress_callback(1.0, "완료!")
    
    return pd.DataFrame(results), None


# ==================== 통합검색 트렌드 API 함수 ====================

def get_trend_data(client_id, client_secret, keyword_groups, start_date, end_date, time_unit='date', device='', ages=[], gender=''):
    """네이버 통합검색 트렌드 데이터를 가져오는 함수"""
    url = "https://openapi.naver.com/v1/datalab/search"
    
    # 요청 본문 구성
    body = {
        "startDate": start_date,
        "endDate": end_date,
        "timeUnit": time_unit,
        "keywordGroups": keyword_groups
    }
    
    # 선택적 파라미터 추가
    if device:
        body["device"] = device
    if ages:
        body["ages"] = ages
    if gender:
        body["gender"] = gender
    
    headers = {
        "X-Naver-Client-Id": client_id,
        "X-Naver-Client-Secret": client_secret,
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(body))
        
        if response.status_code == 200:
            return response.json(), None
        else:
            return None, f"API 오류: {response.status_code} - {response.text}"
    except Exception as e:
        return None, f"요청 중 오류 발생: {str(e)}"


# ==================== 유틸리티 함수 ====================

def format_number(num):
    """숫자를 보기 좋게 포맷팅"""
    if pd.isna(num) or num == '< 10':
        return num
    try:
        num = int(num)
        if num >= 1000000:
            return f"{num/1000000:.1f}M"
        elif num >= 1000:
            return f"{num/1000:.1f}K"
        else:
            return str(num)
    except:
        return str(num)


def get_related_keywords(keyword):
    """네이버 검색에서 연관검색어를 가져오는 함수"""
    try:
        url = f"https://search.naver.com/search.naver?where=nexearch&sm=top_hty&fbm=0&ie=utf8&query={keyword}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            related_keywords = []
            
            # 제외할 단어 목록 (UI 관련 텍스트)
            exclude_words = [
                '더보기', '열기', '접기', '닫기', '이전', '다음', '전체보기',
                '검색', '뉴스', '이미지', '동영상', '블로그', '카페', '지식in',
                '쇼핑', 'VIEW', 'shopping', 'naver'
            ]
            
            # 연관검색어 영역에서 찾기
            related_area = soup.find('div', {'class': 'related_srch'})
            if related_area:
                items = related_area.find_all('a')
                for item in items:
                    text = item.get_text(strip=True)
                    # 유효성 검사
                    if (text and 
                        text != keyword and 
                        len(text) > 1 and 
                        len(text) < 50 and
                        not any(exclude in text for exclude in exclude_words)):
                        related_keywords.append(text)
            
            # 추가 연관검색어 찾기
            if not related_keywords:
                items = soup.select('div.keyword_item a, ul.lst_related_srch a')
                for item in items:
                    text = item.get_text(strip=True)
                    # 유효성 검사
                    if (text and 
                        text != keyword and 
                        len(text) > 1 and 
                        len(text) < 50 and
                        not any(exclude in text for exclude in exclude_words)):
                        related_keywords.append(text)
            
            # 중복 제거
            related_keywords = list(dict.fromkeys(related_keywords))
            return related_keywords
        
        return []
    except Exception as e:
        return []


# ==================== 페이지: 키워드 검색량 분석 ====================

def keyword_analysis_page():
    """키워드 검색량 분석 페이지"""
    # 헤더
    st.markdown('<h1 class="main-header">🔍 네이버 키워드 검색량 분석</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">네이버 검색광고 API를 활용한 키워드 검색량 분석</p>', unsafe_allow_html=True)
    
    # 사이드바 - API 설정
    with st.sidebar:
        st.markdown("### ⚙️ 검색광고 API 설정")
        st.markdown("---")
        
        # 기본값으로 사용자의 API 키 설정
        api_key = st.text_input(
            "API Key (엑세스라이선스)",
            value="010000000040aefa21fbb0a3769e556d20040963da514e6b3e7ea7589fe278cb2e857ce16e",
            type="password",
            key="search_api_key"
        )
        
        secret_key = st.text_input(
            "Secret Key (비밀키)",
            value="AQAAAABArvoh+7Cjdp5VbSAECWPayKfamwuyOYal6veBVythVA==",
            type="password",
            key="search_secret_key"
        )
        
        customer_id = st.text_input(
            "Customer ID",
            value="3900043",
            key="search_customer_id"
        )
        
        st.markdown("---")
        st.markdown("### 📊 분석 옵션")
        
        chart_type = st.selectbox(
            "차트 유형",
            ["막대 차트", "수평 막대 차트", "원형 차트", "트리맵"]
        )
        
        top_n = st.slider("상위 키워드 표시 개수", 5, 50, 20)
        
        st.markdown("---")
        st.markdown("### 🔄 연관검색어 옵션")
        
        enable_2nd_level = st.checkbox(
            "2단계 연관검색어 분석",
            value=False,
            help="각 연관검색어의 연관검색어까지 분석합니다 (시간이 오래 걸릴 수 있습니다)"
        )
        
        if enable_2nd_level:
            max_2nd_keywords = st.slider(
                "2단계 분석할 키워드 개수",
                min_value=3,
                max_value=10,
                value=5,
                help="첫 번째 연관검색어 중 상위 몇 개를 추가 분석할지 선택"
            )
        
        st.markdown("---")
        st.markdown("""
        <div style="color: #475569; font-size: 0.85rem; background: #f1f5f9; padding: 1rem; border-radius: 8px;">
        <strong style="color: #1e293b;">💡 사용 방법</strong><br><br>
        1. 분석할 키워드 입력<br>
        2. 검색 버튼 클릭<br>
        3. 결과 확인 및 다운로드
        </div>
        """, unsafe_allow_html=True)
    
    # 메인 컨텐츠
    col1, col2 = st.columns([3, 1])
    
    with col1:
        keyword_input_raw = st.text_input(
            "🔎 분석할 키워드를 입력하세요",
            placeholder="예: 노트북, 스마트폰, 이어폰",
            key="main_keyword_input"
        )
        # 공백 제거
        keyword_input = keyword_input_raw.replace(" ", "") if keyword_input_raw else ""
        
        # 공백이 제거되었을 경우 안내 메시지
        if keyword_input_raw and keyword_input != keyword_input_raw:
            st.info(f"ℹ️ 공백이 제거되었습니다: '{keyword_input_raw}' → '{keyword_input}'")
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        search_button = st.button("🚀 분석 시작", use_container_width=True)
    
    # 검색 버튼 클릭 시 플래그 설정
    if search_button and keyword_input:
        st.session_state.should_analyze = True
    
    # 세션 상태 초기화
    if 'df_result' not in st.session_state:
        st.session_state.df_result = None
    if 'related_keywords' not in st.session_state:
        st.session_state.related_keywords = []
    if 'selected_keyword' not in st.session_state:
        st.session_state.selected_keyword = None
    if 'should_analyze' not in st.session_state:
        st.session_state.should_analyze = False
    
    # 연관검색어 표시 (키워드 입력 시)
    if keyword_input:
        with st.spinner("🔄 1단계 연관검색어 로딩 중..."):
            related = get_related_keywords(keyword_input)
            st.session_state.related_keywords = related
        
        # 2단계 연관검색어 수집 (옵션 활성화 시)
        if enable_2nd_level and st.session_state.related_keywords:
            all_keywords = set(st.session_state.related_keywords[:max_2nd_keywords])
            
            with st.spinner(f"🔄 2단계 연관검색어 수집 중... (총 {len(all_keywords)}개 키워드)"):
                progress_bar = st.progress(0)
                
                for idx, kw in enumerate(list(all_keywords)[:max_2nd_keywords]):
                    second_level = get_related_keywords(kw)
                    all_keywords.update(second_level)
                    progress_bar.progress((idx + 1) / max_2nd_keywords)
                
                progress_bar.empty()
                
                # 전체 키워드 리스트 저장
                st.session_state.all_keywords = list(all_keywords)
                st.success(f"✅ 총 {len(all_keywords)}개의 연관검색어를 수집했습니다! (1단계 + 2단계)")
        else:
            st.session_state.all_keywords = st.session_state.related_keywords
        
        if st.session_state.related_keywords:
            st.markdown("---")
            
            # 표시할 제목 변경
            if enable_2nd_level:
                st.markdown("### 🔗 전체 연관검색어 목록 (1단계 + 2단계)")
                keywords_to_analyze = st.session_state.all_keywords
            else:
                st.markdown("### 🔗 네이버 연관검색어")
                keywords_to_analyze = st.session_state.related_keywords
            
            # 연관검색어의 검색량 데이터 가져오기
            with st.spinner(f"📊 {len(keywords_to_analyze)}개 키워드 검색량 분석 중... (시간이 소요될 수 있습니다)"):
                related_data = []
                progress_bar = st.progress(0)
                
                for idx, kw in enumerate(keywords_to_analyze):
                    # 각 연관검색어에 대해 API 호출
                    df_kw, error = get_keyword_results(kw, api_key, secret_key, customer_id)
                    
                    if df_kw is not None and not df_kw.empty:
                        # 첫 번째 결과(해당 키워드 자체)의 데이터 가져오기
                        first_row = df_kw.iloc[0]
                        pc_cnt = first_row.get('monthlyPcQcCnt', 0)
                        mobile_cnt = first_row.get('monthlyMobileQcCnt', 0)
                        
                        # 문자열 처리
                        if pc_cnt == '< 10':
                            pc_cnt = 0
                        elif isinstance(pc_cnt, str) and pc_cnt.isdigit():
                            pc_cnt = int(pc_cnt)
                        
                        if mobile_cnt == '< 10':
                            mobile_cnt = 0
                        elif isinstance(mobile_cnt, str) and mobile_cnt.isdigit():
                            mobile_cnt = int(mobile_cnt)
                        
                        total_cnt = pc_cnt + mobile_cnt
                        comp_idx = first_row.get('compIdx', '-')
                    else:
                        pc_cnt = 0
                        mobile_cnt = 0
                        total_cnt = 0
                        comp_idx = '-'
                    
                    related_data.append({
                        '번호': idx + 1,
                        '연관검색어': kw,
                        'PC 검색량': pc_cnt,
                        '모바일 검색량': mobile_cnt,
                        '총 검색량': total_cnt,
                        '경쟁정도': comp_idx
                    })
                    
                    # 진행률 업데이트
                    progress_bar.progress((idx + 1) / len(keywords_to_analyze))
                
                progress_bar.empty()
                
                # 데이터프레임 생성
                related_df = pd.DataFrame(related_data)
                
                # 총 검색량 기준으로 정렬
                related_df = related_df.sort_values('총 검색량', ascending=False).reset_index(drop=True)
                related_df['번호'] = range(1, len(related_df) + 1)
            
            # 연관검색어 테이블 전체 너비로 표시
            st.markdown("#### 📋 연관검색어 전체 목록 (검색량 순)")
            
            # 데이터프레임 표시
            st.dataframe(
                related_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "번호": st.column_config.NumberColumn(
                        "번호",
                        width="small",
                    ),
                    "연관검색어": st.column_config.TextColumn(
                        "연관검색어",
                        width="medium",
                    ),
                    "PC 검색량": st.column_config.NumberColumn(
                        "PC 검색량",
                        width="small",
                        format="%d",
                    ),
                    "모바일 검색량": st.column_config.NumberColumn(
                        "모바일 검색량",
                        width="small",
                        format="%d",
                    ),
                    "총 검색량": st.column_config.NumberColumn(
                        "총 검색량",
                        width="small",
                        format="%d",
                    ),
                    "경쟁정도": st.column_config.TextColumn(
                        "경쟁정도",
                        width="small",
                    ),
                },
                height=500
            )
            
            # 통계 정보와 다운로드 버튼
            col_stat, col_download = st.columns([2, 1])
            
            with col_stat:
                st.info(f"""
                📊 **연관검색어 통계**  
                총 키워드: **{len(related_df)}개** | 총 검색량: **{related_df['총 검색량'].sum():,}** | 평균 검색량: **{int(related_df['총 검색량'].mean()):,}**
                """)
            
            with col_download:
                csv_related = related_df.to_csv(index=False, encoding='utf-8-sig')
                st.download_button(
                    label="📥 CSV 다운로드",
                    data=csv_related,
                    file_name=f"related_keywords_{keyword_input}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            
    
    # 분석할 키워드 결정 (직접 입력 또는 연관검색어 클릭)
    analysis_keyword = keyword_input
    if st.session_state.selected_keyword:
        analysis_keyword = st.session_state.selected_keyword
        st.info(f"📌 선택된 연관검색어: **{analysis_keyword}**")
        st.session_state.selected_keyword = None  # 리셋
    
    # 검색 실행
    if st.session_state.should_analyze and keyword_input:
        with st.spinner("🔄 키워드 분석 중..."):
            df, error = get_keyword_results(
                analysis_keyword if analysis_keyword else keyword_input,
                api_key,
                secret_key,
                customer_id
            )
            
            if error:
                st.error(f"❌ {error}")
            elif df is not None and not df.empty:
                st.session_state.df_result = df
                st.session_state.current_keyword = analysis_keyword if analysis_keyword else keyword_input
                st.success(f"✅ '{st.session_state.current_keyword}'에 대해 {len(df)}개의 연관 키워드를 찾았습니다!")
                st.session_state.should_analyze = False  # 분석 완료 후 플래그 리셋
            else:
                st.warning("⚠️ 검색 결과가 없습니다.")
                st.session_state.should_analyze = False  # 실패해도 플래그 리셋
    
    # 결과 표시
    if st.session_state.df_result is not None:
        df = st.session_state.df_result.copy()
        
        st.markdown("---")
        
        # 컬럼명 한글화
        column_mapping = {
            'relKeyword': '연관키워드',
            'monthlyPcQcCnt': 'PC 검색량',
            'monthlyMobileQcCnt': '모바일 검색량',
            'monthlyAvePcClkCnt': 'PC 평균클릭수',
            'monthlyAveMobileClkCnt': '모바일 평균클릭수',
            'monthlyAvePcCtr': 'PC 클릭률',
            'monthlyAveMobileCtr': '모바일 클릭률',
            'plAvgDepth': '광고노출 평균순위',
            'compIdx': '경쟁정도'
        }
        
        df_display = df.rename(columns=column_mapping)
        
        # 숫자 컬럼 처리
        numeric_cols = ['PC 검색량', '모바일 검색량']
        for col in numeric_cols:
            if col in df_display.columns:
                df_display[col] = df_display[col].apply(
                    lambda x: 0 if x == '< 10' else (int(x) if pd.notna(x) and str(x).isdigit() else 0)
                )
        
        # 총 검색량 계산
        if 'PC 검색량' in df_display.columns and '모바일 검색량' in df_display.columns:
            df_display['총 검색량'] = df_display['PC 검색량'] + df_display['모바일 검색량']
        
        # 메트릭 카드
        st.markdown("### 📈 주요 지표")
        
        metric_cols = st.columns(4)
        
        with metric_cols[0]:
            total_keywords = len(df_display)
            st.metric("총 키워드 수", f"{total_keywords:,}개")
        
        with metric_cols[1]:
            if '총 검색량' in df_display.columns:
                total_search = df_display['총 검색량'].sum()
                st.metric("총 검색량", format_number(total_search))
        
        with metric_cols[2]:
            if '총 검색량' in df_display.columns:
                avg_search = df_display['총 검색량'].mean()
                st.metric("평균 검색량", format_number(int(avg_search)))
        
        with metric_cols[3]:
            if '모바일 검색량' in df_display.columns and 'PC 검색량' in df_display.columns:
                mobile_ratio = df_display['모바일 검색량'].sum() / max(df_display['총 검색량'].sum(), 1) * 100
                st.metric("모바일 비율", f"{mobile_ratio:.1f}%")
        
        st.markdown("---")
        
        # 차트 섹션
        st.markdown("### 📊 시각화")
        
        chart_col1, chart_col2 = st.columns(2)
        
        with chart_col1:
            # 상위 키워드 차트
            if '총 검색량' in df_display.columns:
                df_top = df_display.nlargest(top_n, '총 검색량')
                
                if chart_type == "막대 차트":
                    fig = px.bar(
                        df_top,
                        x='연관키워드',
                        y='총 검색량',
                        title=f"🏆 상위 {top_n}개 키워드 검색량",
                        color='총 검색량',
                        color_continuous_scale='Greens'
                    )
                    fig.update_layout(
                        plot_bgcolor='white',
                        paper_bgcolor='white',
                        font_color='#334155',
                        title_font_color='#1e293b',
                        xaxis_tickangle=-45
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                elif chart_type == "수평 막대 차트":
                    fig = px.bar(
                        df_top.sort_values('총 검색량'),
                        y='연관키워드',
                        x='총 검색량',
                        title=f"🏆 상위 {top_n}개 키워드 검색량",
                        color='총 검색량',
                        color_continuous_scale='Greens',
                        orientation='h'
                    )
                    fig.update_layout(
                        plot_bgcolor='white',
                        paper_bgcolor='white',
                        font_color='#334155',
                        title_font_color='#1e293b',
                        height=max(400, top_n * 25)
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                elif chart_type == "원형 차트":
                    fig = px.pie(
                        df_top.head(10),
                        values='총 검색량',
                        names='연관키워드',
                        title="🥧 상위 10개 키워드 비율",
                        hole=0.4
                    )
                    fig.update_layout(
                        plot_bgcolor='white',
                        paper_bgcolor='white',
                        font_color='#334155',
                        title_font_color='#1e293b'
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                elif chart_type == "트리맵":
                    fig = px.treemap(
                        df_top,
                        path=['연관키워드'],
                        values='총 검색량',
                        title=f"🌳 상위 {top_n}개 키워드 트리맵",
                        color='총 검색량',
                        color_continuous_scale='Greens'
                    )
                    fig.update_layout(
                        plot_bgcolor='white',
                        paper_bgcolor='white',
                        font_color='#334155',
                        title_font_color='#1e293b'
                    )
                    st.plotly_chart(fig, use_container_width=True)
        
        with chart_col2:
            # PC vs 모바일 비교 차트
            if 'PC 검색량' in df_display.columns and '모바일 검색량' in df_display.columns:
                df_top = df_display.nlargest(10, '총 검색량')
                
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    name='PC',
                    x=df_top['연관키워드'],
                    y=df_top['PC 검색량'],
                    marker_color='#00c73c'
                ))
                fig.add_trace(go.Bar(
                    name='모바일',
                    x=df_top['연관키워드'],
                    y=df_top['모바일 검색량'],
                    marker_color='#00a032'
                ))
                
                fig.update_layout(
                    title='📱 PC vs 모바일 검색량 비교 (상위 10개)',
                    barmode='group',
                    plot_bgcolor='white',
                    paper_bgcolor='white',
                    font_color='#334155',
                    title_font_color='#1e293b',
                    xaxis_tickangle=-45,
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    )
                )
                st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        # 데이터 테이블
        st.markdown("### 📋 상세 데이터")
        
        # 필터링 옵션
        filter_col1, filter_col2, filter_col3 = st.columns(3)
        
        with filter_col1:
            if '총 검색량' in df_display.columns:
                min_search = st.number_input("최소 검색량", min_value=0, value=0)
        
        with filter_col2:
            sort_by = st.selectbox("정렬 기준", df_display.columns.tolist())
        
        with filter_col3:
            sort_order = st.selectbox("정렬 순서", ["내림차순", "오름차순"])
        
        # 필터 적용
        df_filtered = df_display.copy()
        if '총 검색량' in df_filtered.columns and min_search > 0:
            df_filtered = df_filtered[df_filtered['총 검색량'] >= min_search]
        
        # 정렬 적용
        ascending = sort_order == "오름차순"
        df_filtered = df_filtered.sort_values(sort_by, ascending=ascending)
        
        # 데이터 표시
        st.dataframe(
            df_filtered,
            use_container_width=True,
            height=400
        )
        
        # 다운로드 버튼
        st.markdown("---")
        download_col1, download_col2, download_col3 = st.columns([1, 1, 2])
        
        # 현재 분석된 키워드 가져오기
        current_kw = st.session_state.get('current_keyword', keyword_input)
        
        with download_col1:
            csv = df_filtered.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="📥 CSV 다운로드",
                data=csv,
                file_name=f"keyword_analysis_{current_kw}.csv",
                mime="text/csv"
            )
        
        with download_col2:
            excel_buffer = df_filtered.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="📥 Excel 다운로드",
                data=excel_buffer,
                file_name=f"keyword_analysis_{current_kw}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        
        # 추가 정보 섹션 (선택사항)
        if st.session_state.related_keywords and st.session_state.get('current_keyword'):
            st.markdown("---")
            st.markdown("### 📊 분석 요약")
            
            summary_col1, summary_col2, summary_col3 = st.columns(3)
            
            with summary_col1:
                st.info(f"**현재 분석 키워드**\n\n🎯 {st.session_state.get('current_keyword', keyword_input)}")
            
            with summary_col2:
                st.success(f"**발견된 연관검색어**\n\n🔗 {len(st.session_state.related_keywords)}개")
            
            with summary_col3:
                st.warning(f"**API 분석 결과**\n\n📈 {len(df_filtered)}개 키워드")
    
    else:
        # 안내 메시지
        st.markdown("""
        <div style="text-align: center; padding: 3rem;">
            <h2 style="color: #1e293b;">👆 키워드를 입력하고 분석을 시작하세요</h2>
            <p style="color: #64748b; font-size: 1.1rem;">네이버 검색광고 API를 활용하여 키워드의 월간 검색량, 경쟁도 등을 분석합니다.</p>
            <br>
            <div style="display: flex; justify-content: center; gap: 2rem; flex-wrap: wrap;">
                <div style="background: white; padding: 1.5rem 2rem; border-radius: 16px; border: 1px solid #e2e8f0; box-shadow: 0 4px 12px rgba(0,0,0,0.08);">
                    <h3 style="color: #00a032; margin-bottom: 0.5rem;">🔍 검색량 분석</h3>
                    <p style="color: #64748b; margin: 0;">PC와 모바일 월간 검색량 확인</p>
                </div>
                <div style="background: white; padding: 1.5rem 2rem; border-radius: 16px; border: 1px solid #e2e8f0; box-shadow: 0 4px 12px rgba(0,0,0,0.08);">
                    <h3 style="color: #00a032; margin-bottom: 0.5rem;">📊 시각화</h3>
                    <p style="color: #64748b; margin: 0;">다양한 차트로 데이터 시각화</p>
                </div>
                <div style="background: white; padding: 1.5rem 2rem; border-radius: 16px; border: 1px solid #e2e8f0; box-shadow: 0 4px 12px rgba(0,0,0,0.08);">
                    <h3 style="color: #00a032; margin-bottom: 0.5rem;">📥 내보내기</h3>
                    <p style="color: #64748b; margin: 0;">CSV, Excel 형식으로 다운로드</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)


# ==================== 페이지: 통합검색 트렌드 ====================

def trend_analysis_page():
    """통합검색 트렌드 분석 페이지"""
    # 헤더
    st.markdown('<h1 class="main-header">📈 네이버 통합검색 트렌드 분석</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">네이버 DataLab API를 활용한 검색 트렌드 분석</p>', unsafe_allow_html=True)
    
    # 사이드바 - API 설정
    with st.sidebar:
        st.markdown("### ⚙️ DataLab API 설정")
        st.markdown("---")
        
        client_id = st.text_input(
            "Client ID",
            value="0BSBBSMbwWik9xyQuW82",
            type="password",
            key="trend_client_id"
        )
        
        client_secret = st.text_input(
            "Client Secret",
            value="sfGGSl_E82",
            type="password",
            key="trend_client_secret"
        )
        
        st.markdown("---")
        st.markdown("### 📅 기간 설정")
        
        # 기본 날짜 설정 (최근 1년)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
        
        col1, col2 = st.columns(2)
        with col1:
            start = st.date_input(
                "시작일",
                value=start_date,
                key="trend_start_date"
            )
        with col2:
            end = st.date_input(
                "종료일",
                value=end_date,
                key="trend_end_date"
            )
        
        time_unit = st.selectbox(
            "시간 단위",
            ["date", "week", "month"],
            format_func=lambda x: {"date": "일별", "week": "주별", "month": "월별"}[x]
        )
        
        st.markdown("---")
        st.markdown("### 🔧 필터 옵션")
        
        device = st.selectbox(
            "디바이스",
            ["", "pc", "mo"],
            format_func=lambda x: {"": "전체", "pc": "PC", "mo": "모바일"}[x]
        )
        
        gender = st.selectbox(
            "성별",
            ["", "m", "f"],
            format_func=lambda x: {"": "전체", "m": "남성", "f": "여성"}[x]
        )
        
        # 연령대 선택 (다중 선택)
        age_options = {
            "1": "0~12세",
            "2": "13~18세",
            "3": "19~24세",
            "4": "25~29세",
            "5": "30~34세",
            "6": "35~39세",
            "7": "40~44세",
            "8": "45~49세",
            "9": "50~54세",
            "10": "55~59세",
            "11": "60세 이상"
        }
        
        selected_ages = st.multiselect(
            "연령대",
            options=list(age_options.keys()),
            format_func=lambda x: age_options[x]
        )
        
        st.markdown("---")
        st.markdown("""
        <div style="color: #475569; font-size: 0.85rem; background: #f1f5f9; padding: 1rem; border-radius: 8px;">
        <strong style="color: #1e293b;">💡 사용 방법</strong><br><br>
        1. 비교할 키워드 그룹 추가<br>
        2. 기간 및 필터 설정<br>
        3. 분석 시작 버튼 클릭<br>
        4. 트렌드 차트 확인
        </div>
        """, unsafe_allow_html=True)
    
    # 메인 컨텐츠
    st.markdown("### 🔑 키워드 그룹 설정")
    st.info("💡 최대 5개의 키워드 그룹을 비교할 수 있으며, 각 그룹당 최대 20개의 키워드를 입력할 수 있습니다.")
    
    # 세션 상태 초기화
    if 'keyword_groups' not in st.session_state:
        st.session_state.keyword_groups = [
            {"groupName": "", "keywords": []}
        ]
    
    # 키워드 그룹 입력
    for idx, group in enumerate(st.session_state.keyword_groups):
        with st.expander(f"📦 키워드 그룹 {idx + 1}", expanded=True):
            col1, col2 = st.columns([1, 3])
            
            with col1:
                group_name = st.text_input(
                    "그룹명",
                    value=group.get("groupName", ""),
                    key=f"group_name_{idx}",
                    placeholder="예: 스마트폰"
                )
            
            with col2:
                keywords_input = st.text_input(
                    "키워드 (쉼표로 구분)",
                    value=", ".join(group.get("keywords", [])),
                    key=f"keywords_{idx}",
                    placeholder="예: 갤럭시, 아이폰, 샤오미"
                )
            
            # 그룹 데이터 업데이트
            st.session_state.keyword_groups[idx] = {
                "groupName": group_name,
                "keywords": [kw.strip() for kw in keywords_input.split(",") if kw.strip()]
            }
            
            # 그룹 삭제 버튼 (첫 번째 그룹은 삭제 불가)
            if idx > 0:
                if st.button(f"🗑️ 그룹 {idx + 1} 삭제", key=f"delete_{idx}"):
                    st.session_state.keyword_groups.pop(idx)
                    st.rerun()
    
    # 그룹 추가 버튼
    col_add, col_analyze = st.columns([1, 4])
    
    with col_add:
        if len(st.session_state.keyword_groups) < 5:
            if st.button("➕ 그룹 추가"):
                st.session_state.keyword_groups.append({"groupName": "", "keywords": []})
                st.rerun()
    
    with col_analyze:
        analyze_button = st.button("🚀 트렌드 분석 시작", type="primary", use_container_width=True)
    
    # 분석 실행
    if analyze_button:
        # 유효성 검사
        valid_groups = [g for g in st.session_state.keyword_groups if g["groupName"] and g["keywords"]]
        
        if not valid_groups:
            st.error("❌ 최소 1개 이상의 키워드 그룹을 입력해주세요.")
        else:
            # 날짜 포맷 변환
            start_date_str = start.strftime("%Y-%m-%d")
            end_date_str = end.strftime("%Y-%m-%d")
            
            with st.spinner("🔄 트렌드 데이터 분석 중..."):
                result, error = get_trend_data(
                    client_id,
                    client_secret,
                    valid_groups,
                    start_date_str,
                    end_date_str,
                    time_unit,
                    device,
                    selected_ages,
                    gender
                )
                
                if error:
                    st.error(f"❌ {error}")
                elif result:
                    st.session_state.trend_result = result
                    st.success(f"✅ {len(valid_groups)}개 키워드 그룹의 트렌드 데이터를 가져왔습니다!")
    
    # 결과 표시
    if 'trend_result' in st.session_state and st.session_state.trend_result:
        result = st.session_state.trend_result
        
        st.markdown("---")
        st.markdown("### 📊 트렌드 분석 결과")
        
        # 데이터 가공
        all_data = []
        for item in result.get('results', []):
            group_name = item['title']
            for data_point in item['data']:
                all_data.append({
                    '그룹': group_name,
                    '날짜': data_point['period'],
                    '검색 비율': data_point['ratio']
                })
        
        df_trend = pd.DataFrame(all_data)
        df_trend['날짜'] = pd.to_datetime(df_trend['날짜'])
        
        # 트렌드 차트
        fig = px.line(
            df_trend,
            x='날짜',
            y='검색 비율',
            color='그룹',
            title='🔍 키워드 그룹별 검색 트렌드',
            markers=True
        )
        
        fig.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            font_color='#334155',
            title_font_color='#1e293b',
            hovermode='x unified',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # 통계 정보
        st.markdown("### 📈 주요 통계")
        
        stat_cols = st.columns(len(result.get('results', [])))
        
        for idx, item in enumerate(result.get('results', [])):
            with stat_cols[idx]:
                ratios = [d['ratio'] for d in item['data']]
                avg_ratio = sum(ratios) / len(ratios)
                max_ratio = max(ratios)
                min_ratio = min(ratios)
                
                st.markdown(f"""
                <div style="background: white; padding: 1rem; border-radius: 12px; border: 1px solid #e2e8f0;">
                    <h4 style="color: #00a032; margin-bottom: 0.5rem;">{item['title']}</h4>
                    <p style="color: #64748b; font-size: 0.9rem; margin: 0.25rem 0;">평균: <strong>{avg_ratio:.1f}</strong></p>
                    <p style="color: #64748b; font-size: 0.9rem; margin: 0.25rem 0;">최대: <strong>{max_ratio:.1f}</strong></p>
                    <p style="color: #64748b; font-size: 0.9rem; margin: 0.25rem 0;">최소: <strong>{min_ratio:.1f}</strong></p>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # 데이터 테이블
        st.markdown("### 📋 상세 데이터")
        
        # 피벗 테이블 생성 (중복 처리를 위해 pivot_table 사용)
        df_pivot = df_trend.pivot_table(index='날짜', columns='그룹', values='검색 비율', aggfunc='first')
        df_pivot = df_pivot.reset_index()
        
        st.dataframe(
            df_pivot,
            use_container_width=True,
            height=400
        )
        
        # 다운로드 버튼
        st.markdown("---")
        download_col1, download_col2 = st.columns([1, 4])
        
        with download_col1:
            csv = df_trend.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="📥 CSV 다운로드",
                data=csv,
                file_name=f"trend_analysis_{start.strftime('%Y%m%d')}_{end.strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )


# ==================== 페이지: 블로그 순위 조회 ====================

def blog_rank_page():
    """블로그 순위 조회 페이지"""
    # 헤더
    st.markdown('<h1 class="main-header">📝 네이버 블로그 순위 조회</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">네이버 검색 API 또는 Selenium을 활용한 블로그 검색 순위 확인</p>', unsafe_allow_html=True)
    
    # 탭 생성
    tab1, tab2 = st.tabs(["📊 API 방식 (빠름)", "🔍 Selenium 방식 (정확함)"])
    
    with tab1:
        blog_rank_api_tab()
    
    with tab2:
        blog_rank_selenium_tab()


def blog_rank_api_tab():
    """API 방식 블로그 순위 조회"""
    
    # 사이드바 - API 설정
    with st.sidebar:
        st.markdown("### ⚙️ 블로그 검색 API 설정")
        st.markdown("---")
        
        client_id = st.text_input(
            "Client ID",
            value="0BSBBSMbwWik9xyQuW82",
            type="password",
            key="blog_client_id"
        )
        
        client_secret = st.text_input(
            "Client Secret",
            value="sfGGSl_E82",
            type="password",
            key="blog_client_secret"
        )
        
        st.markdown("---")
        st.markdown("### 🔧 검색 옵션")
        
        sort_option = st.selectbox(
            "정렬 기준",
            ["sim", "date"],
            format_func=lambda x: {"sim": "정확도순", "date": "최신순"}[x]
        )
        
        max_results = st.selectbox(
            "검색 결과 수",
            [100, 200, 300, 400, 500],
            index=1,
            help="더 많은 결과를 검색할수록 시간이 오래 걸립니다"
        )
        
        st.markdown("---")
        st.markdown("""
        <div style="color: #475569; font-size: 0.85rem; background: #f1f5f9; padding: 1rem; border-radius: 8px;">
        <strong style="color: #1e293b;">💡 사용 방법</strong><br><br>
        1. 검색어 입력<br>
        2. 내 블로그 이름 입력<br>
        3. 순위 조회 버튼 클릭<br>
        4. 결과 확인
        </div>
        """, unsafe_allow_html=True)
    
    # 메인 컨텐츠
    st.markdown("### 🔍 검색 설정")
    
    col1, col2 = st.columns(2)
    
    with col1:
        search_query = st.text_input(
            "검색어",
            placeholder="예: 맛집, 여행, 리뷰 등",
            key="blog_search_query"
        )
    
    with col2:
        my_blog_name = st.text_input(
            "내 블로그 이름",
            placeholder="블로그 이름을 정확히 입력하세요",
            key="my_blog_name"
        )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    search_button = st.button("🚀 순위 조회", type="primary", use_container_width=True)
    
    # 검색 실행
    if search_button:
        if not search_query:
            st.error("❌ 검색어를 입력해주세요.")
        elif not my_blog_name:
            st.error("❌ 내 블로그 이름을 입력해주세요.")
        else:
            with st.spinner(f"🔄 '{search_query}' 검색 중... (최대 {max_results}개 결과)"):
                result_all = pd.DataFrame()
                num_requests = max_results // 100
                
                progress_bar = st.progress(0)
                
                for i in range(num_requests):
                    start = 1 + 100 * i
                    df_result, error = get_blog_search_result(
                        client_id,
                        client_secret,
                        search_query,
                        display=100,
                        start=start,
                        sort=sort_option
                    )
                    
                    if error:
                        st.error(f"❌ {error}")
                        break
                    elif df_result is not None and not df_result.empty:
                        result_all = pd.concat([result_all, df_result], ignore_index=True)
                    
                    progress_bar.progress((i + 1) / num_requests)
                
                progress_bar.empty()
                
                if not result_all.empty:
                    st.session_state.blog_result = result_all
                    st.session_state.blog_query = search_query
                    st.session_state.my_blog = my_blog_name
                    
                    # 내 블로그 순위 찾기
                    rank = None
                    for index, row in result_all.iterrows():
                        bloggername = row.get('bloggername', '')
                        if my_blog_name == bloggername:
                            rank = index + 1
                            break
                    
                    st.session_state.blog_rank = rank
                    
                    st.success(f"✅ {len(result_all)}개의 블로그 검색 결과를 가져왔습니다!")
    
    # 결과 표시
    if 'blog_result' in st.session_state and st.session_state.blog_result is not None:
        result_all = st.session_state.blog_result
        rank = st.session_state.get('blog_rank')
        search_query = st.session_state.get('blog_query', '')
        my_blog_name = st.session_state.get('my_blog', '')
        
        st.markdown("---")
        
        # 순위 결과 표시
        if rank:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%); padding: 2rem; border-radius: 16px; border: 2px solid #00a032; text-align: center; margin: 2rem 0;">
                <h2 style="color: #1e293b; margin-bottom: 1rem;">🎉 블로그 순위 확인!</h2>
                <p style="color: #475569; font-size: 1.2rem; margin-bottom: 0.5rem;">검색어: <strong style="color: #00a032;">"{search_query}"</strong></p>
                <p style="color: #475569; font-size: 1.2rem; margin-bottom: 1rem;">블로그: <strong style="color: #00a032;">{my_blog_name}</strong></p>
                <div style="background: white; padding: 1.5rem; border-radius: 12px; display: inline-block;">
                    <p style="color: #64748b; font-size: 1rem; margin: 0;">현재 순위</p>
                    <p style="color: #00a032; font-size: 3rem; font-weight: 700; margin: 0.5rem 0;">{rank}위</p>
                    <p style="color: #64748b; font-size: 0.9rem; margin: 0;">전체 {len(result_all)}개 중</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%); padding: 2rem; border-radius: 16px; border: 2px solid #ff9800; text-align: center; margin: 2rem 0;">
                <h2 style="color: #1e293b; margin-bottom: 1rem;">⚠️ 블로그를 찾을 수 없습니다</h2>
                <p style="color: #475569; font-size: 1.1rem; margin-bottom: 0.5rem;">검색어: <strong>"{search_query}"</strong></p>
                <p style="color: #475569; font-size: 1.1rem; margin-bottom: 1rem;">블로그: <strong>{my_blog_name}</strong></p>
                <p style="color: #64748b;">현재 검색 결과 <strong>{len(result_all)}개</strong> 내에서 블로그를 찾을 수 없습니다.</p>
                <p style="color: #64748b; font-size: 0.9rem; margin-top: 0.5rem;">• 블로그 이름을 정확히 입력했는지 확인해주세요<br>• 검색 결과 수를 늘려보세요<br>• 다른 검색어로 시도해보세요</p>
            </div>
            """, unsafe_allow_html=True)
        
        # 통계 정보
        st.markdown("### 📊 검색 결과 통계")
        
        stat_cols = st.columns(4)
        
        with stat_cols[0]:
            st.metric("총 검색 결과", f"{len(result_all)}개")
        
        with stat_cols[1]:
            if rank:
                st.metric("내 순위", f"{rank}위")
            else:
                st.metric("내 순위", "순위권 밖")
        
        with stat_cols[2]:
            if rank:
                percentile = (1 - (rank / len(result_all))) * 100
                st.metric("상위 비율", f"{percentile:.1f}%")
            else:
                st.metric("상위 비율", "-")
        
        with stat_cols[3]:
            unique_bloggers = result_all['bloggername'].nunique()
            st.metric("블로거 수", f"{unique_bloggers}명")
        
        st.markdown("---")
        
        # 상위 10개 블로그 목록
        st.markdown("### 🏆 상위 10개 블로그")
        
        top_10 = result_all.head(10).copy()
        top_10['순위'] = range(1, len(top_10) + 1)
        
        # 내 블로그 하이라이트
        if rank and rank <= 10:
            top_10['내 블로그'] = top_10['bloggername'] == my_blog_name
        
        # 표시할 컬럼 선택
        display_columns = ['순위', 'title', 'bloggername', 'postdate']
        if 'bloggername' in top_10.columns:
            top_10_display = top_10[display_columns].copy()
            top_10_display.columns = ['순위', '제목', '블로거', '작성일']
            
            # 데이터프레임 표시
            st.dataframe(
                top_10_display,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "순위": st.column_config.NumberColumn(
                        "순위",
                        width="small",
                    ),
                    "제목": st.column_config.TextColumn(
                        "제목",
                        width="large",
                    ),
                    "블로거": st.column_config.TextColumn(
                        "블로거",
                        width="medium",
                    ),
                    "작성일": st.column_config.TextColumn(
                        "작성일",
                        width="small",
                    ),
                }
            )
        
        st.markdown("---")
        
        # 전체 결과 테이블
        st.markdown("### 📋 전체 검색 결과")
        
        # 필터링 옵션
        col_filter1, col_filter2 = st.columns(2)
        
        with col_filter1:
            filter_blogger = st.text_input("블로거 이름 필터", placeholder="특정 블로거 검색", key="filter_blogger")
        
        with col_filter2:
            filter_title = st.text_input("제목 필터", placeholder="제목에 포함된 단어 검색", key="filter_title")
        
        # 필터 적용
        df_filtered = result_all.copy()
        df_filtered['순위'] = range(1, len(df_filtered) + 1)
        
        if filter_blogger:
            df_filtered = df_filtered[df_filtered['bloggername'].str.contains(filter_blogger, na=False, case=False)]
        
        if filter_title:
            df_filtered = df_filtered[df_filtered['title'].str.contains(filter_title, na=False, case=False)]
        
        # 순위 재계산
        df_filtered = df_filtered.reset_index(drop=True)
        
        # 표시할 컬럼
        display_cols = ['순위', 'title', 'bloggername', 'postdate', 'link']
        df_display = df_filtered[display_cols].copy()
        df_display.columns = ['순위', '제목', '블로거', '작성일', '링크']
        
        st.dataframe(
            df_display,
            use_container_width=True,
            hide_index=True,
            height=400,
            column_config={
                "순위": st.column_config.NumberColumn("순위", width="small"),
                "제목": st.column_config.TextColumn("제목", width="large"),
                "블로거": st.column_config.TextColumn("블로거", width="medium"),
                "작성일": st.column_config.TextColumn("작성일", width="small"),
                "링크": st.column_config.LinkColumn("링크", width="small"),
            }
        )
        
        # 다운로드 버튼
        st.markdown("---")
        download_col1, download_col2 = st.columns([1, 4])
        
        with download_col1:
            csv = df_display.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="📥 CSV 다운로드",
                data=csv,
                file_name=f"blog_rank_{search_query}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    
    else:
        # 안내 메시지
        st.markdown("""
        <div style="text-align: center; padding: 3rem;">
            <h2 style="color: #1e293b;">👆 검색어와 블로그 이름을 입력하고 순위를 조회하세요</h2>
            <p style="color: #64748b; font-size: 1.1rem;">네이버 검색 API를 활용하여 블로그 검색 순위를 확인합니다.</p>
            <br>
            <div style="display: flex; justify-content: center; gap: 2rem; flex-wrap: wrap;">
                <div style="background: white; padding: 1.5rem 2rem; border-radius: 16px; border: 1px solid #e2e8f0; box-shadow: 0 4px 12px rgba(0,0,0,0.08);">
                    <h3 style="color: #00a032; margin-bottom: 0.5rem;">🔍 순위 확인</h3>
                    <p style="color: #64748b; margin: 0;">내 블로그의 검색 순위 조회</p>
                </div>
                <div style="background: white; padding: 1.5rem 2rem; border-radius: 16px; border: 1px solid #e2e8f0; box-shadow: 0 4px 12px rgba(0,0,0,0.08);">
                    <h3 style="color: #00a032; margin-bottom: 0.5rem;">📊 경쟁 분석</h3>
                    <p style="color: #64748b; margin: 0;">상위 블로그 목록 확인</p>
                </div>
                <div style="background: white; padding: 1.5rem 2rem; border-radius: 16px; border: 1px solid #e2e8f0; box-shadow: 0 4px 12px rgba(0,0,0,0.08);">
                    <h3 style="color: #00a032; margin-bottom: 0.5rem;">📥 내보내기</h3>
                    <p style="color: #64748b; margin: 0;">CSV 형식으로 다운로드</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)


def blog_rank_selenium_tab():
    """Selenium 방식 블로그 순위 조회"""
    
    st.info("💡 **Selenium 방식**: 실제 네이버 검색 결과 페이지를 크롤링하여 정확한 순위를 확인합니다. API 방식보다 느리지만 더 정확합니다.")
    
    # 메인 컨텐츠
    st.markdown("### 🔍 검색 설정")
    
    # 단일 검색과 다중 검색 선택
    search_type = st.radio(
        "검색 유형",
        ["단일 검색", "다중 검색"],
        horizontal=True
    )
    
    if search_type == "단일 검색":
        col1, col2 = st.columns(2)
        
        with col1:
            search_query = st.text_input(
                "검색어",
                placeholder="예: python flask",
                key="selenium_search_query"
            )
        
        with col2:
            target_blog_link = st.text_input(
                "내 블로그 글 전체 URL",
                placeholder="https://blog.naver.com/사용자아이디/글번호",
                key="selenium_blog_link"
            )
        
        max_scroll = st.slider(
            "최대 스크롤 횟수",
            min_value=3,
            max_value=10,
            value=7,
            help="스크롤 횟수가 많을수록 더 많은 결과를 확인하지만 시간이 오래 걸립니다"
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        search_button = st.button("🚀 순위 조회", type="primary", use_container_width=True, key="selenium_single_search")
        
        if search_button:
            if not search_query:
                st.error("❌ 검색어를 입력해주세요.")
            elif not target_blog_link:
                st.error("❌ 블로그 글 URL을 입력해주세요.")
            else:
                progress_container = st.empty()
                status_container = st.empty()
                
                def update_progress(value, text):
                    progress_container.progress(value)
                    status_container.info(text)
                
                with st.spinner("🔄 Selenium을 사용하여 순위를 조회 중입니다..."):
                    rank, error = get_blog_rank_selenium(
                        search_query,
                        target_blog_link,
                        max_scroll,
                        update_progress
                    )
                    
                    progress_container.empty()
                    status_container.empty()
                    
                    if error:
                        st.error(f"❌ {error}")
                    elif rank:
                        st.session_state.selenium_result = {
                            'query': search_query,
                            'url': target_blog_link,
                            'rank': rank
                        }
                        st.success(f"✅ 순위 조회 완료!")
                    else:
                        st.warning(f"⚠️ {max_scroll}번 스크롤했지만 블로그를 찾을 수 없습니다. 순위권 밖이거나 URL이 정확하지 않을 수 있습니다.")
        
        # 결과 표시
        if 'selenium_result' in st.session_state:
            result = st.session_state.selenium_result
            
            st.markdown("---")
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%); padding: 2rem; border-radius: 16px; border: 2px solid #00a032; text-align: center; margin: 2rem 0;">
                <h2 style="color: #1e293b; margin-bottom: 1rem;">🎉 블로그 순위 확인!</h2>
                <p style="color: #475569; font-size: 1.2rem; margin-bottom: 0.5rem;">검색어: <strong style="color: #00a032;">"{result['query']}"</strong></p>
                <p style="color: #475569; font-size: 0.9rem; margin-bottom: 1rem; word-break: break-all;">URL: {result['url']}</p>
                <div style="background: white; padding: 1.5rem; border-radius: 12px; display: inline-block;">
                    <p style="color: #64748b; font-size: 1rem; margin: 0;">현재 순위</p>
                    <p style="color: #00a032; font-size: 3rem; font-weight: 700; margin: 0.5rem 0;">{result['rank']}위</p>
                    <p style="color: #64748b; font-size: 0.9rem; margin: 0;">네이버 VIEW 탭 기준</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    else:  # 다중 검색
        st.markdown("#### 📋 여러 키워드에 대한 순위를 한 번에 조회")
        
        # 세션 상태 초기화
        if 'selenium_queries' not in st.session_state:
            st.session_state.selenium_queries = []
        
        # 키워드와 URL 입력
        col1, col2, col3 = st.columns([2, 3, 1])
        
        with col1:
            new_query = st.text_input("검색어", placeholder="예: python flask", key="new_query")
        
        with col2:
            new_url = st.text_input("블로그 URL", placeholder="https://blog.naver.com/...", key="new_url")
        
        with col3:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("➕ 추가"):
                if new_query and new_url:
                    st.session_state.selenium_queries.append({
                        'query': new_query,
                        'url': new_url
                    })
                    st.rerun()
        
        # 추가된 키워드 목록 표시
        if st.session_state.selenium_queries:
            st.markdown("---")
            st.markdown("#### 📝 조회할 목록")
            
            for idx, item in enumerate(st.session_state.selenium_queries):
                col1, col2, col3 = st.columns([1, 2, 3])
                
                with col1:
                    st.write(f"**{idx + 1}.**")
                
                with col2:
                    st.write(f"🔍 {item['query']}")
                
                with col3:
                    if st.button(f"🗑️ 삭제", key=f"delete_{idx}"):
                        st.session_state.selenium_queries.pop(idx)
                        st.rerun()
            
            max_scroll = st.slider(
                "최대 스크롤 횟수",
                min_value=3,
                max_value=10,
                value=7,
                help="스크롤 횟수가 많을수록 더 많은 결과를 확인하지만 시간이 오래 걸립니다",
                key="multi_max_scroll"
            )
            
            st.markdown("<br>", unsafe_allow_html=True)
            search_button = st.button("🚀 전체 순위 조회", type="primary", use_container_width=True, key="selenium_multi_search")
            
            if search_button:
                search_queries = [item['query'] for item in st.session_state.selenium_queries]
                target_urls = [item['url'] for item in st.session_state.selenium_queries]
                
                progress_container = st.empty()
                status_container = st.empty()
                
                def update_progress(value, text):
                    progress_container.progress(value)
                    status_container.info(text)
                
                with st.spinner("🔄 여러 키워드의 순위를 조회 중입니다... (시간이 오래 걸릴 수 있습니다)"):
                    df_result, error = get_multiple_blog_ranks_selenium(
                        search_queries,
                        target_urls,
                        max_scroll,
                        update_progress
                    )
                    
                    progress_container.empty()
                    status_container.empty()
                    
                    if error:
                        st.error(f"❌ {error}")
                    elif df_result is not None:
                        st.session_state.selenium_multi_result = df_result
                        st.success(f"✅ {len(df_result)}개 키워드의 순위 조회 완료!")
            
            # 결과 표시
            if 'selenium_multi_result' in st.session_state:
                df_result = st.session_state.selenium_multi_result
                
                st.markdown("---")
                st.markdown("### 📊 조회 결과")
                
                # 통계 정보
                stat_cols = st.columns(3)
                
                with stat_cols[0]:
                    total = len(df_result)
                    st.metric("총 조회 수", f"{total}개")
                
                with stat_cols[1]:
                    success = len(df_result[df_result['상태'] == '성공'])
                    st.metric("성공", f"{success}개")
                
                with stat_cols[2]:
                    failed = total - success
                    st.metric("실패/순위권 밖", f"{failed}개")
                
                st.markdown("---")
                
                # 결과 테이블
                st.dataframe(
                    df_result,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "검색어": st.column_config.TextColumn("검색어", width="medium"),
                        "URL": st.column_config.TextColumn("URL", width="large"),
                        "순위": st.column_config.TextColumn("순위", width="small"),
                        "상태": st.column_config.TextColumn("상태", width="small"),
                    },
                    height=400
                )
                
                # 다운로드 버튼
                st.markdown("---")
                csv = df_result.to_csv(index=False, encoding='utf-8-sig')
                st.download_button(
                    label="📥 CSV 다운로드",
                    data=csv,
                    file_name=f"blog_rank_selenium_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )


# ==================== 메인 함수 ====================

def main():
    # 사이드바 메뉴
    with st.sidebar:
        st.markdown("## 🔍 메뉴")
        page = st.radio(
            "분석 도구 선택",
            ["키워드 검색량 분석", "통합검색 트렌드 분석", "블로그 순위 조회"],
            label_visibility="collapsed"
        )
        st.markdown("---")
    
    # 페이지 라우팅
    if page == "키워드 검색량 분석":
        keyword_analysis_page()
    elif page == "통합검색 트렌드 분석":
        trend_analysis_page()
    elif page == "블로그 순위 조회":
        blog_rank_page()


if __name__ == "__main__":
    main()
