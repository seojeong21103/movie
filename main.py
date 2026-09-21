import streamlit as st
import requests
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import pandas as pd
import html

st.set_page_config(
    page_title="어제의 박스오피스 ✨",
    page_icon="🎬",
    layout="wide"
)

# =========================
# 예쁜 반짝이 디자인
# =========================
st.markdown("""
<style>
.stApp {
    background:
        radial-gradient(circle at 10% 10%, rgba(255,180,220,.35), transparent 22%),
        radial-gradient(circle at 90% 15%, rgba(180,170,255,.35), transparent 22%),
        radial-gradient(circle at 50% 90%, rgba(255,220,150,.25), transparent 25%),
        linear-gradient(135deg,#fff8fc 0%,#f5f1ff 50%,#fffaf4 100%);
}

.stApp::before {
    content: "✦  ✧   ✨    ⋆   ✦      ✧   ✨    ⋆   ✦";
    position: fixed;
    top: 8%;
    left: 3%;
    width: 94%;
    font-size: 22px;
    letter-spacing: 25px;
    color: rgba(255,160,205,.45);
    pointer-events: none;
    z-index: 0;
    animation: sparkle 4s ease-in-out infinite;
}

.stApp::after {
    content: "✨   ✦    ⋆     ✧    ✨     ✦    ⋆";
    position: fixed;
    bottom: 8%;
    left: 5%;
    width: 90%;
    font-size: 18px;
    letter-spacing: 30px;
    color: rgba(150,130,255,.35);
    pointer-events: none;
    z-index: 0;
    animation: sparkle2 5s ease-in-out infinite;
}

@keyframes sparkle {
    0%,100% { opacity:.3; transform:translateY(0); }
    50% { opacity:1; transform:translateY(8px); }
}

@keyframes sparkle2 {
    0%,100% { opacity:.2; transform:translateY(0); }
    50% { opacity:.9; transform:translateY(-8px); }
}

.main-title {
    text-align:center;
    font-size:3.2rem;
    font-weight:900;
    margin-top:15px;
    margin-bottom:5px;

    background:linear-gradient(
        90deg,
        #ff5c9a,
        #9b6cff,
        #ff75b5,
        #8b72ff,
        #ff5c9a
    );

    background-size:300% auto;

    -webkit-background-clip:text;
    -webkit-text-fill-color:transparent;

    animation:titleGlow 4s linear infinite;
}

@keyframes titleGlow {
    0% { background-position:0% center; }
    100% { background-position:300% center; }
}

.sub-title {
    text-align:center;
    color:#777080;
    font-size:1.05rem;
    margin-bottom:30px;
}

.winner-card {
    position:relative;
    overflow:hidden;

    background:rgba(255,255,255,.92);
    border-radius:28px;
    padding:30px;
    margin-bottom:22px;

    border:1px solid rgba(255,190,220,.7);

    box-shadow:
        0 10px 35px rgba(120,80,150,.12),
        0 0 25px rgba(255,150,205,.12);

    transition:.3s;
}

.winner-card:hover {
    transform:translateY(-4px);
    box-shadow:
        0 15px 40px rgba(120,80,150,.18),
        0 0 35px rgba(255,150,205,.22);
}

.winner-card::after {
    content:"✦";
    position:absolute;
    top:15px;
    right:25px;
    font-size:28px;
    color:#ff8fbd;
    animation:twinkle 1.8s infinite;
}

@keyframes twinkle {
    0%,100% {
        opacity:.2;
        transform:scale(.8) rotate(0deg);
    }
    50% {
        opacity:1;
        transform:scale(1.25) rotate(20deg);
    }
}

.winner-rank {
    color:#ff5c98;
    font-size:.95rem;
    font-weight:800;
    letter-spacing:1px;
}

.winner-title {
    font-size:2.1rem;
    font-weight:900;
    color:#29243d;
    margin:5px 0 8px 0;
}

.winner-info {
    color:#777;
    font-size:.95rem;
}

.metric-card {
    position:relative;
    overflow:hidden;

    background:rgba(255,255,255,.94);
    border-radius:22px;
    padding:22px;
    text-align:center;

    border:1px solid #eadff5;

    box-shadow:
        0 7px 22px rgba(80,60,120,.08);

    transition:.3s;
}

.metric-card:hover {
    transform:translateY(-5px);
    box-shadow:
        0 12px 30px rgba(100,70,150,.15),
        0 0 20px rgba(255,180,220,.2);
}

.metric-card::before {
    content:"✧";
    position:absolute;
    top:8px;
    right:14px;
    color:#ff9fc7;
    font-size:18px;
    animation:twinkle 2s infinite;
}

.metric-label {
    color:#888;
    font-size:.9rem;
    margin-bottom:7px;
}

.metric-value {
    color:#29243d;
    font-size:1.65rem;
    font-weight:900;
}

.section-title {
    color:#29243d;
    font-size:1.4rem;
    font-weight:900;
    margin-top:32px;
    margin-bottom:15px;
}

.help-box {
    background:rgba(255,255,255,.92);
    border-radius:20px;
    padding:23px;
    border:1px solid #eadff5;
    color:#555;
    line-height:1.7;
    box-shadow:0 6px 20px rgba(80,60,120,.07);
}

[data-testid="stDataFrame"] {
    border-radius:18px;
    overflow:hidden;
    box-shadow:0 7px 25px rgba(80,60,120,.08);
}

[data-testid="stArrowVegaLiteChart"] {
    background:rgba(255,255,255,.75);
    border-radius:20px;
    padding:12px;
}

.footer {
    text-align:center;
    color:#999;
    font-size:.85rem;
    margin-top:40px;
    padding-bottom:25px;
}

.block-container {
    padding-top:2rem;
    padding-bottom:2rem;
}

@media (max-width:768px) {
    .main-title {
        font-size:2.3rem;
    }

    .winner-title {
        font-size:1.6rem;
    }

    .metric-value {
        font-size:1.25rem;
    }
}
</style>
""", unsafe_allow_html=True)


