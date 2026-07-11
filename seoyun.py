import streamlit as st
from openai import OpenAI
from datetime import datetime, timedelta
import os
import csv
import numpy as np

# ==========================================
# 1. 🌐 다크모드 강제 고정 및 모바일 통합 테마 정의
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
except KeyError:
    st.error("Streamlit Secrets에 'OPENAI_API_KEY'가 설정되지 않았습니다.")
    st.stop()

client = OpenAI(api_key=MY_OPENAI_API_KEY)

# 🎨 안드로이드 크롬 / 아이폰 사파리 브라우저별 파편화 완전 방어 CSS (강제 다크모드)
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap');

        /* -------------------------------------------
         * 1) 🖤 전역 다크모드 시스템 강제 덮어쓰기 (테마 전환 차단)
         * ------------------------------------------- */
        :root {
            --background-color: #121214 !important;
            --secondary-background-color: #1a1a1e !important;
            --text-color: #f1f3f5 !important;
            --primary-color: #ff4b4b !important;
        }

        /* Streamlit 고유 배경 요소 다크화 */
        html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"], [data-testid="stSidebar"] {
            background-color: #121214 !important;
            color: #f1f3f5 !important;
            max-width: 100vw !important;
            overflow-x: hidden !important;
            box-sizing: border-box !important;
            -webkit-text-size-adjust: none !important; /* 📱 안드로이드 크롬/사파리 글자 크기 강제 축소 방지 */
            text-size-adjust: none !important;
        }

        /* ⚙️ 우측 상단 테마 변경 설정을 포함한 메뉴 및 헤더 툴바 완전 제거 (모드 전환 프로그램 무력화) */
        [data-testid="stToolbar"], [data-testid="stDecoration"], #MainMenu, footer {
            display: none !important;
            visibility: hidden !important;
            height: 0 !important;
        }

        .block-container {
            padding-top: 1.5rem !important;
            padding-bottom: 4rem !important;
            padding-left: 14px !important;
            padding-right: 14px !important;
            max-width: 100% !important;
            box-sizing: border-box !important;
        }

        .stApp, .title-section-container, .premium-card {
            font-family: 'Noto Sans KR', sans-serif !important;
        }

        /* -------------------------------------------
         * 2) 📱 안드로이드 크롬/삼성인터넷 가독성 저하 방지 배너
         * ------------------------------------------- */
        .title-section-container { 
            padding: 22px 18px; 
            border-radius: 16px; 
            background: linear-gradient(135deg, #1e1e24 0%, #2a1b1b 100%) !important;
            border: 1px solid #3a2525;
            margin-bottom: 18px; 
            text-align: left; 
            width: 100%;
            box-sizing: border-box !important;
        }
        .title-text { 
            color: #ff5c5c !important;
            font-size: 1.6rem !important; 
            font-weight: 800 !important; 
            margin: 0; 
            line-height: 1.3;
        }
        .subtitle-text { 
            color: #b0b5bc !important;
            font-size: 0.9rem !important; 
            font-weight: 500 !important; 
            margin-top: 6px; 
            margin-bottom: 0; 
        }

        /* 💎 다크모드 카드 컴포넌트 */
        .premium-card { 
            padding: 18px; 
            background: #1a1a1e !important;
            border-radius: 16px; 
            border: 1px solid #2d2d34; 
            box-shadow: 0 4px 16px rgba(0,0,0,0.2); 
            margin-bottom: 18px; 
            width: 100%;
            box-sizing: border-box !important;
        }
        .card-title { 
            font-size: 1.05rem; 
            font-weight: 700; 
            color: #ffffff !important;
            margin-bottom: 10px; 
            display: flex; 
            align-items: center; 
            gap: 8px; 
        }
        .card-content { 
            font-size: 0.9rem; 
            line-height: 1.6; 
            color: #ccd0d5 !important;
            margin: 0; 
            word-break: keep-all;
        }
        
        /* 🔥 질문 칩 크기 안드로이드 크롬 대응 대폭 확장 */
        .card-highlight { 
            color: #ff5c5c !important; 
            font-weight: 600; 
            background: #2d1f1f !important;
            padding: 10px 14px;
            border-radius: 20px;
            display: inline-block; 
            margin: 6px 4px;
            font-size: 0.88rem;
            border: 1px solid #4a2e2e;
            touch-action: manipulation;
        }

        /* -------------------------------------------
         * 3) 🔘 브라우저별 버튼 무조건 크게 확대 핵 (핵심 수정)
         * ------------------------------------------- */
        /* 안드로이드 크롬, 삼성인터넷, iOS 사파리 공통 적용 버튼 빌더 */
        div.stButton > button, div[data-testid="stSidebar"] button, .st-emotion-cache-19rx9w1e {
            width: 100% !important;
            padding: 16px 22px !important;
            font-size: 1.1rem !important;
            font-weight: 700 !important;
            background-color: #ff4b4b !important;
            color: #ffffff !important;
            min-height: 56px !important; /* 안드로이드 크롬 터치 스케일링 무시하고 고정 */
            height: 56px !important;
            border-radius: 14px !important;
            border: none !important;
            box-sizing: border-box !important;
            box-shadow: 0 4px 10px rgba(255, 75, 75, 0.3) !important;
            -webkit-appearance: none !important; /* 브라우저 기본 버튼 스타일 무력화 */
            appearance: none !important;
            touch-action: manipulation !important;
        }
        
        div.stButton > button:hover, div.stButton > button:active {
            background-color: #e03e3e !important;
            color: #ffffff !important;
        }

        /* 💬 하단 입력창 크롬에서 씹히거나 작아지는 현상 보정 */
        div[data-testid="stChatInput"] {
            background-color: #1a1a1e !important;
            border-radius: 14px !important;
            border: 1px solid #3a3a44 !important;
            padding: 4px !important;
        }
        
        div[data-testid="stChatInput"] textarea {
            min-height: 56px !important;
            font-size: 1.05rem !important;
            background-color: transparent !important;
            color: #ffffff !important;
            padding: 14px !important;
            line-height: 1.4 !important;
        }

        /* 마크다운 텍스트 및 기본 위젯 글자 크기 보정 */
        p, span, li, label, .stMarkdown {
            color: #f1f3f5 !important;
            font-size: 1rem !important;
        }

        /* 🖥️ 대화면 데스크톱 브라우저 역대응 스케일 밸런스 */
        @media (min-width: 768px) {
            .block-container { padding: 2.5rem 6rem !important; }
            .title-section-container { padding: 26px 36px; text-align: center; }
            .title-text { font-size: 2.4rem !important; }
            .subtitle-text { font-size: 1.05rem !important; }
            .premium-card { padding: 22px 28px; }
            .card-highlight { padding: 8px 14px; margin: 0 6px; }
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

    if not os.path.exists(rule_path):
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
            ["전자기기 반납", "아침 조례 시간에 개인 스마트폰을 의무적으로 반납해야 하며, 종례 시간 하교 시에 돌려받습니다. 공계기 적발 시 규정에 따라 조치됩니다."],
            ["쉬는시간 스마트폰", "조례 때 스마트폰을 일괄 수거하므로 쉬는 시간이나 점심시간에도 개인 휴대폰 사용은 원칙적으로 불가능합니다."],
            ["아이패드 노트북 태블릿", "개인 태블릿PC, 노트북, 아이패드 등은 선생님들이 아침에 따로 걷지는 않습니다. 수업 중 교과 선생님이 허용해 주신 상황에서는 자유롭게 쓸 수 있지만, 허용되지 않은 상황에서 무단으로 사용하는 것은 엄격히 금지됩니다."],
            ["무선 이어폰 에어팟", "일과 시간 중(쉬는 시간 포함) 에어팟, 갤럭시 버즈 등 무선 이어폰 착용은 금지됩니다. 단, 수업 중 선생님이 허가한 시청각 학습 시에는 사용 가능합니다."],
            ["전동 킥보드 자전거 등교", "전동 킥보드나 자전거를 타고 등교하는 것 자체를 완전히 금지한다는 명시적 조항은 없습니다. 하지만 무면허 주행이거나 나이 제한에 걸리는 경우, 혹은 헬멧 등 필수 안전 장비를 착용하지 않고 타는 등 법적/안전 요건을 갖추지 않은 위험한 운행 및 등교는 금지됩니다."],
            ["상벌점 제도", "우리 학교는 그린마일리지(상벌점) 제도 자체가 존재하지 않습니다. 벌점 누적에 대한 걱정 없이 자율적이고 즐겁게 학교생활을 하면 됩니다."],
            ["교내 흡연 금지", "교내 공공장소 및 학교 주변에서의 흡연은 학생 생활 규정에 따라 엄격히 금지되며, 적발 시 즉시 학생생활지도위원회에 회부되어 징계 및 금연 교육을 받게 됩니다."],
            ["무단 외출 금지", "점심시간이나 쉬는 시간에 교사 승인 없이 학교 정문 밖으로 나가는 것은 무단 외출로 간주되며, 안전사고 예방을 위해 엄격히 통제됩니다."],
            ["학교 폭력 예방", "언어폭력, 사이버 따돌림, 신체 폭력 등 모든 형태의 학교폭력은 무관용 원칙으로 대응하며, 인성인권부와 학교폭력대책심의위원회를 통해 엄중 처벌됩니다."],
            ["Wee클래스 상담실", "Wee클래스 상담실은 본관 3층에 위치해 있습니다. 다만 상담실에 담당 선생님이 계시지 않거나 부재중이실 때는 학생 마음대로 혼자 들어가는 것은 어려울 수 있으니 주의해야 합니다."],
            ["보건실 이용 및 위치", "보건실은 본관 2층에 위치해 있습니다. 수업 시간이든 쉬는 시간이든, 점심시간이든 몸이 아프다면 언제든지 방문하여 이용할 수 있습니다. 안정을 취하는 구체적인 최대 시간 제한은 유연하게 운영될 수 있습니다."],
            ["체육관 강당 운동장 없음", "현재 우리 학교에는 체육관(강당)이 존재하지 않으며, 운동장 또한 따로 마련되어 있지 않습니다. 따라서 체육 활동을 할 때에는 교내에 있는 탁구장, 헬스장, 당구 시설을 주로 이용합니다. 학년별 외부 체육 활동의 경우 1학년은 배드민턴을 치러 가고, 2학년은 외부 볼링장으로 이동하며, 3학년은 농구장을 이용하여 수업을 진행합니다."],
            ["학생회실 위치 및 규칙", "전교 학생회실은 본관 3층에 위치해 있습니다. 학생회실 내부에 학생회 임원 인원들이 없을 때에는 기본적으로 문이 잠겨 있으므로, 상시 개방되어 있거나 언제든 마음대로 방문할 수 있는 구조는 아닙니다."],
            ["급식 배식 순서 학년 반별", "안전하고 질서 있는 급식을 위해 기본 학년별 순서는 3학년 -> 2학년 -> 1학년 순서로 배식합니다. 다만, 각 학년 내에 속한 반(1반, 2반, 3반, 4반, 5반, 6반 등)의 세부 진입 순서는 공평성을 위해 매달 학교에서 정해주는 로테이션 스케줄에 맞춰 순서대로 배식을 받게 됩니다."],
            ["주말 급식 운영 여부", "주말(토요일, 일요일) 급식 운영 여부에 대해서는 정확히 명시되거나 확인된 바가 없으므로 주말 학사일정이나 학교 공식 공지사항 확인이 따로 필요합니다."],
            ["급식실 새치기 규정", "급식실 내에서 줄을 서는 도중 새치기를 하거나 일행을 끼워주는 행위는 엄격히 금지됩니다. 적발 시 선생님께 크게 혼나는 것은 물론이며, 불이익으로 줄의 가장 맨 뒤쪽 끝으로 밀려나서 배식을 늦게 받아야 할 수 있습니다."],
            ["동아리 활동 전일제", "동아리 활동은 목요일에 진행됩니다. 가끔씩 '전일제 동아리'라고 해서 1교시부터 7교시까지 하루 종일 동아리 활동만 하는 날이 있습니다. 이런 날에는 동아리 내에서 부원들끼리 의견을 모아 하고 싶은 활동을 직접 정해서 자유롭게 진행할 수 있습니다. 또한 상황에 따라 5교시부터 7교시까지만 압축적으로 동아리 활동을 진행하는 날도 존재합니다."],
            ["동아리 신청 및 상설 동아리", "동아리는 학기 초에 개설된 부서 중 본인이 원하는 곳을 선택하여 신청할 수 있습니다. 일반 동아리는 학기마다 새로 고를 수 있는 기회가 생기지만, 학생회나 방송부 같은 특수 상설 동아리의 경우에는 한 번 들어가면 1학기와 2학기 모두 변경 없이 유지하여 활동해야 하는 규칙이 있습니다."],
            ["방과후 학교", "방과 후 학교 수업의 구체적인 시작 및 종료 시간은 고정되어 있지 않으나 정규 수업이 모두 끝난 직후에 진행됩니다. 분기별로 배부되는 가정통신문을 통해 정식 신청을 완료한 학생에 한해서만 참여가 가능합니다."]
        ]
        with open(rule_path, mode="w", encoding="utf-8-sig", newline="") as f:
            csv.writer(f).writerows(rules)

    if not os.path.exists(lunch_path):
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
            ["7월 14일", "화요일", "초복", "혼합잡곡밥, 닭다리삼계탕, 찐만두(고기, 김치), 매운어묵잡채, 석박지, 수박화채"],
            ["7월 15일", "수요일", "일반식단", "귀리밥, 생배추된장국, 매콤돼지갈비찜, 통옥수수조각피자, 콩나물무침, 열무김치, 유산균요구르트"],
            ["7월 16일", "목요일", "제헌절전야", "일반식단 제공"],
            ["7월 17일", "금요일", "제헌절", "제헌절로 인한 휴업일 (급식 없음)"],
            ["7월 20일", "월요일", "일반식단", "열무비빔밥&약고추장, 연포탕, 소시지롤도그, 계란찜, 백김치, 포도(거봉)"],
            ["7월 21일", "방학식", "방학식 (급식 없음 / 신나는 여름방학)"]
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

    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=raw_docs
    )
    embeddings = np.array([d.embedding for d in response.data])
    np.save(embed_cache_path, embeddings)

    return raw_docs, embeddings


