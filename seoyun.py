import streamlit as st
from openai import OpenAI
from datetime import datetime, timedelta, date
import os
import csv
import numpy as np

# ==========================================
# 1. 🌐 웹페이지 기본 구성 및 모바일 레이아웃 정의
# ==========================================
st.set_page_config(
    page_title="서연중학교 AI 안내 센터",
    page_icon="🏫",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 🔑 OpenAI API 키 환경변수 보안 적용
try:
    MY_OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
except Exception:
    st.error("Streamlit Secrets에 'OPENAI_API_KEY'가 설정되지 않았습니다.")
    st.stop()

client = OpenAI(api_key=MY_OPENAI_API_KEY)

# 🎨 레이아웃 미세 조정 및 최적화 스타일시트
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap');

        html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
            max-width: 100vw !important;
            overflow-x: hidden !important;
            box-sizing: border-box !important;
            -webkit-text-size-adjust: none !important;
            text-size-adjust: none !important;
        }
        
        [data-testid="stToolbar"], [data-testid="stDecoration"], #MainMenu, footer {
            display: none !important;
            visibility: hidden !important;
            height: 0 !important;
        }

        .block-container {
            padding-top: 1.5rem !important;
            padding-bottom: 3rem !important;
            padding-left: 16px !important;
            padding-right: 16px !important;
            max-width: 100% !important;
        }

        .stApp, .title-section-container, .premium-card {
            font-family: 'Noto Sans KR', sans-serif !important;
        }

        .title-section-container { 
            padding: 24px 20px; 
            border-radius: 18px; 
            background: linear-gradient(135deg, #FFFDFB 0%, #FFF3F3 100%) !important;
            border: 1px solid #FFD8D8;
            box-shadow: 0 6px 20px rgba(255, 107, 107, 0.04); 
            margin-bottom: 20px; 
            text-align: left; 
        }
        .title-text { 
            background: linear-gradient(135deg, #FF4B4B, #FF6B2B); 
            -webkit-background-clip: text; 
            -webkit-text-fill-color: transparent; 
            font-size: 1.6rem !important; 
            font-weight: 900 !important; 
            margin: 0; 
            letter-spacing: -1px; 
            line-height: 1.2;
        }
        .subtitle-text { 
            color: #555555 !important;
            font-size: 0.88rem !important; 
            font-weight: 500 !important; 
            margin-top: 8px; 
            margin-bottom: 0; 
            word-break: keep-all; 
            line-height: 1.4;
        }

        .premium-card { 
            padding: 20px 18px; 
            background: #FFFFFF !important;
            border-radius: 16px; 
            border: 1px solid #EAEAEA; 
            box-shadow: 0 4px 16px rgba(0,0,0,0.015); 
            margin-bottom: 20px; 
        }
        .card-title { 
            font-size: 1rem; 
            font-weight: 700; 
            color: #111111 !important;
            margin-top: 0; 
            margin-bottom: 12px; 
            display: flex; 
            align-items: center; 
            gap: 8px; 
        }
        .card-content { 
            font-size: 0.88rem; 
            line-height: 1.6; 
            color: #444444 !important;
            margin: 0; 
            word-break: keep-all;
        }
        
        .card-highlight { 
            color: #FF4B4B !important; 
            font-weight: 600; 
            background: #FFF2F2 !important;
            padding: 6px 14px;
            border-radius: 20px;
            display: inline-block; 
            margin: 5px 3px;
            font-size: 0.82rem;
            border: 1px solid #FFD5D5;
            touch-action: manipulation;
        }

        div.stButton > button {
            width: 100% !important;
            padding: 10px 16px !important;
            font-size: 0.95rem !important;
            font-weight: 600 !important;
            border-radius: 10px !important;
        }

        div[data-testid="stChatInput"] textarea {
            min-height: 42px !important;
            height: 42px !important;
            font-size: 0.95rem !important;
        }

        .sidebar-custom-box {
            background: linear-gradient(135deg, #FFF0F0 0%, #FFE3E3 100%) !important; 
            border-radius: 12px; 
            padding: 12px; 
            border: 1px solid #FFAFAF; 
        }

        @media (min-width: 768px) {
            .block-container { padding: 2.5rem 6rem !important; }
            .title-section-container { padding: 28px 36px; text-align: center; }
            .title-text { font-size: 2.3rem !important; }
            .subtitle-text { font-size: 1.05rem !important; }
            .premium-card { padding: 22px 26px; }
        }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 📂 데이터 로드 및 RAG 엔진
# ==========================================
@st.cache_resource
def DEEP_INITIALIZE_RAG_ENGINE():
    rule_path = "seoyeon_chatbot_data.csv"
    lunch_path = "seoyeon_lunch_data.csv"
    embed_cache_path = "seoyeon_embeddings.npy"

    if os.path.exists(rule_path): os.remove(rule_path)
    if os.path.exists(lunch_path): os.remove(lunch_path)
    if os.path.exists(embed_cache_path): os.remove(embed_cache_path)

    rules = [
        ["카테고리", "학칙 및 규정 내용"],
        ["등교 시간 및 지각", "아침 오전 8시 50분까지 교실에 입실 완료해야 합니다. 8시 50분이 지나면 지각 처리됩니다."],
        ["지각 처리 인정 기준", "오전 8시 50분 이후에 교실에 들어오면 지각으로 기록됩니다. 단, 버스 지연 등의 불가피한 사유나 몸이 아픈 경우, 병원 방문 등 합당한 증빙 서류나 사유가 확인되면 인정될 수 있습니다."],
        ["무단 지각 결석", "무단 지각, 무단 결과, 무단 조퇴를 합산하여 3회가 되면 무단 결석 1회로 처리되므로 생활기록부 관리를 위해 유의해야 합니다."],
        ["질병 결석 신청", "질병으로 인해 결석할 경우, 등교 후 3일 이내에 질병결석계와 함께 의사 진단서, 소견서 또는 처방전 등 증빙 서류를 담임선생님께 제출해야 합니다."],
        ["조퇴 및 외출", "일과 중 아프거나 부득이한 사정으로 조퇴·외출을 하려면 반드시 담임선생님의 승인을 받아 '외출증/조퇴증'을 발급받은 후 경비실에 제출하고 하교해야 합니다."],
        ["복장 규정", "사복(평상복) 착용은 금지됩니다. 등교 시 교복 또는 학교 생활복, 체육복 중에서 본인이 원하는 옷을 자율적으로 선택해서 편하게 입고 오면 됩니다."],
        ["체육복 등교", "체육 수업이 없는 날을 포함하여 평일 언제든 학교 지정 체육복을 입고 등하교하는 것이 전면 허용됩니다."],
        ["교복 사복 혼용", "교복이나 체육복 위에 사복 아우터(패딩, 코트 등)를 입는 것은 허용되지만, 아우터 안에는 반드시 교복, 생활복, 체육복 중 하나를 착용해야 합니다."],
        ["두발 규정", "우리 학교 두발 규정에 대해서 명확하게 정해진 틀은 없지만, 타인에게 혐오감을 주거나 너무 과도하게 눈에 띄는 스타일, 혹은 수업에 방해가 되는 수준의 두발 상태는 제한 및 금지될 수 있습니다."],
        ["교내 화장", "우리 학교 화장 규정에 대해서는 딱히 명확하게 정해진 규칙은 없지만, 너무 과도하게 눈에 띄거나 수업 분위기에 방해가 되는 정도의 화장은 금지 및 제한될 수 있습니다."],
        ["피어싱 및 귀걸이", "귀걸이나 피어싱은 착용 가능하나, 체육 활동 시 부상 위험이 있거나 타인에게 위해를 가할 수 있는 날카롭고 과도하게 큰 장신구는 착용을 금지합니다."],
        ["전자기기 반납", "아침 조례 시간에 개인 스마트폰을 의무적으로 반납해야 하며, 종례 시간 하교 시에 돌려받습니다."],
        ["쉬는시간 스마트폰", "조례 때 스마트폰을 일괄 수거하므로 쉬는 시간이나 점심시간에도 개인 휴대폰 사용은 원칙적으로 불가능합니다."],
        ["아이패드 노트북 태블릿", "개인 태블릿PC, 노트북, 아이패드 등은 선생님들이 아침에 따로 걷지는 않습니다. 수업 중 교과 선생님이 허용해 주신 상황에서는 자유롭게 쓸 수 있습니다."],
        ["무선 이어폰 에어팟", "일과 시간 중 무선 이어폰 착용은 금지됩니다. 단, 수업 중 선생님이 허가한 시청각 학습 시에는 사용 가능합니다."],
        ["전동 킥보드 자전거 등교", "전동 킥보드나 자전거 이용 시 안전 장비를 착용하지 않거나 법적 요건을 갖추지 않은 위험한 운행은 금지됩니다."],
        ["상벌점 제도", "우리 학교는 그린마일리지(상벌점) 제도 자체가 존재하지 않습니다."],
        ["교내 흡연 금지", "교내 공공장소 및 학교 주변에서의 흡연은 학생 생활 규정에 따라 엄격히 금지됩니다."],
        ["무단 외출 금지", "점심시간이나 쉬는 시간에 교사 승인 없이 학교 정문 밖으로 나가는 것은 무단 외출로 간주됩니다."],
        ["학교 폭력 예방", "모든 형태의 학교폭력은 무관용 원칙으로 대응하며 엄중 처벌됩니다."],
        ["Wee클래스 상담실", "Wee클래스 상담실은 본관 3층에 위치해 있습니다. 담당 선생님이 부재중이실 때는 혼자 들어갈 수 없습니다."],
        ["보건실 이용 및 위치", "보건실은 본관 2층에 위치해 있으며, 몸이 아프다면 언제든지 방문하여 이용할 수 있습니다."],
        ["체육관 강당 운동장 없음", "현재 우리 학교에는 체육관과 운동장이 존재하지 않습니다. 체육 활동 시 교내 탁구장, 헬스장, 당구 시설을 주로 이용하며 학년별 외부 체육 시설(1학년 배드민턴, 2학년 볼링장, 3학년 농구장)을 이용합니다."],
        ["학생회실 위치 및 규칙", "전교 학생회실은 본관 3층에 위치해 있으며 임원이 없을 때는 기본적으로 문이 잠겨 있습니다."],
        ["급식 배식 순서 학년 반별", "기본 학년별 순서는 3학년 -> 2학년 -> 1학년 순서로 배식하며, 반별 순서는 매달 정해주는 로테이션 스케줄에 맞춥니다."],
        ["주말 급식 운영 여부", "주말 급식 운영 여부에 대해서는 주말 학사일정이나 학교 공식 공지사항 확인이 따로 필요합니다."],
        ["급식실 새치기 규정", "급식실 내에서 새치기를 하거나 일행을 끼워주는 행위는 엄격히 금지되며 맨 뒤쪽 끝으로 밀려날 수 있습니다."],
        ["동아리 활동 전일제", "동아리 활동은 목요일에 진행되며, 가끔 1교시부터 7교시까지 하루 종일 동아리 활동만 하는 전일제도 존재합니다."],
        ["동아리 신청 및 상설 동아리", "학생회나 방송부 같은 특수 상설 동아리는 한 번 들어가면 1학기와 2학기 모두 변경 없이 유지해야 합니다."],
        ["방과후 학교", "방과 후 학교 수업은 정규 수업이 모두 끝난 직후에 진행되며 가정통신문을 통해 정식 신청을 완료한 학생만 참여 가능합니다."]
    ]
    with open(rule_path, mode="w", encoding="utf-8-sig", newline="") as f:
        csv.writer(f).writerows(rules)

    lunch = [
        ["날짜", "요일", "특이사항", "메뉴"],
        ["7월 1일", "수요일", "일반식단", "강량쌀밥, 육개장, 궁중떡볶, 육원전, 백김치, 블루베리요구르트"],
        ["7월 2일", "목요일", "일반식단", "맑은미역국, 코다리조림, 배추김치, 수박 등"],
        ["7월 3일", "금요일", "일반식단", "흑미밥, 순살감자탕, 고추파스타&소스, 아삭이고추된장무침, 석박지, 망고요거트"],
        ["7월 6일", "월요일", "일반식단", "칼슘강화쌀밥, 근대된장국, 코다리무조림, 크림감자뇨끼, 오이사과초무침, 총각김치, 체리"],
        ["7월 7일", "화요일", "국 없는 날", "베트남식볶음밥, 석쇠불고기분짜, 짜조, 꼬들단무지무침, 배추김치, 레몬에이드"],
        ["7월 8일", "수요일", "일반식단", "쇠고기콩나물밥&양념간장, 참치김치찌개, 지들레닭구이, 청포묵김무침, 무말랭이김치, 아이스슈"],
        ["7월 9일", "목요일", "일반식단", "카레우동, 연두부양념장, 배추김치, 과일 등"],
        ["7월 10일", "금요일", "일반식단", "찰옥수수밥, 부대찌개, 고구마아몬드또띠아, 계란장조림, 백김치, 하우스밀감"],
        ["7월 11일", "토요일", "주말", "주말 급식 미실시 (학교 휴무입니다.)"],
        ["7월 12일", "일요일", "주말", "주말 급식 미실시 (학교 휴무입니다.)"],
        ["7월 13일", "월요일", "일반식단", "칼슘강화쌀밥, 크림스프, 목살스테이크, 양상추샐러드&블루베리드레싱, 배추김치, 스틱마늘빵"],
        ["7월 14일", "화요일", "초복", "혼합잡곡밥, 닭다리삼계탕, 찐만두, 매운어묵잡채, 석박지, 수박화채"],
        ["7월 15일", "수요일", "일반식단", "귀리밥, 생배추된장국, 매콤돼지갈비찜, 통옥수수조각피자, 콩나물무침, 열무김치, 유산균요구르트"],
        ["7월 16일", "목요일", "제헌절전야", "일반식단 제공"],
        ["7월 17일", "금요일", "제헌절", "제헌절로 인한 휴업일 (급식 없음)"],
        ["7월 20일", "월요일", "일반식단", "열무비빔밥, 연포탕, 소시지롤도그, 계란찜, 백김치, 포도"],
        ["7월 21일", "방학식", "방학식 (급식 없음)"]
    ]
    with open(lunch_path, mode="w", encoding="utf-8-sig", newline="") as f:
        csv.writer(f).writerows(lunch)

    raw_docs = []
    with open(rule_path, mode="r", encoding="utf-8-sig") as f:
        r = csv.reader(f)
        next(r)
        for row in r:
            if len(row) >= 2: raw_docs.append(f"[수정학칙] 주제: {row[0]} -> 내부규정 상세: {row[1]}")

    with open(lunch_path, mode="r", encoding="utf-8-sig") as f:
        r = csv.reader(f)
        next(r)
        for row in r:
            if len(row) >= 4: raw_docs.append(f"[식단데이터] 날짜일정: {row[0]} ({row[1]}) [{row[2]}] -> 제공메뉴: {row[3]}")

    response = client.embeddings.create(model="text-embedding-3-small", input=raw_docs)
    embeddings = np.array([d.embedding for d in response.data])
    np.save(embed_cache_path, embeddings)

    return raw_docs, embeddings

try:
    ALL_CHUNKS, EMBEDDING_MATRIX = DEEP_INITIALIZE_RAG_ENGINE()
except Exception as e:
    st.error(f"데이터 엔지니어링 로드 실패: {e}")
    st.stop()

def retrieve_relevant_context_openai(query, documents, embedding_matrix, top_n=3):
    if not documents or embedding_matrix.size == 0:
        return "", []
    try:
        q_res = client.embeddings.create(model="text-embedding-3-small", input=[query])
        q_embed = np.array(q_res.data[0].embedding)
        similarities = np.dot(embedding_matrix, q_embed)
        top_indices = similarities.argsort()[-top_n:][::-1]
        matched_chunks = [documents[i] for i in top_indices if similarities[i] > 0.15]
        return "\n".join(matched_chunks), matched_chunks
    except Exception:
        return "", []

def save_unknown_question_csv(question):
    file_path = "unknown_questions.csv"
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    exists = os.path.exists(file_path)
    with open(file_path, mode="a", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        if not exists:
            writer.writerow(["기록시간", "검토필요 질문"])
        writer.writerow([current_time, question])

# ==========================================
# 3. 📱 사이드바 메뉴 및 메인 인터페이스
# ==========================================
with st.sidebar:
    st.markdown("## 🏫 서연중 AI 가이드")
    st.caption("학생 지원 대시보드")
    st.markdown("---")
    st.markdown("""
        <div class="sidebar-custom-box">
            <p style="color: #FF4B4B; margin: 0; font-weight: 600; font-size: 0.85rem;">
                🚨 체육관과 운동장이 없으므로 탁구장, 헬스장, 당구 및 학년별 외부 체육 장소를 우선 가이드합니다.
            </p>
        </div>
    """, unsafe_allow_html=True)

st.markdown("""
    <div class="title-section-container">
        <h1 class="title-text">서연중학교 AI 안내 센터</h1>
        <p class="subtitle-text">우리 학교의 다양한 학칙 규정과 급식 일정을 안내합니다.</p>
    </div>
""", unsafe_allow_html=True)

st.markdown("""
    <div class="premium-card">
        <div class="card-title">
            <img src="https://img.icons8.com/fluency/48/sparkles.png" width="22" height="22"/>
            자주 묻는 질문 예시
        </div>
        <p class="card-content">
            궁금한 점을 아래 입력창에 검색하거나 참고해 보세요.<br><br>
            <span class="card-highlight">🍱 반별 급식 순서가 어떻게 돼?</span> 
            <span class="card-highlight">🏓 체육관 없는데 체육 어디서 해?</span> 
            <span class="card-highlight">🏃 오늘 하교 시간 언제야?</span>
        </p>
    </div>
""", unsafe_allow_html=True)

st.markdown("---")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "안녕하세요! 서연중학교 AI 안내 센터에 오신 것을 환영합니다. 학교 생활에 대해 궁금한 점을 편하게 물어보세요! 🏫"}
    ]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if "contexts" in msg and msg["contexts"]:
            with st.expander("🔍 관련 규정 근거"):
                for source in msg["contexts"]:
                    st.caption(source)

# ==========================================
# 4. 🤖 실시간 대화 추론 엔진 (정밀 학사일정)
# ==========================================
if user_input := st.chat_input("Gemini에 물어보기..."):
    with st.chat_message("user"):
        st.write(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    try:
        now = datetime.now()
        weekday_map = {0: "월요일", 1: "화요일", 2: "수요일", 3: "목요일", 4: "금요일", 5: "토요일", 6: "일요일"}
        realtime_today = f"{now.strftime('%Y년 %m월 %d일')} {weekday_map[now.weekday()]}"

        is_asking_dismissal = any(k in user_input for k in ["하교", "끝나", "몇시에", "집에가", "끝나는"])
        is_asking_lunch = any(k in user_input for k in ["급식", "식단", "메뉴", "밥", "먹어"])
        
        target_date = now
        is_asking_specific_day = False

        if "오늘" in user_input:
            target_date = now
            is_asking_specific_day = True
        elif "내일" in user_input:
            target_date = now + timedelta(days=1)
            is_asking_specific_day = True
        elif "모레" in user_input:
            target_date = now + timedelta(days=2)
            is_asking_specific_day = True
        elif "어제" in user_input:
            target_date = now - timedelta(days=1)
            is_asking_specific_day = True

        target_date_only = target_date.date()

        # 📅 학사일정 명세 세트 생성
        CLUB_DAYS = {date(2026, 8, 27), date(2026, 9, 17), date(2026, 10, 22)}
        NEXT_CLUB_DAYS = {date(2026, 9, 3), date(2026, 9, 24), date(2026, 10, 29)}

        HOLIDAYS = {
            date(2026, 10, 5), date(2026, 10, 9), date(2026, 11, 19), 
            date(2026, 11, 20), date(2026, 12, 25), date(2027, 1, 1)
        }
        
        SPECIAL_SCHEDULES = {
            date(2026, 8, 19): "2학기 개학식을 진행하는 날이야!",
            date(2026, 10, 7): "금요일 시간표로 수업을 변경해서 진행하는 날이야!",
            date(2026, 10, 20): "1,2학년은 중간고사, 3학년은 기말고사를 치르는 지필평가 기간이야! 시험 일정이 끝나면 바로 하교해.",
            date(2026, 10, 21): "1,2학년은 중간고사, 3학년은 기말고사를 치르는 지필평가 기간이야! 시험 일정이 끝나면 바로 하교해.",
            date(2026, 12, 14): "1,2학년 기말고사 시험을 보는 날이야! 시험 일정이 끝나면 바로 하교해.",
            date(2026, 12, 15): "1,2학년 기말고사 시험을 보는 날이야! 시험 일정이 끝나면 바로 하교해.",
            date(2026, 12, 30): "우리 학교 축제인 '서연제' 행사가 있는 날이야!",
            date(2027, 1, 4): "차기 학생회장 선거가 진행되는 날이야!",
            date(2027, 1, 8): "2학기 종업식을 하는 날이야!"
        }

        is_vacation = date(2026, 7, 22) <= target_date_only <= date(2026, 8, 18)
        is_chuseok = date(2026, 9, 24) <= target_date_only <= date(2026, 9, 27)

        intercepted = False
        full_response = ""
        context_tag = []

        # 🛑 예외 예측 레이어 A: 급식 일정 가로채기
        if is_asking_lunch and is_asking_specific_day:
            intercepted = True
            context_tag = ["학사일정 급식 예외 필터"]
            if target_date.weekday() in [5, 6]:
                full_response = f"질문한 날짜({target_date.strftime('%m월 %d일')})는 주말이라 급식이 없어! 주말엔 맛있는 거 챙겨 먹어. ☀️"
            elif is_vacation:
                full_response = "방학 기간(7/22 ~ 8/18)이라서 학교 급식이 운영되지 않는 시기야! 🏖️"
            elif is_chuseok:
                full_response = "추석 연휴라 학교 급식이 없어! 맛있는 명절 음식 많이 먹어. 🌾"
            elif target_date_only in HOLIDAYS:
                full_response = f"질문한 날짜({target_date.strftime('%m월 %d일')})는 학교가 쉬는 공휴일/휴업일이라 급식이 제공되지 않는 날이야!"
            elif target_date_only == date(2026, 7, 17):
                full_response = "7월 17일은 제헌절로 인한 휴업일이라 급식이 제공되지 않아!"
            elif target_date_only == date(2026, 7, 21):
                full_response = "7월 21일은 방학식 날이라서 급식이 제공되지 않는 날이야!"
            else:
                intercepted = False

        # 🕒 예외 예측 레이어 B: 하교 일정 가로채기
        if not intercepted and is_asking_dismissal and is_asking_specific_day:
            intercepted = True
            context_tag = ["실시간 정밀 하교 예측 알고리즘"]
            target_weekday = target_date.weekday()
            
            if target_weekday in [5, 6]:
                full_response = "주말이라 학교에 안 가니까 하교 시간도 따로 없어! 🛌"
            elif is_vacation:
                full_response = "여름방학 기간(7/22 ~ 8/18)이라 학교에 등교하지 않는 날이야! 🏖️"
            elif is_chuseok:
                full_response = "추석 연휴라서 학교에 가지 않는 날이야! 🌾"
            elif target_date_only in HOLIDAYS:
                full_response = "학교가 쉬는 날(공휴일/재량휴업일)이라 하교 시간이 없는 날이야! 🎈"
            elif target_date_only in SPECIAL_SCHEDULES:
                full_response = SPECIAL_SCHEDULES[target_date_only]
            else:
                if target_weekday == 1:  # 화요일 -> 7교시 (4시 하교)
                    full_response = "화요일은 정규 7교시 수업을 진행하니까 **오후 4시**에 하교해! 🏫"
                elif target_weekday == 3:  # 목요일 분기
                    if target_date_only in CLUB_DAYS:
                        full_response = f"목요일({target_date.strftime('%m월 %d일')})은 동아리 활동이 있는 날이라 7교시로 진행되어 **오후 4시**에 하교해! 🎸"
                    elif target_date_only in NEXT_CLUB_DAYS:
                        full_response = f"목요일({target_date.strftime('%m월 %d일')})은 동아리 활동을 했던 다음 주 목요일이라 한 교시가 더해진 7교시날이라서 **오후 4시**에 하교해! ✍️"
                    else:
                        full_response = "일반적인 목요일은 6교시 수업이라 **오후 3시**에 하교해! 🏃"
                else:  # 월, 수, 금 -> 6교시 (3시 하교)
                    full_response = f"질문한 {weekday_map[target_weekday]}은 정규 6교시 수업을 진행하니까 **오후 3시**에 하교하는 날이야! 🏃"

        if intercepted:
            with st.chat_message("assistant"):
                st.write(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response, "contexts": context_tag})
        else:
            # 🧠 3. 일반적인 학칙 및 RAG 질문 처리 단계
            DYNAMIC_CONTEXT, matched_chunks = retrieve_relevant_context_openai(user_input, ALL_CHUNKS, EMBEDDING_MATRIX, top_n=3)

            SYSTEM_PROMPT = f"""
            당신은 서연중학교 학생들을 위한 친근한 학교생활 가이드 AI입니다.
            - 오늘 기준 날짜: {realtime_today}

            [학교 공식 규정 데이터베이스]
            {DYNAMIC_CONTEXT if DYNAMIC_CONTEXT else "사용자 질의와 일치하는 공식 규정이 없습니다."}

            [답변 규칙]
            1. 제공된 데이터베이스 내용에 기반해서만 대답하고 거짓 내용을 지어내지 마세요.
            2. 학사일정이나 이벤트를 안내할 때 '오늘'이라는 말을 절대로 사용하지 마세요. 대신 "~한 날이야", "~하는 날은 이때야" 처럼 서술하세요.
            3. 학칙이나 위치 등 데이터가 없어 모호한 질문의 경우, 문장 가장 끝부분에 "[확인 필요]"를 정확하게 적어주세요.
            4. 스마트폰 화면에서 읽기 편하게 불필요한 인사는 빼고, 줄바꿈을 조합하여 최대 3~4줄 이내로 핵심만 요약해서 친구처럼 반말로 대답하세요.
            """

            api_messages = [{"role": "system", "content": SYSTEM_PROMPT}]
            for msg in st.session_state.messages:
                if msg["role"] in ["user", "assistant"]:
                    api_messages.append({"role": msg["role"], "content": msg["content"]})

            with st.chat_message("assistant"):
                response_container = st.empty()
                response_stream = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=api_messages,
                    stream=True
                )

                raw_response = ""
                for chunk in response_stream:
                    if chunk.choices[0].delta.content is not None:
                        raw_response += chunk.choices[0].delta.content
                        display_response = raw_response.replace("[확인 필요]", "").strip()
                        response_container.write(display_response)

                cleaned_display_response = raw_response.replace("[확인 필요]", "").strip()
                response_container.write(cleaned_display_response)

                if matched_chunks:
                    with st.expander("🔍 매칭 규정 확인"):
                        for idx, src in enumerate(matched_chunks):
                            st.caption(f"**규정 {idx + 1}:** {src}")

            st.session_state.messages.append({
                "role": "assistant",
                "content": cleaned_display_response,
                "contexts": matched_chunks
            })

            if "[확인 필요]" in raw_response:
                save_unknown_question_csv(user_input)
                st.toast("💾 추가 검토가 필요한 질문은 보관함에 기록되었습니다.", icon="💡")

    except Exception as e:
        st.error(f"실시간 엔진 작동 중 예외 오류 발생: {e}")