# =========================
# 한국 시간 기준 어제 계산
# =========================

KST = ZoneInfo("Asia/Seoul")

now_kst = datetime.now(KST)
yesterday_kst = now_kst - timedelta(days=1)

target_date = yesterday_kst.strftime("%Y%m%d")
display_date = yesterday_kst.strftime("%Y년 %m월 %d일")


# =========================
# KOBIS API 주소
# =========================

API_URL = (
    "https://www.kobis.or.kr/"
    "kobisopenapi/webservice/rest/boxoffice/"
    "searchDailyBoxOfficeList.json"
)


# =========================
# 제목
# =========================

st.markdown(
    '<div class="main-title">✨ 🎬 어제의 박스오피스 ✨</div>',
    unsafe_allow_html=True
)

st.markdown(
    f'<div class="sub-title">✦ {display_date} · KOBIS 일일 박스오피스 ✦</div>',
    unsafe_allow_html=True
)


# =========================
# Secrets에서 API 키 가져오기
# =========================

try:
    api_key = st.secrets["KOBIS_KEY"]

except Exception:

    st.error("🔑 KOBIS 인증키를 찾을 수 없습니다.")

    st.markdown("""
    <div class="help-box">

    <b>✨ 확인해 주세요</b><br><br>

    Streamlit Cloud의 <b>Settings → Secrets</b>에<br><br>

    <code>KOBIS_KEY = "본인의_인증키"</code><br><br>

    형식으로 입력되어 있는지 확인하세요.

    </div>
    """, unsafe_allow_html=True)

    st.stop()


# =========================
# KOBIS API 요청
# =========================

params = {
    "key": api_key,
    "targetDt": target_date
}