try:
    ALL_CHUNKS, EMBEDDING_MATRIX = DEEP_INITIALIZE_RAG_ENGINE()
except Exception as e:
    st.error(f"데이터 로드 오류: {e}")
    st.stop()


def retrieve_relevant_context_openai(query, documents, embedding_matrix, top_n=3):
    if not documents or embedding_matrix.size == 0:
        return "", []
    try:
        q_res = client.embeddings.create(
            model="text-embedding-3-small",
            input=[query]
        )
        q_embed = np.array(q_res.data[0].embedding)
        similarities = np.dot(embedding_matrix, q_embed)
        top_indices = similarities.argsort()[-top_n:][::-1]
        matched_chunks = [documents[i] for i in top_indices if similarities[i] > 0.15]
        return "\n".join(matched_chunks), matched_chunks
    except Exception as e:
        return f"문맥 오류 ({e})", []


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
# 3. 📱 사이드바 메뉴 (다크 스킨)
# ==========================================
with st.sidebar:
    st.markdown("<h2 style='color:#ffffff;'>🏫 서연중 AI 가이드</h2>", unsafe_allow_html=True)
    st.caption("학생 지원 대시보드")
    st.markdown("<hr style='border:1px solid #2d2d34;'>", unsafe_allow_html=True)
    
    st.markdown("<h4 style='color:#ffffff;'>안내사항</h4>", unsafe_allow_html=True)
    st.markdown("""
        <div style="background: linear-gradient(135deg, #2d1f1f 0%, #4a2e2e 100%) !important; border-radius: 12px; padding: 14px; border: 1px solid #6b3e3e;">
            <p style="color: #ff5c5c; margin: 0; font-weight: 600; font-size: 0.88rem; word-break:keep-all;">
                🚨 체육관과 운동장이 없으므로 탁구장, 헬스장, 당구 및 학년별 외부 체육 장소를 우선 가이드합니다.
            </p>
        </div>
    """, unsafe_allow_html=True)

