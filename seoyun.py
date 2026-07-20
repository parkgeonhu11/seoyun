import streamlit as st
from openai import OpenAI
from datetime import datetime, timedelta, date
import os
import csv
import re
import time
import numpy as np

# ==========================================
# 1. 🌐 웹페이지 기본 구성 및 반응형 크로스 브라우징 정의
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

# 🎨 [기존 UI/디자인 유지] PC 다크모드 무조건 차단 및 연회색/흰색 강제 고정 스타일
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght=400;500;700;900&display=swap');

/* 📱 기본 배경 정의 및 가로 스크롤 제거 */
html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
max-width: 100vw !important;
overflow-x: hidden !important;
box-sizing: border-box !important;
-webkit-text-size-adjust: none !important;
text-size-adjust: none !important;
background-color: #F8FAFC !important;
}

/* ⚙️ 불필요한 기본 툴바 및 내부 데코레이션 제거 */
[data-testid="stToolbar"], [data-testid="stDecoration"], #MainMenu, footer {
display: none !important;
visibility: hidden !important;
height: 0 !important;
}

/* 🧩 메인 컨테이너 여백 최적화 */
.block-container {
padding-top: 3.5rem !important;
padding-bottom: 9rem !important;
padding-left: 4% !important;
padding-right: 4% !important;
max-width: 100% !important;
box-sizing: border-box !important;
}

/* 전역 폰트 지정 */
.stApp, .title-section-container, .premium-card {
font-family: 'Noto Sans KR', sans-serif !important;
}

/* 🔴 챗봇 메시지 영역 스타일 */
[data-testid="stChatMessage"] {
background-color: #FFFFFF !important;
border: 1px solid #E2E8F0 !important;
border-radius: 12px !important;
margin-bottom: 10px !important;
box-shadow: 0 2px 8px rgba(15, 23, 42, 0.02) !important;
}

[data-testid="stChatMessage"] *, 
[data-testid="stChatMessage"] p, 
.stMarkdown div p,
[data-testid="stMarkdownContainer"] p {
color: #0F172A !important;
font-size: 0.95rem !important;
line-height: 1.6 !important;
}

