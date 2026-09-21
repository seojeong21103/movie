import streamlit as st
import requests
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import pandas as pd
import html


# =========================================================
# 1. 기본 페이지 설정
# =========================================================

st.set_page_config(
    page_title="어제의 박스오피스",
    page_icon="🎬",
    layout="wide"
)


# =========================================================
# 2. 예쁜 화면을 위한 CSS
# =========================================================

st.markdown("""
<style>
    /* 전체 배경 */
    .stApp {
        background: linear-gradient(135deg, #fff8fb 0%, #f7f4ff 100%);
    }

    /* 메인 제목 */
    .main-title {
        text-align: center;
        font-size: 3rem;
        font-weight: 800;
        margin-top: 10px;
        margin-bottom: 5px;
        background: linear-gradient(90deg, #ff5c8a, #8b6cff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .sub-title {
        text-align: center;
        color: #777;
        font-size: 1.05rem;
        margin-bottom: 30px;
    }

    /* 1위 영화 카드 */
    .winner-card {
        background: white;
        border-radius: 24px;
        padding: 28px;
        margin-bottom: 22px;
        box-shadow: 0 8px 25px rgba(80, 60, 120, 0.10);
        border: 1px solid #eee;
    }

    .winner-rank {
        color: #ff5c8a;
        font-size: 1rem;
        font-weight: 700;
    }

    .winner-title {
        font-size: 2rem;
        font-weight: 800;
        color: #29243d;
        margin: 5px 0 8px 0;
    }

    .winner-info {
        color: #777;
        font-size: 0.95rem;
    }

    /* 지표 카드 */
    .metric-card {
        background: white;
        border-radius: 20px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 6px 20px rgba(80, 60, 120, 0.08);
        border: 1px solid #eee;
    }

    .metric-label {
        color: #888;
        font-size: 0.9rem;
        margin-bottom: 7px;
    }

    .metric-value {
        color: #29243d;
        font-size: 1.65rem;
        font-weight: 800;
    }

    /* 섹션 제목 */
    .section-title {
        color: #29243d;
        font-size: 1.35rem;
        font-weight: 800;
        margin-top: 30px;
        margin-bottom: 15px;
    }

    /* 안내 박스 */
    .help-box {
        background: #fff;
        border-radius: 18px;
        padding: 22px;
        border: 1px solid #eadff5;
        color: #555;
        line-height: 1.7;
        box-shadow: 0 5px 18px rgba(80, 60, 120, 0.06);
    }

    /* 하단 */
    .footer {
        text-align: center;
        color: #999;
        font-size: 0.85rem;
        margin-top: 40px;
        padding-bottom: 20px;
    }

    /* 표 모서리 */
    [data-testid="stDataFrame"] {
        border-radius: 15px;
        overflow: hidden;
    }
</style>
""", unsafe_allow_html=True)


# =========================================================
# 3. 한국 시간 기준으로 '어제' 계산
# =========================================================
# Streamlit Cloud 서버가 한국 시간이 아닐 수도 있기 때문에
# 반드시 Asia/Seoul 시간대를 직접 지정한다.

KST = ZoneInfo("Asia/Seoul")

now_kst = datetime.now(KST)
yesterday_kst = now_kst - timedelta(days=1)

# KOBIS API가 요구하는 날짜 형식: YYYYMMDD
target_date = yesterday_kst.strftime("%Y%m%d")

# 화면에 보여줄 날짜
display_date = yesterday_kst.strftime("%Y년 %m월 %d일")


# =========================================================
# 4. KOBIS API 주소
# =========================================================

API_URL = (
    "https://www.kobis.or.kr/"
    "kobisopenapi/webservice/rest/boxoffice/"
    "searchDailyBoxOfficeList.json"
)


# =========================================================
# 5. 화면 제목
# =========================================================

st.markdown(
    '<div class="main-title">🎬 어제의 박스오피스</div>',
    unsafe_allow_html=True
)

st.markdown(
    f'<div class="sub-title">{display_date} · KOBIS 일일 박스오피스</div>',
    unsafe_allow_html=True
)