try:

    response = requests.get(
        API_URL,
        params=params,
        timeout=15
    )

    response.raise_for_status()

    data = response.json()

except requests.exceptions.Timeout:

    st.error("⏱️ KOBIS API 응답 시간이 초과되었습니다.")

    st.markdown("""
    <div class="help-box">
    <b>확인할 것</b><br><br>
    • 인터넷 연결 상태를 확인하세요.<br>
    • 잠시 후 새로고침하세요.<br>
    • KOBIS 서버가 일시적으로 응답하지 않을 수 있습니다.
    </div>
    """, unsafe_allow_html=True)

    st.stop()

except requests.exceptions.RequestException:

    st.error("🌐 KOBIS API에 연결하지 못했습니다.")

    st.markdown("""
    <div class="help-box">
    <b>확인할 것</b><br><br>
    • 인터넷 연결 상태를 확인하세요.<br>
    • KOBIS API 주소를 확인하세요.<br>
    • 잠시 후 다시 실행하세요.
    </div>
    """, unsafe_allow_html=True)

    st.stop()

except ValueError:

    st.error("📦 KOBIS에서 올바른 데이터를 받지 못했습니다.")

    st.markdown("""
    <div class="help-box">
    <b>확인할 것</b><br><br>
    • KOBIS API 서버 상태를 확인하세요.<br>
    • 잠시 후 다시 실행하세요.
    </div>
    """, unsafe_allow_html=True)

    st.stop()


# =========================
# KOBIS 오류 확인
# =========================

if "faultInfo" in data:

    fault_info = data["faultInfo"]

    reason = fault_info.get(
        "message",
        "KOBIS API에서 오류가 발생했습니다."
    )

    st.error("🔑 KOBIS API 요청에 문제가 있습니다.")

    st.markdown(
        f"""
        <div class="help-box">

        <b>API 오류 내용</b><br>
        {html.escape(str(reason))}

        <br><br>

        <b>✨ 확인할 것</b><br>
        • Secrets의 KOBIS_KEY가 정확한지 확인하세요.<br>
        • 인증키 앞뒤에 공백이 없는지 확인하세요.<br>
        • KOBIS 인증키가 활성화되어 있는지 확인하세요.

        </div>
        """,
        unsafe_allow_html=True
    )

    st.stop()


# =========================
# 박스오피스 데이터
# =========================

try:

    boxoffice_result = data["boxOfficeResult"]
    movie_list = boxoffice_result["dailyBoxOfficeList"]

except (KeyError, TypeError):

    st.error("📭 박스오피스 데이터를 찾을 수 없습니다.")

    st.markdown("""
    <div class="help-box">

    <b>✨ 확인할 것</b><br><br>

    • KOBIS API 응답 형식을 확인하세요.<br>
    • 해당 날짜의 데이터가 아직 제공되지 않았을 수 있습니다.<br>
    • 잠시 후 다시 실행하세요.

    </div>
    """, unsafe_allow_html=True)

    st.stop()


# =========================
# 영화 목록이 없는 경우
# =========================

if not movie_list:

    st.warning("🎬 해당 날짜의 영화 목록이 없습니다.")

    st.markdown(
        f"""
        <div class="help-box">

        <b>{display_date}</b>의 박스오피스 데이터가 비어 있습니다.<br><br>

        <b>✨ 확인할 것</b><br>

        • 날짜가 올바른지 확인하세요.<br>
        • KOBIS에서 해당 날짜의 데이터가 제공되는지 확인하세요.<br>
        • 잠시 후 다시 실행하세요.

        </div>
        """,
        unsafe_allow_html=True
    )

    st.stop()


# =========================
# 숫자 변환
# =========================

for movie in movie_list:

    movie["rank"] = int(movie.get("rank", 0))

    movie["audiCnt"] = int(
        movie.get("audiCnt", 0)
    )

    movie["audiAcc"] = int(
        movie.get("audiAcc", 0)
    )

    movie["scrnCnt"] = int(
        movie.get("scrnCnt", 0)
    )