# ==========================================
# 4. 🖤 메인 인터페이스 레이아웃 (수식어 없는 다크 테마)
# ==========================================
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
            <span class="card-highlight">🎸 동아리 전일제에는 뭐해?</span>
        </p>
    </div>
""", unsafe_allow_html=True)

st.markdown("<hr style='border:1px solid #2d2d34;'>", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant",
         "content": "안녕하세요! 서연중학교 AI 안내 센터에 오신 것을 환영합니다. 오늘 학교 생활이나 학칙에 대해 어떤 도움이 필요하신가요? 🏫"}
    ]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if "contexts" in msg and msg["contexts"]:
            with st.expander("🔍 관련 규정 근거"):
                for source in msg["contexts"]:
                    st.caption(source)

# ==========================================
# 5. 🤖 실시간 대화 추론 엔진
# ==========================================
if user_input := st.chat_input("Gemini에 물어보기..."):
    with st.chat_message("user"):
        st.write(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    try:
        now = datetime.now()
        weekday_map = {0: "월요일", 1: "화요일", 2: "수요일", 3: "목요일", 4: "금요일", 5: "토요일", 6: "일요일"}
        realtime_today = f"{now.strftime('%Y년 %m월 %d일')} {weekday_map[now.weekday()]}"

        is_asking_lunch = any(keyword in user_input for keyword in ["급식", "식단", "메뉴", "밥", "먹어"])
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

        if is_asking_lunch and is_asking_specific_day and target_date.weekday() in [5, 6]:
            with st.chat_message("assistant"):
                full_response = f"질문한 날짜({target_date.strftime('%m월 %d일')} {weekday_map[target_date.weekday()]})는 주말이라 급식이 없어! 주말 일정표를 다시 확인해줘. ☀️"
                st.write(full_response)
                st.session_state.messages.append(
                    {"role": "assistant", "content": full_response, "contexts": ["주말 예외 필터 레이어"]})
        else:
            DYNAMIC_CONTEXT, matched_chunks = retrieve_relevant_context_openai(user_input, ALL_CHUNKS, EMBEDDING_MATRIX,
                                                                               top_n=3)

            SYSTEM_PROMPT = f"""
            당신은 서연중학교 학생들을 위한 친근한 학교생활 가이드 AI입니다.
            - 오늘 기준 날짜: {realtime_today}

            [학교 공식 규정 데이터베이스]
            {DYNAMIC_CONTEXT if DYNAMIC_CONTEXT else "사용자 질의와 일치하는 공식 규정이 없습니다."}

            [답변 규칙]
            1. 제공된 데이터베이스 내용에 기반해서만 대답하고 거짓 내용을 지어내지 마세요.
            2. 학칙이나 위치 등 데이터가 없어 모호한 질문의 경우, 문장 가장 끝부분에 "[확인 필요]"를 정확하게 적어주세요.
            3. 스마트폰 화면에서 읽기 편하게 불필요한 인사는 빼고, 줄바꿈을 조합하여 최대 3~4줄 이내로 핵심만 요약해서 친구처럼 반말로 대답하세요.
            """

            api_messages = [{"role": "system", "content": SYSTEM_PROMPT}]
            for msg in st.session_state.messages:
                if msg["role"] == "user":
                    api_messages.append({"role": "user", "content": msg["content"]})
            if not api_messages or api_messages[-1]["content"] != user_input:
                api_messages.append({"role": "user", "content": user_input})

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

                full_response = raw_response
                cleaned_display_response = full_response.replace("[확인 필요]", "").strip()
                response_container.write(cleaned_display_response)

                with st.expander("🔍 매칭 규정 확인"):
                    if matched_chunks:
                        for idx, source in enumerate(matched_chunks):
                            st.caption(f"**규정 {idx + 1}:** {source}")
                    else:
                        st.caption("데이터베이스에 매칭된 내용이 없습니다.")

        st.session_state.messages.append({
            "role": "assistant",
            "content": cleaned_display_response,
            "contexts": matched_chunks if 'matched_chunks' in locals() else []
        })

        if "[확인 필요]" in full_response:
            save_unknown_question_csv(user_input)
            st.toast("💾 추가 검토가 필요한 질문은 보관함에 기록되었습니다.", icon="💡")

    except Exception as e:
        st.error(f"오류가 발생했습니다: {e}")