# =========================================================
# 6. API 인증키 가져오기
# =========================================================
# 실제 인증키는 코드에 넣지 않는다.
# Streamlit Cloud의 Secrets에서 KOBIS_KEY를 읽는다.

try:
    api_key = st.secrets["KOBIS_KEY"]
except Exception:
    st.error("🔑 KOBIS 인증키를 찾을 수 없습니다.")

    st.markdown("""
    <div class="help-box">
        <b>확인할 것</b><br><br>
        ① Streamlit Cloud의 앱 설정에서 <b>Secrets</b>를 열어 주세요.<br>
        ② 아래와 같이 입력되어 있는지 확인하세요.<br><br>

        <code>KOBIS_KEY = "발급받은_인증키"</code><br><br>

        ③ 인증키 이름이 정확히 <b>KOBIS_KEY</b>인지 확인하세요.
    </div>
    """, unsafe_allow_html=True)

    st.stop()


# =========================================================
# 7. KOBIS API 요청
# =========================================================

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

    # HTTP 오류가 발생했는지 확인
    response.raise_for_status()

    data = response.json()

except requests.exceptions.Timeout:
    st.error("⏱️ KOBIS API 응답 시간이 초과되었습니다.")

    st.markdown("""
    <div class="help-box">
        <b>확인할 것</b><br><br>
        • 인터넷 연결 상태를 확인하세요.<br>
        • 잠시 후 앱을 새로고침해 보세요.<br>
        • KOBIS API 서버가 일시적으로 응답하지 않는 경우도 있습니다.
    </div>
    """, unsafe_allow_html=True)

    st.stop()

except requests.exceptions.RequestException:
    st.error("🌐 KOBIS API에 연결하지 못했습니다.")

    st.markdown("""
    <div class="help-box">
        <b>확인할 것</b><br><br>
        • 인터넷 연결 상태를 확인하세요.<br>
        • KOBIS API 주소가 정상인지 확인하세요.<br>
        • 잠시 후 다시 실행해 보세요.
    </div>
    """, unsafe_allow_html=True)

    st.stop()

except ValueError:
    st.error("📦 KOBIS API에서 올바른 JSON 데이터를 받지 못했습니다.")

    st.markdown("""
    <div class="help-box">
        <b>확인할 것</b><br><br>
        • KOBIS API 서버의 응답 상태를 확인하세요.<br>
        • 잠시 후 다시 실행해 보세요.
    </div>
    """, unsafe_allow_html=True)

    st.stop()