/* ✨ 메인 비주얼 배너 */
.title-section-container {
padding: 24px 20px;
border-radius: 20px;
background: linear-gradient(135deg, #FF5252 0%, #FF7A45 100%) !important;
box-shadow: 0 8px 24px rgba(255, 82, 82, 0.15);
margin-bottom: 20px;
text-align: left;
width: 100%;
box-sizing: border-box !important;
}
.title-text {
color: #FFFFFF !important;
font-size: 1.5rem !important;
font-weight: 900 !important;
margin: 0 !important;
padding: 0 !important;
text-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
.subtitle-text {
color: #FFFFFF !important;
font-size: 0.88rem !important;
font-weight: 500 !important;
margin-top: 8px !important;
margin-bottom: 0 !important;
line-height: 1.4 !important;
}

/* 💎 대시보드형 안내 카드 레이아웃 */
.premium-card {
padding: 18px 16px;
background: #FFFFFF !important;
border-radius: 18px;
border: 1px solid #E2E8F0;
box-shadow: 0 4px 14px rgba(0, 0, 0, 0.03);
margin-bottom: 20px;
width: 100%;
box-sizing: border-box !important;
}
.card-title {
font-size: 1.0rem !important;
font-weight: 700 !important;
color: #0F172A !important;
margin-bottom: 12px !important;
display: flex;
align-items: center;
gap: 6px;
}
.card-content {
font-size: 0.88rem !important;
color: #334155 !important;
}

/* 📱 추천 질문 태그 칩 */
.chip-container {
margin-top: 14px;
display: flex;
flex-wrap: wrap;
gap: 8px;
}
.card-highlight {
color: #E11D48 !important;
font-weight: 700 !important;
background: #FFF1F2 !important;
padding: 8px 14px;
border-radius: 30px;
font-size: 0.82rem !important;
border: 1px solid #FECDD3 !important;
}

/* 🔍 근거 스니펫 박스 */
.evidence-box {
background-color: #F1F5F9 !important;
border-left: 4px solid #EF4444 !important;
padding: 12px 14px !important;
color: #1E293B !important;
font-size: 0.85rem !important;
}

/* 🎯 하단 입력창 밝은 톤 강제 유지 */
div[data-testid="stBottom"],
div[data-testid="stBottom"] > div,
div[data-testid="stBottomBlockContainer"],
div[data-testid="stBottomBlockContainer"] > div,
div[data-testid="stChatInput"],
div[data-testid="stChatInput"] > div,
div[data-testid="stChatInputContainer"],
.stChatInputContainer {
background-color: #F8FAFC !important;
background: #F8FAFC !important;
box-shadow: none !important;
border: none !important;
}

div[data-testid="stChatInput"] textarea,
div[data-testid="stChatInput"] [data-baseweb="textarea"],
div[data-testid="stChatInput"] [data-baseweb="base-input"],
.stChatInputContainer textarea,
div[data-testid="stChatInput"] [data-testid="stMarkdownContainer"] p {
background-color: #FFFFFF !important;
background: #FFFFFF !important;
color: #0F172A !important;
border: 1px solid #CBD5E1 !important;
border-radius: 14px !important;
}

div[data-testid="stChatInput"] textarea::placeholder {
color: #94A3B8 !important;
}

div[data-testid="stChatInput"] button {
background-color: transparent !important;
}

.sidebar-custom-box {
background: linear-gradient(135deg, #FFF1F2 0%, #FFE4E6 100%) !important;
border-radius: 12px;
padding: 12px;
}

@media (max-width: 380px) {
.block-container { padding-top: 2.2rem !important; padding-bottom: 7.5rem !important; }
.title-section-container { padding: 16px 14px; }
.title-text { font-size: 1.2rem !important; }
.subtitle-text { font-size: 0.78rem !important; }
.premium-card { padding: 14px 12px; }
.card-title { font-size: 0.92rem !important; }
.card-content { font-size: 0.8rem !important; }
.card-highlight { font-size: 0.74rem !important; padding: 6px 10px; }
[data-testid="stChatMessage"] p { font-size: 0.88rem !important; }
}

@media (min-width: 381px) and (max-width: 767px) {
.block-container { padding-top: 2.6rem !important; padding-bottom: 8rem !important; }
}

@media (min-width: 768px) and (max-width: 1024px) {
.block-container { max-width: 90% !important; margin: 0 auto !important; padding-top: 3.2rem !important; }
.title-text { font-size: 1.7rem !important; }
.premium-card { padding: 20px; }
}

@media (min-width: 1025px) {
.block-container { max-width: 800px !important; margin: 0 auto !important; padding-top: 4.5rem !important; }
.title-section-container { padding: 34px 36px; }
.title-text { font-size: 2.0rem !important; }
.premium-card { padding: 24px; }

div[data-testid="stBottomBlockContainer"] {
max-width: 800px !important;
margin: 0 auto !important;
}
}
</style>
""", unsafe_allow_html=True)


# ==========================================
# 2. 📂 데이터 로드 및 RAG 엔진
# ==========================================
RULES_DATA = [
["카테고리", "학칙 및 규정 내용"],
["등교 시간 및 지각", "아침 오전 8시 50분까지 교실에 입실 완료해야 합니다. 8시 50분이 지나면 지각 처리됩니다."],
["지각 처리 인정 기준", "오전 8시 50분 이후에 교실에 들어오면 지각으로 기록됩니다. 단, 버스 지연 등의 불가피한 사유나 몸이 아픈 경우, 병원 방문 등 합당한 증빙 서류나 사유가 확인되면 인정될 수 있습니다."],
["무단 지각 결석", "무단 지각, 무단 결과, 무단 조퇴를 합산하여 3회가 되면 무단 결석 1회로 처리되므로 생활기록부 관리를 위해 유의해야 합니다."],
["질병 결석 신청", "질병으로 인해 결석할 경우, 등교 후 3일 이내에 질병결석계와 함께 의사 진단서, 소견서 또는 처방전 등 증빙 서류를 담임선생님께 제출해야 합니다."],
["조퇴 및 외출", "일과 중 아프거나 부득이한 사정으로 조퇴·외출을 하려면 반드시 담임선생님의 승인을 받아 '외출증/조퇴증'을 발급받은 후 경비실에 제출하고 하교해야 합니다."],
["복장 규정", "사복(평상복) 착용은 금지됩니다. 등교 시 교복 또는 학교 생활복, 체육복 중에서 본인이 원하는 옷을 자율적으로 선택해서 편하게 입고 오면 됩니다."],
["체육복 등교", "체육 수업이 없는 날을 포함하여 평일 언제든 학교 지정 체육복을 입고 등하교하는 것이 전면 허용됩니다."],
["교복 사복 혼용", "교   나 체육복 위에 사복 아우터(패딩, 코트 등)를 입는 것은 허용되지만, 아우터 안에는 반드시 교복, 생활복, 체육복 중 하나를 착용해야 합니다."],
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
["체육관 강당 운동장 없음", "현재 우리 학교에는 체육  (강당)이 존재하지 않으며, 운동장 또한 따로 마련되어 있지 않습니다. 따라서 체육 활동을 할 때에는 교내에 있는 탁구장, 헬스장, 당구 시설을 주로 이용합니다. 학년별 외부 체육 활동의 경우 1학년은 배드민턴을 치러 가고, 2학년은 외부 볼링장으로 이동하며, 3학년은 농구장을 이용하여 수업을 진행합니다."],
["학생회실 위치 및 규칙", "전교 학생회실은 본관 3층에 위치해 있습니다. 학생회실 내부에 학생회 임원 인원들이 없을 때에는 기본적으로 문이 잠겨 있으므로, 상시 개방되어 있거나 언제든 마음대로 방문할 수 있는 구조는 아닙니다."],
["급식 배식 순서 학년 반별", "안전하고 질서 있는 급식을 위해 기본 학년별 순서는 3학년 -> 2학년 -> 1학년 순서로 배식합니다. 다만, 각 학년 내에 속한 반의 세부 진입 순서는 공평성을 위해 매달 학교에서 정해주는 로테이션 스케줄에 맞춰 순서대로 배식을 받게 됩니다."],
["주말 급식 운영 여부", "주말(토요일, 일요일) 급식 운영 여부에 대해서는 정확히 명시되거나 확인된 바가 없으므로 주말 학사일정이나 학교 공식 공지사항 확인이 따로 필요합니다."],
["급식실 새치기 규정", "급식실 내에서 줄을 서는 도중 새치기를 하거나 일행을 끼워주는 행위는 엄격히 금지됩니다. 적발 시 선생님께 크게 혼나는 것은 물론이며, 불이익으로 줄의 가장 맨 뒤쪽 끝으로 밀려나서 배식을 늦게 받아야 할 수 있습니다."],
["동아리 활동 전일제", "동아리 활동은 목요일에 진행됩니다. 가끔씩 '전일제 동아리'라고 해서 1교시부터 7교시까지 하루 종일 동아리 활동만 하는 날이 있습니다. 이런 날에는 동아리 내에서 부원들끼리 의견을 모아 하고 싶은 활동을 직접 정해서 자유롭게 진행할 수 있습니다. 또한 상황에 따라 5교시부터 7교시까지만 압축적으로 동아리 활동을 진행하는 날도 존재합니다."],
["동아리 신청 및 상설 동아리", "동아리는 학기 초에 개설된 부서 중 본인이 원하는 곳을 선택하여 신청할 수 있습니다. 일반 동아리는 학기마다 새로 고를 수 있는 기회가 생기지만, 학생회나 방송부 같은 특수 상설 동아리의 경우에는 한 번 들어가면 1학기와 2학기 모두 변경 없이 유지하여 활동해야 하는 규칙이 있습니다."],
["방과후 학교", "방과 후 학교 수업의 구체적인 시작 및 종료 시간은 고정되어 있지 않으나 정규 수업이 모두 끝난 직후에 진행됩니다. 분기별로 배부되는 가정통신문을 통해 정식 신청을 완료한 학생에 한해서만 참여가 가능합니다."],
["급식 시작 시간", "급식은 4교시가 끝난 직후부터 시작됩니다. 1교시는 오전 8시 50분에 시작하고 수업은 45분, 쉬는 시간은 10분이므로 보통 오후 12시 20분쯤부터 급식이 시작된다고 보면 됩니다."],
["수업 시간", "1교시는 오전 8시 50분에 시작합니다. 한 교시는 45분 수업이며, 교시 사이 쉬는 시간은 10분입니다."],
["급식 새치기", "급식 줄 새치기는 절대 허용되지 않습니다. 적발되면 줄 맨 뒤로 이동하며 선생님의 지도를 받을 수 있습니다."],
["급식 알레르기 표시", "급식 식단표에는 알레르기 유발 식품 표시가 함께 제공됩니다."],
["방학식 급식 및 수업", "7월 21일은 방학식입니다. 정규 7교시가 아니라 단축수업으로 평소보다 일찍 끝나는 날이며, 급식은 제공되지 않습니다. 방학식 다음 날부터 여름방학이 시작됩니다."],
["여름방학 기간", "여름방학은 7월 22일부터 8월 18일까지입니다. 8월 19일은 2학기 개학식입니다."],
]

LUNCH_DATA = [
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
["7월 21일", "방학식", "방학식", "방학식 (급식 없음 / 신나는 여름방학)"],
]
cat >> /mnt/user-data/outputs/seoyeon_ai_center_refactored.py <<'PY'


@st.cache_resource
def DEEP_INITIALIZE_RAG_ENGINE():
    rule_path = "seoyeon_chatbot_data.csv"
    lunch_path = "seoyeon_lunch_data.csv"
    embed_cache_path = "seoyeon_embeddings.npy"

    with open(rule_path, mode="w", encoding="utf-8-sig", newline="") as f:
        csv.writer(f).writerows(RULES_DATA)

    with open(lunch_path, mode="w", encoding="utf-8-sig", newline="") as f:
        csv.writer(f).writerows(LUNCH_DATA)

    raw_docs = []
    with open(rule_path, mode="r", encoding="utf-8-sig") as f:
        r = csv.reader(f)
        next(r)
        for row in r:
            if len(row) >= 2:
                raw_docs.append(f"[수정학칙] 주제: {row[0]} -> 내부규정 상세: {row[1]}")

    with open(lunch_path, mode="r", encoding="utf-8-sig") as f:
        r = csv.reader(f)
        next(r)
        for row in r:
            if len(row) >= 4:
                raw_docs.append(f"[식단데이터] 날짜일정: {row[0]} ({row[1]}) [{row[2]}] -> 제공메뉴: {row[3]}")

    rebuild_embeddings = True
    embeddings = None
    if os.path.exists(embed_cache_path):
        try:
            cached = np.load(embed_cache_path)
            if len(cached) == len(raw_docs):
                embeddings = cached
                rebuild_embeddings = False
        except Exception:
            rebuild_embeddings = True

    if rebuild_embeddings:
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


def get_context_for_query(query, top_n=3):
    _, matched = retrieve_relevant_context_openai(query, ALL_CHUNKS, EMBEDDING_MATRIX, top_n=top_n)
    return matched


def stream_text_like_chatgpt(container, text, delay=0.012):
    rendered = ""
    for ch in text:
        rendered += ch
        container.markdown(rendered + "▌")
        time.sleep(delay)
    container.markdown(rendered)


def parse_target_date(user_input, now_dt):
    target_date = now_dt
    is_specific = False

    date_pattern_match = re.search(r'(\d{1,2})\s*[월./]\s*(\d{1,2})\s*일?', user_input)
    explicit_date = None
    if date_pattern_match:
        try:
            _m, _d = int(date_pattern_match.group(1)), int(date_pattern_match.group(2))
            _inferred_year = 2027 if _m <= 3 else 2026
            explicit_date = date(_inferred_year, _m, _d)
        except ValueError:
            explicit_date = None

    if "오늘" in user_input:
        target_date = now_dt
        is_specific = True
    elif "내일" in user_input:
        target_date = now_dt + timedelta(days=1)
        is_specific = True
    elif "모레" in user_input:
        target_date = now_dt + timedelta(days=2)
        is_specific = True
    elif "어제" in user_input:
        target_date = now_dt - timedelta(days=1)
        is_specific = True
    elif explicit_date:
        target_date = datetime(explicit_date.year, explicit_date.month, explicit_date.day)
        is_specific = True

    return target_date, is_specific, explicit_date


weekday_map = {
    0: "월요일", 1: "화요일", 2: "수요일", 3: "목요일", 4: "금요일", 5: "토요일", 6: "일요일"
}

CLUB_DAYS = {date(2026, 8, 27), date(2026, 9, 17), date(2026, 10, 22)}
NEXT_CLUB_DAYS = {day + timedelta(weeks=1) for day in CLUB_DAYS}
HOLIDAY_NAMES = {
    date(2026, 7, 17): "제헌절 휴업일",
    date(2026, 10, 5): "대체공휴일",
    date(2026, 10, 9): "한글날",
    date(2026, 11, 19): "수능 재량휴업일",
    date(2026, 11, 20): "재량휴업일",
    date(2026, 12, 25): "성탄절",
    date(2027, 1, 1): "신정",
}
SPECIAL_SCHEDULES = {
    date(2026, 8, 19): "2학기 개학식을 진행하는 날이야!",
    date(2026, 10, 7): "수요일이지만 금요일 시간표로 수업을 변경해서 진행하는 날이야!",
    date(2026, 10, 20): "1,2학년은 중간고사, 3학년은 기말고사를 치르는 지필평가 기간이야! 시험 일정이 끝나면 바로 하교해.",
    date(2026, 10, 21): "1,2학년은 중간고사, 3학년은 기말고사를 치르는 지필평가 기간이야! 시험 일정이 끝나면 바로 하교해.",
    date(2026, 12, 14): "1,2학년 기말고사 시험을 보는 날이야! 시험 일정이 끝나면 바로 하교해.",
    date(2026, 12, 15): "1,2학년 기말고사 시험을 보는 날이야! 시험 일정이 끝나면 바로 하교해.",
    date(2026, 12, 30): "우리 학교 축제인 '서연제' 행사가 있는 날이야!",
    date(2027, 1, 4): "차기 학생회장 선거가 진행되는 날이야!",
    date(2027, 1, 8): "2학기 종업식을 하는 날이야!",
}
SCHOOL_EVENTS = [
    {"date": date(2026, 7, 17), "name": "제헌절로 인한 휴업일", "keywords": ["제헌절"]},
    {"date": date(2026, 7, 21), "name": "방학식", "keywords": ["방학식"]},
    {"date": date(2026, 8, 19), "name": "2학기 개학식", "keywords": ["개학식"]},
    {"date": date(2026, 8, 27), "name": "동아리 전일제 활동일", "keywords": ["동아리 전일제", "전일제 동아리"]},
    {"date": date(2026, 9, 17), "name": "동아리 전일제 활동일", "keywords": ["동아리 전일제", "전일제 동아리"]},
    {"date": date(2026, 10, 5), "name": "대체공휴일", "keywords": ["대체공휴일"]},
    {"date": date(2026, 10, 7), "name": "금요일 시간표로 변경되어 수업하는 날", "keywords": ["시간표 변경", "금요일 시간표"]},
    {"date": date(2026, 10, 9), "name": "한글날", "keywords": ["한글날"]},
    {"date": date(2026, 10, 20), "name": "지필평가(1,2학년 중간고사 / 3학년 기말고사) 1일차", "keywords": ["중간고사"]},
    {"date": date(2026, 10, 21), "name": "지필평가(1,2학년 중간고사 / 3학년 기말고사) 2일차", "keywords": ["중간고사"]},
    {"date": date(2026, 10, 22), "name": "동아리 전일제 활동일", "keywords": ["동아리 전일제", "전일제 동아리"]},
    {"date": date(2026, 11, 19), "name": "수능 재량휴업일", "keywords": ["수능 재량휴업일", "수능"]},
    {"date": date(2026, 11, 20), "name": "재량휴업일", "keywords": ["재량휴업일"]},
    {"date": date(2026, 12, 14), "name": "1,2학년 기말고사 1일차", "keywords": ["기말고사"]},
    {"date": date(2026, 12, 15), "name": "1,2학년 기말고사 2일차", "keywords": ["기말고사"]},
    {"date": date(2026, 12, 25), "name": "성탄절", "keywords": ["성탄절", "크리스마스"]},
    {"date": date(2026, 12, 30), "name": "서연제(학교 축제)", "keywords": ["서연제", "축제"]},
    {"date": date(2027, 1, 1), "name": "신정", "keywords": ["신정"]},
    {"date": date(2027, 1, 4), "name": "차기 학생회장 선거", "keywords": ["학생회장 선거", "회장 선거"]},
    {"date": date(2027, 1, 8), "name": "2학기 종업식", "keywords": ["종업식"]},
    {"date": date(2027, 3, 2), "name": "새 학년도 개학식(화요일)", "keywords": ["새 학년도 개학식", "새학년도 개학식", "새 학기 개학식", "3월 개학식"]},
]


def get_day_off_reason(d):
    if d.weekday() in (5, 6):
        return "주말"
    if date(2026, 7, 22) <= d <= date(2026, 8, 18):
        return "여름방학 기간"
    if date(2026, 9, 24) <= d <= date(2026, 9, 27):
        return "추석 연휴 기간"
    if date(2027, 1, 9) <= d <= date(2027, 3, 1):
        return "겨울방학 기간"
    if d in HOLIDAY_NAMES:
        return HOLIDAY_NAMES[d]
    return None


def find_event_name_by_date(d):
    names = [ev["name"] for ev in SCHOOL_EVENTS if ev["date"] == d]
    off_reason = get_day_off_reason(d)
    if off_reason and off_reason not in ("주말",) and off_reason not in names:
        names.append(off_reason)
    if names:
        return ", ".join(dict.fromkeys(names))
    if off_reason:
        return off_reason
    return None


def find_events_by_keyword(text):
    matched = []
    for ev in SCHOOL_EVENTS:
        if any(kw in text for kw in ev["keywords"]):
            matched.append(ev)
    return matched


def get_lunch_row_by_date(target_date_only):
    month_day = f"{target_date_only.month}월 {target_date_only.day}일"
    for row in LUNCH_DATA[1:]:
        if row[0] == month_day:
            return row
    return None


def build_lunch_response(target_date_only):
    off_reason = get_day_off_reason(target_date_only)
    if target_date_only == date(2026, 7, 21):
        return "7월 21일은 방학식이라 급식이 없어! 방학식 끝나고 바로 여름방학 분위기 들어가는 날이야."
    if off_reason == "주말":
        return f"{target_date_only.strftime('%m월 %d일')}은 주말이라 급식이 없어!"
    if off_reason == "여름방학 기간":
        return "여름방학 기간이라 학교 급식이 운영되지 않아!"
    if off_reason == "추석 연휴 기간":
        return "추석 연휴라 급식이 없어!"
    if off_reason == "겨울방학 기간":
        return "겨울방학 기간이라 급식이 운영되지 않아!"
    if off_reason:
        return f"{target_date_only.strftime('%m월 %d일')}은 {off_reason}이라 급식이 제공되지 않아!"

    row = get_lunch_row_by_date(target_date_only)
    if row:
        return f"{row[0]} 급식은 **{row[3]}** 이야!"
    return "그 날짜 급식 정보는 아직 등록된 데이터에서 확인되지 않아. [확인 필요]"


def build_dismissal_response(target_date_only):
    off_reason = get_day_off_reason(target_date_only)
    if target_date_only == date(2026, 7, 21):
        return "7월 21일은 방학식이야! 정규 7교시가 아니라 단축수업으로 일찍 끝나는 날이야. 그리고 급식도 제공되지 않아."
    if off_reason == "주말":
        return "주말이라 학교에 안 가니까 하교 시간도 따로 없어! 🛌"
    if off_reason == "여름방학 기간":
        return "여름방학 기간이라 학교에 등교하지 않는 날이야! 🏖️"
    if off_reason == "추석 연휴 기간":
        return "추석 연휴라 학교에 가지 않는 날이야! 🌾"
    if off_reason == "겨울방학 기간":
        return "겨울방학 기간이라 학교에 등교하지 않는 날이야! ❄️"
    if off_reason:
        return f"{off_reason}이라 하교 시간이 없는, 학교에 안 가는 날이야! 🎈"
    if target_date_only in SPECIAL_SCHEDULES:
        return SPECIAL_SCHEDULES[target_date_only]

    target_weekday = target_date_only.weekday()
    if target_weekday == 1:
        return "화요일은 정규 7교시 수업이라 **오후 4시**에 끝나!"
    if target_weekday == 3:
        if target_date_only in CLUB_DAYS:
            return f"{target_date_only.strftime('%m월 %d일')} 목요일은 동아리 활동이 있는 날이라 **오후 4시**에 끝나!"
        if target_date_only in NEXT_CLUB_DAYS:
            return f"{target_date_only.strftime('%m월 %d일')} 목요일은 동아리 다음 주 7교시 운영 날이라 **오후 4시**에 끝나!"
        return "일반적인 목요일은 6교시 수업이라 **오후 3시**에 끝나!"
    return f"{weekday_map[target_weekday]}은 보통 6교시 수업이라 **오후 3시**에 끝나!"
cat >> /mnt/user-data/outputs/seoyeon_ai_center_refactored.py <<'PY'

# ==========================================
# 3. 📱 사이드바 메뉴
# ==========================================
with st.sidebar:
    st.markdown("## 🏫 서연중 AI 가이드")
    st.caption("학생 지원 대시보드")
    st.markdown("---")

    st.markdown("#### 안내사항")
    st.markdown(
        """
        <div class="sidebar-custom-box">
            <p style="color: #E11D48; margin: 0; font-weight: 700; font-size: 0.85rem; word-break:keep-all;">
                🚨 체육관과 운동장이 없으므로 탁구장, 헬스장, 당구 및 학년별 외부 체육 장소를 우선 가이드합니다.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ==========================================
# 4. 👑 메인 인터페이스 레이아웃
# ==========================================
st.markdown(
    """
    <div class="title-section-container">
        <h1 class="title-text">서연중학교 AI 안내 센터</h1>
        <p class="subtitle-text">우리 학교의 다양한 학칙 규정과 급식 일정을 안내합니다.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="premium-card">
        <div class="card-title">
            <img src="https://img.icons8.com/fluency/48/sparkles.png" width="20" height="20"/>
            자주 묻는 질문 예시
        </div>
        <p class="card-content">
            궁금한 점을 아래 입력창에 검색하거나 참고해 보세요.
        </p>
        <div class="chip-container">
            <span class="card-highlight">🍱 오늘 급식 뭐야?</span>
            <span class="card-highlight">🍚 급식은 몇 시부터 먹어?</span>
            <span class="card-highlight">🚫 급식 줄 새치기 가능해?</span>
            <span class="card-highlight">🥜 급식 알레르기 표시 있어?</span>
            <span class="card-highlight">📅 내일 급식 있어?</span>
            <span class="card-highlight">🏫 오늘 하교 시간 언제야?</span>
            <span class="card-highlight">🎓 방학식은 언제야?</span>
            <span class="card-highlight">📱 휴대폰 언제 반납해?</span>
            <span class="card-highlight">🩺 보건실 어디야?</span>
            <span class="card-highlight">🏓 체육관 없는데 체육 어디서 해?</span>
            <span class="card-highlight">🍚 급식 순서는 어떻게 돼?</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "안녕하세요! 서연중학교 AI 안내 센터에 오신 것을 환영합니다. 오늘 학교 생활이나 학칙에 대해 어떤 도움이 필요하신가요? 🏫",
            "contexts": [],
        }
    ]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if msg.get("contexts"):
            with st.expander("🔍 관련 규정 근거 보기"):
                for source in msg["contexts"]:
                    st.markdown(f'<div class="evidence-box">{source}</div>', unsafe_allow_html=True)


def answer_common_queries(user_input, now_dt, target_date_only, is_asking_specific_day):
    lower = user_input

    if any(k in lower for k in ["급식", "식단", "메뉴", "밥", "먹어"]) and any(k in lower for k in ["몇 시", "몇시", "언제", "시작"]):
        contexts = get_context_for_query("급식 시작 시간 수업 시간")
        return "급식은 4교시가 끝난 직후부터 시작돼! 1교시가 8시 50분 시작이고 45분 수업, 쉬는 시간 10분 기준이라 보통 **오후 12시 20분쯤**부터라고 보면 돼.", contexts

    if "알레르기" in lower and any(k in lower for k in ["급식", "식단"]):
        contexts = get_context_for_query("급식 알레르기 표시")
        return "응, 급식 식단표에는 **알레르기 유발 식품 표시가 함께 제공돼!** 확인하고 먹으면 돼.", contexts

    if any(k in lower for k in ["새치기", "끼어", "줄"] ) and "급식" in lower:
        contexts = get_context_for_query("급식 새치기 규정")
        return "안 돼! 급식 줄 새치기는 **절대 허용되지 않아.** 적발되면 줄 맨 뒤로 가야 하고 선생님 지도를 받을 수 있어.", contexts

    if "휴대폰" in lower and any(k in lower for k in ["언제", "반납", "걷", "수거"]):
        contexts = get_context_for_query("전자기기 반납 쉬는시간 스마트폰")
        return "휴대폰은 **아침 조례 시간에 반납**하고, **종례 때 하교하면서 돌려받아!**", contexts

    if any(k in lower for k in ["보건실", "아프면 어디", "몸 아프"]):
        contexts = get_context_for_query("보건실 이용 및 위치")
        return "보건실은 **본관 2층**이야! 수업 시간이나 쉬는 시간, 점심시간에도 몸이 아프면 이용할 수 있어.", contexts

    if any(k in lower for k in ["학생회실", "학생회 실"]):
        contexts = get_context_for_query("학생회실 위치 및 규칙")
        return "학생회실은 **본관 3층**이야! 다만 학생회 임원이 없으면 문이 잠겨 있을 수 있어.", contexts

    if any(k in lower for k in ["체육관", "강당", "운동장", "체육 어디서"]):
        contexts = get_context_for_query("체육관 강당 운동장 없음")
        return "우리 학교는 체육관이랑 운동장이 따로 없어! 그래서 교내 **탁구장, 헬스장, 당구 시설**을 주로 쓰고, 학년별로는 1학년 배드민턴, 2학년 볼링장, 3학년 농구장처럼 외부 장소도 이용해.", contexts

    if any(k in lower for k in ["방학식", "여름방학"]) and any(k in lower for k in ["언제", "몇일", "며칠"]):
        if "여름방학" in lower:
            contexts = get_context_for_query("여름방학 기간 방학식")
            return "여름방학은 **7월 22일부터** 시작이야! 그 전날인 **7월 21일이 방학식**이고, 방학식 끝나면 바로 여름방학 들어가.", contexts
        contexts = get_context_for_query("방학식 급식 및 수업")
        return "방학식은 **7월 21일**이야! 단축수업으로 일찍 끝나고, 급식은 없어.", contexts

    if any(k in lower for k in ["오늘 급식", "내일 급식"]) or (("급식" in lower or "식단" in lower) and is_asking_specific_day):
        contexts = get_context_for_query(f"{target_date_only.month}월 {target_date_only.day}일 급식")
        return build_lunch_response(target_date_only), contexts

    if any(k in lower for k in ["하교", "끝나", "몇시에", "몇 시에", "언제 끝"]):
        if is_asking_specific_day or "오늘" in lower or "내일" in lower:
            contexts = get_context_for_query("방학식 급식 및 수업 수업 시간")
            return build_dismissal_response(target_date_only), contexts

    if "급식 순서" in lower or ("급식" in lower and "순서" in lower):
        contexts = get_context_for_query("급식 배식 순서 학년 반별")
        return "급식은 기본적으로 **3학년 → 2학년 → 1학년** 순서로 먹어! 학년 안에서 반별 순서는 매달 정해지는 로테이션 기준으로 들어가.", contexts

    return None, []


# ==========================================
# 5. 🤖 실시간 대화 추론 엔진
# ==========================================
if user_input := st.chat_input(placeholder="서연 chatbot에게 물어보세요..."):
    with st.chat_message("user"):
        st.write(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input, "contexts": []})

    try:
        now = datetime.now()
        realtime_today = f"{now.strftime('%Y년 %m월 %d일')} {weekday_map[now.weekday()]}"
        target_date, is_asking_specific_day, explicit_date_mentioned = parse_target_date(user_input, now)
        target_date_only = target_date.date()

        is_asking_all_offdays = (
            any(p in user_input for p in [
                "쉬는 날", "쉬는날", "노는 날", "노는날", "안 가는 날", "안가는날",
                "휴일 목록", "쉬는 날짜", "쉬는날짜", "쉬는날들", "쉬는 날들"
            ])
            or ("쉬는" in user_input and any(w in user_input for w in ["전부", "모두", "다"]))
            or ("휴일" in user_input and any(w in user_input for w in ["전부", "모두", "목록"]))
        )

        if is_asking_all_offdays:
            full_response = (
                "쉬는 날 싹 다 정리해줄게! 🗓️\n"
                "- 여름방학: 7월 22일 ~ 8월 18일\n"
                "- 제헌절 휴업일: 7월 17일\n"
                "- 추석 연휴: 9월 24일 ~ 9월 27일\n"
                "- 대체공휴일: 10월 5일\n"
                "- 한글날: 10월 9일\n"
                "- 수능 재량휴업일: 11월 19일\n"
                "- 재량휴업일: 11월 20일\n"
                "- 성탄절: 12월 25일\n"
                "- 신정: 1월 1일\n"
                "- 겨울방학: 1월 9일 ~ 3월 1일\n"
                "- 그리고 매주 토요일, 일요일도 쉬는 날이야! 🛌"
            )
            contexts = ["학사일정 전체 휴무일 조회"]
        elif "요일" in user_input and is_asking_specific_day:
            weekday_name = weekday_map[target_date.weekday()]
            full_response = f"{target_date.strftime('%m월 %d일')}은 **{weekday_name}**이야!"
            off_reason = get_day_off_reason(target_date_only)
            if off_reason:
                full_response += f" ({off_reason}이라 학교는 쉬는 날이야!)"
            contexts = ["요일 계산"]
        else:
            event_keyword_matches = find_events_by_keyword(user_input)
            if event_keyword_matches and not explicit_date_mentioned and not any(k in user_input for k in ["급식", "하교", "끝나"]):
                lines = []
                seen = set()
                for ev in event_keyword_matches:
                    key = (ev["name"], ev["date"])
                    if key in seen:
                        continue
                    seen.add(key)
                    lines.append(f"**{ev['date'].strftime('%m월 %d일')}**이 {ev['name']}이야!")
                full_response = "\n".join(lines)
                contexts = ["학사일정 이벤트명→날짜 역질의"]
            elif explicit_date_mentioned and not any(k in user_input for k in ["급식", "하교", "끝나"]):
                event_name_found = find_event_name_by_date(explicit_date_mentioned)
                if event_name_found:
                    full_response = f"{explicit_date_mentioned.strftime('%m월 %d일')}은 {event_name_found}이야!"
                    contexts = ["학사일정 날짜→이벤트명 정질의"]
                else:
                    full_response, contexts = answer_common_queries(user_input, now, target_date_only, is_asking_specific_day)
            else:
                full_response, contexts = answer_common_queries(user_input, now, target_date_only, is_asking_specific_day)

            if not full_response:
                DYNAMIC_CONTEXT, matched_chunks = retrieve_relevant_context_openai(user_input, ALL_CHUNKS, EMBEDDING_MATRIX, top_n=4)
                SYSTEM_PROMPT = f"""
                당신은 서연중학교 학생들을 위한 친근한 학교생활 가이드 AI입니다.
                - 오늘 기준 날짜: {realtime_today}

                [학교 공식 규정 데이터베이스]
                {DYNAMIC_CONTEXT if DYNAMIC_CONTEXT else '사용자 질의와 일치하는 공식 규정이 없습니다.'}

                [중요 운영 지식]
                - 1교시 시작은 오전 8시 50분입니다.
                - 한 교시는 45분 수업, 쉬는 시간은 10분입니다.
                - 급식은 4교시 종료 직후 시작됩니다.
                - 급식 줄 새치기는 금지입니다.
                - 급식 식단표에는 알레르기 표시가 있습니다.
                - 7월 21일 방학식은 정규 7교시가 아니라 단축수업입니다.
                - 7월 21일 방학식에는 급식이 없습니다.
                - 방학식 다음 날부터 여름방학이 시작됩니다.

                [답변 규칙]
                1. 제공된 데이터베이스 내용에 기반해서만 대답하고 거짓 내용을 지어내지 마세요.
                2. 학사일정이나 이벤트를 안내할 때 '오늘'이라는 말을 반복적으로 남발하지 말고 자연스럽게 설명하세요.
                3. 데이터가 없어 모호한 질문의 경우 문장 가장 끝부분에 '[확인 필요]'를 정확하게 적으세요.
                4. 스마트폰 화면에서 읽기 편하게 최대 3~4줄 이내로 핵심만 요약해서 친구처럼 반말로 대답하세요.
                5. 학생 안내 AI처럼 자연스럽고 친절하게 답변하세요.
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
                        stream=True,
                    )
                    raw_response = ""
                    rendered = ""
                    for chunk in response_stream:
                        delta = chunk.choices[0].delta.content
                        if delta:
                            raw_response += delta
                            for ch in delta:
                                rendered += ch
                                response_container.markdown(rendered.replace("[확인 필요]", "").strip() + "▌")
                                time.sleep(0.008)
                    cleaned_display_response = raw_response.replace("[확인 필요]", "").strip()
                    response_container.markdown(cleaned_display_response)

                    if matched_chunks:
                        with st.expander("🔍 관련 규정 근거 보기"):
                            for source in matched_chunks:
                                st.markdown(f'<div class="evidence-box">{source}</div>', unsafe_allow_html=True)

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": cleaned_display_response,
                        "contexts": matched_chunks,
                    }
                )

                if "[확인 필요]" in raw_response:
                    save_unknown_question_csv(user_input)
                    st.toast("💾 추가 검토가 필요한 질문은 보관함에 기록되었습니다.", icon="💡")
                st.stop()

        with st.chat_message("assistant"):
            response_container = st.empty()
            cleaned_display_response = (full_response or "").replace("[확인 필요]", "").strip()
            stream_text_like_chatgpt(response_container, cleaned_display_response)
            if contexts:
                with st.expander("🔍 관련 규정 근거 보기"):
                    for source in contexts:
                        st.markdown(f'<div class="evidence-box">{source}</div>', unsafe_allow_html=True)

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": cleaned_display_response,
                "contexts": contexts,
            }
        )

        if "[확인 필요]" in (full_response or ""):
            save_unknown_question_csv(user_input)
            st.toast("💾 추가 검토가 필요한 질문은 보관함에 기록되었습니다.", icon="💡")

    except Exception as e:
        st.error(f"오류가 발생했습니다: {e}")