# =========================
# 1위 영화
# =========================

first_movie = movie_list[0]

first_movie_name = first_movie.get(
    "movieNm",
    "영화명 없음"
)

first_audi = first_movie.get(
    "audiCnt",
    0
)

first_acc = first_movie.get(
    "audiAcc",
    0
)

first_screen = first_movie.get(
    "scrnCnt",
    0
)

first_open = first_movie.get(
    "openDt",
    "-"
)

if len(first_open) == 8:

    first_open = (
        f"{first_open[:4]}."
        f"{first_open[4:6]}."
        f"{first_open[6:]}"
    )


# =========================
# 1위 카드
# =========================

st.markdown(
    f"""
    <div class="winner-card">

        <div class="winner-rank">
            ✨ 🏆 DAILY BOX OFFICE #1 ✨
        </div>

        <div class="winner-title">
            {html.escape(first_movie_name)}
        </div>

        <div class="winner-info">
            🎞️ 개봉일 · {first_open}
        </div>

    </div>
    """,
    unsafe_allow_html=True
)


# =========================
# 지표 카드
# =========================

col1, col2, col3 = st.columns(3)

with col1:

    st.markdown(
        f"""
        <div class="metric-card">

            <div class="metric-label">
                ✨ 어제 관객수
            </div>

            <div class="metric-value">
                {first_audi:,}명
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

with col2:

    st.markdown(
        f"""
        <div class="metric-card">

            <div class="metric-label">
                ✦ 누적 관객수
            </div>

            <div class="metric-value">
                {first_acc:,}명
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

with col3:

    st.markdown(
        f"""
        <div class="metric-card">

            <div class="metric-label">
                ✧ 스크린수
            </div>

            <div class="metric-value">
                {first_screen:,}개
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


# =========================
# 관객수 TOP 5
# =========================

top5 = sorted(
    movie_list,
    key=lambda x: x["audiCnt"],
    reverse=True
)[:5]

chart_df = pd.DataFrame({
    "영화": [
        movie["movieNm"]
        for movie in top5
    ],
    "관객수": [
        movie["audiCnt"]
        for movie in top5
    ]
})

chart_df = chart_df.set_index("영화")

st.markdown(
    '<div class="section-title">✨ 📊 관객수 TOP 5</div>',
    unsafe_allow_html=True
)

st.bar_chart(
    chart_df,
    y="관객수",
    use_container_width=True
)


# =========================
# 전체 박스오피스 표
# =========================

table_data = []

for movie in movie_list:

    open_date = movie.get(
        "openDt",
        "-"
    )

    if len(open_date) == 8:

        open_date = (
            f"{open_date[:4]}."
            f"{open_date[4:6]}."
            f"{open_date[6:]}"
        )

    table_data.append({
        "순위": movie.get("rank", 0),
        "영화명": movie.get("movieNm", "-"),
        "개봉일": open_date,
        "관객수": f'{movie.get("audiCnt", 0):,}명',
        "누적관객": f'{movie.get("audiAcc", 0):,}명',
        "스크린수": f'{movie.get("scrnCnt", 0):,}개'
    })

table_df = pd.DataFrame(table_data)

st.markdown(
    '<div class="section-title">🎞️ ✨ 전체 박스오피스</div>',
    unsafe_allow_html=True
)

st.dataframe(
    table_df,
    use_container_width=True,
    hide_index=True
)


# =========================
# 하단
# =========================

st.markdown(
    f"""
    <div class="footer">

        ✦ ✨ ✦ ✧ ✦ ✨ ✦<br><br>

        📅 조회 날짜 · {display_date}<br>
        🎬 데이터 제공 · KOBIS 영화관입장권통합전산망

    </div>
    """,
    unsafe_allow_html=True
)