# =========================================================
# 8. KOBIS API의 오류 응답 확인
# =========================================================
# 인증키가 틀려도 HTTP 상태코드는 200일 수 있다.
# 따라서 faultInfo가 있는지도 반드시 확인한다.

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
            {html.escape(str(reason))}<br><br>

            <b>확인할 것</b><br>
            • Streamlit Secrets의 <b>KOBIS_KEY</b>가 정확한지 확인하세요.<br>
            • 인증키 앞뒤에 불필요한 공백이 없는지 확인하세요.<br>
            • KOBIS에서 발급받은 API 키가 정상적으로 활성화되어 있는지 확인하세요.
        </div>
        """,
        unsafe_allow_html=True
    )

    st.stop()


# =========================================================
# 9. 박스오피스 데이터 가져오기
# =========================================================

try:
    boxoffice_result = data["boxOfficeResult"]
    movie_list = boxoffice_result["dailyBoxOfficeList"]

except (KeyError, TypeError):
    st.error("📭 박스오피스 데이터를 찾을 수 없습니다.")

    st.markdown("""
    <div class="help-box">
        <b>확인할 것</b><br><br>
        • KOBIS API의 응답 형식이 정상인지 확인하세요.<br>
        • 조회 날짜에 박스오피스 데이터가 아직 제공되지 않았을 수 있습니다.<br>
        • 잠시 후 다시 실행해 보세요.
    </div>
    """, unsafe_allow_html=True)

    st.stop()


# =========================================================
# 10. 영화 목록이 비어 있는 경우
# =========================================================

if not movie_list:

    st.warning("🎬 해당 날짜의 영화 목록이 없습니다.")

    st.markdown(
        f"""
        <div class="help-box">
            <b>{display_date}</b>의 박스오피스 데이터가 비어 있습니다.<br><br>

            <b>확인할 것</b><br>
            • 날짜가 올바른지 확인하세요.<br>
            • KOBIS에서 해당 날짜의 일일 박스오피스가 제공되는지 확인하세요.<br>
            • 잠시 후 다시 실행해 보세요.
        </div>
        """,
        unsafe_allow_html=True
    )

    st.stop()


# =========================================================
# 11. 숫자 데이터를 숫자로 변환
# =========================================================
# KOBIS API에서는 숫자도 문자열로 전달될 수 있으므로
# 그래프와 표에서 제대로 사용하기 위해 정수로 변환한다.

for movie in movie_list:
    movie["rank"] = int(movie.get("rank", 0))
    movie["audiCnt"] = int(movie.get("audiCnt", 0))
    movie["audiAcc"] = int(movie.get("audiAcc", 0))
    movie["scrnCnt"] = int(movie.get("scrnCnt", 0))
    movie["showCnt"] = int(movie.get("showCnt", 0))


# =========================================================
# 12. 1위 영화 가져오기
# =========================================================

first_movie = movie_list[0]

first_movie_name = first_movie.get("movieNm", "영화명 없음")
first_audi = first_movie.get("audiCnt", 0)
first_acc = first_movie.get("audiAcc", 0)
first_screen = first_movie.get("scrnCnt", 0)
first_open = first_movie.get("openDt", "-")

# 개봉일 보기 좋게 변경
if len(first_open) == 8:
    first_open = (
        f"{first_open[:4]}."
        f"{first_open[4:6]}."
        f"{first_open[6:]}"
    )


# =========================================================
# 13. 1위 영화 크게 표시
# =========================================================

st.markdown(
    f"""
    <div class="winner-card">
        <div class="winner-rank">🏆 DAILY BOX OFFICE #1</div>
        <div class="winner-title">{html.escape(first_movie_name)}</div>
        <div class="winner-info">
            개봉일 · {first_open}
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# 14. 지표 카드 3개
# =========================================================

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">어제 관객수</div>
            <div class="metric-value">{first_audi:,}명</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">누적 관객수</div>
            <div class="metric-value">{first_acc:,}명</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col3:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">스크린수</div>
            <div class="metric-value">{first_screen:,}개</div>
        </div>
        """,
        unsafe_allow_html=True
    )


# =========================================================
# 15. 관객수 상위 5편
# =========================================================

top5 = sorted(
    movie_list,
    key=lambda x: x["audiCnt"],
    reverse=True
)[:5]

chart_df = pd.DataFrame({
    "영화": [movie["movieNm"] for movie in top5],
    "관객수": [movie["audiCnt"] for movie in top5]
})

chart_df = chart_df.set_index("영화")


st.markdown(
    '<div class="section-title">📊 관객수 TOP 5</div>',
    unsafe_allow_html=True
)

st.bar_chart(
    chart_df,
    y="관객수",
    use_container_width=True
)


# =========================================================
# 16. 전체 영화 데이터를 표로 만들기
# =========================================================

table_data = []

for movie in movie_list:

    open_date = movie.get("openDt", "-")

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


# =========================================================
# 17. 전체 박스오피스 표
# =========================================================

st.markdown(
    '<div class="section-title">🎞️ 전체 박스오피스</div>',
    unsafe_allow_html=True
)

st.dataframe(
    table_df,
    use_container_width=True,
    hide_index=True
)


# =========================================================
# 18. 하단 안내
# =========================================================

st.markdown(
    f"""
    <div class="footer">
        📅 조회 날짜: {display_date}<br>
        데이터 제공: KOBIS 영화관입장권통합전산망
    </div>
    """,
    unsafe_allow_html=True
)
