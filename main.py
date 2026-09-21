import streamlit as st
import requests
import plotly.express as px

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo


# --------------------------------------------------
# 기본 페이지 설정
# --------------------------------------------------

st.set_page_config(
    page_title="어제의 박스오피스",
    page_icon="🎬",
    layout="wide"
)


# --------------------------------------------------
# 화면 디자인
# --------------------------------------------------

st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(
            180deg,
            #f7f8ff 0%,
            #ffffff 55%,
            #f4f6fb 100%
        );
    }

    .main-title {
        text-align: center;
        font-size: 42px;
        font-weight: 800;
        margin-top: 10px;
        margin-bottom: 4px;
        color: #20243a;
    }

    .sub-title {
        text-align: center;
        font-size: 17px;
        color: #70758a;
        margin-bottom: 28px;
    }

    .number-one-box {
        background: white;
        border-radius: 24px;
        padding: 25px;
        margin-bottom: 20px;
        box-shadow: 0 8px 25px rgba(50, 55, 90, 0.08);
        border: 1px solid #eeeeF5;
    }

    .number-one-label {
        color: #777b91;
        font-size: 15px;
        font-weight: 700;
        margin-bottom: 5px;
    }

    .movie-name {
        font-size: 32px;
        font-weight: 800;
        color: #20243a;
        margin-bottom: 4px;
    }

    .movie-info {
        color: #777b91;
        font-size: 15px;
    }

    .metric-box {
        background: white;
        border-radius: 20px;
        padding: 22px;
        text-align: center;
        min-height: 135px;
        box-shadow: 0 7px 22px rgba(50, 55, 90, 0.08);
        border: 1px solid #eeeeF5;
    }

    .metric-title {
        color: #777b91;
        font-size: 15px;
        font-weight: 700;
        margin-bottom: 8px;
    }

    .metric-value {
        color: #20243a;
        font-size: 29px;
        font-weight: 800;
    }

    .section-title {
        font-size: 25px;
        font-weight: 800;
        color: #20243a;
        margin-top: 35px;
        margin-bottom: 12px;
    }

    .building-guide {
        background: #20243a;
        color: white;
        padding: 15px 20px;
        border-radius: 16px;
        margin-bottom: 15px;
        font-size: 15px;
    }

    .help-box {
        background: #fff8e8;
        border: 1px solid #f0dca8;
        border-radius: 18px;
        padding: 20px;
        color: #5f5134;
        margin-top: 20px;
        line-height: 1.7;
    }

    .footer {
        text-align: center;
        color: #999daf;
        font-size: 13px;
        margin-top: 40px;
        padding-bottom: 20px;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# --------------------------------------------------
# 제목
# --------------------------------------------------

st.markdown(
    '<div class="main-title">🎬 어제의 박스오피스</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="sub-title">영화 관객수를 건물의 높이처럼 한눈에 비교해 보세요 🏢</div>',
    unsafe_allow_html=True
)


# --------------------------------------------------
# 한국 시간 기준으로 어제 날짜 계산
# --------------------------------------------------

KOREA_TZ = ZoneInfo("Asia/Seoul")

now_korea = datetime.now(KOREA_TZ)

yesterday = now_korea.date() - timedelta(days=1)

target_dt = yesterday.strftime("%Y%m%d")

display_date = yesterday.strftime("%Y년 %m월 %d일")


# --------------------------------------------------
# KOBIS 인증키 가져오기
# --------------------------------------------------

try:
    KOBIS_KEY = st.secrets["KOBIS_KEY"]

except Exception:
    st.error("🔐 KOBIS 인증키를 찾을 수 없습니다.")

    st.markdown(
        """
        <div class="help-box">
        <b>다음 내용을 확인해 주세요.</b><br><br>

        ① Streamlit Cloud에서 <b>Settings → Secrets</b>로 이동하세요.<br>

        ② 아래처럼 입력하세요.<br><br>

        <code>KOBIS_KEY = "여기에_본인의_KOBIS_인증키"</code><br><br>

        ③ 저장한 뒤 앱을 다시 실행하세요.<br><br>

        ⚠️ 인증키를 <b>main.py 코드 안에 직접 입력하지 마세요.</b>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.stop()


# --------------------------------------------------
# KOBIS API 주소
# --------------------------------------------------

API_URL = (
    "https://www.kobis.or.kr/"
    "kobisopenapi/webservice/rest/boxoffice/"
    "searchDailyBoxOfficeList.json"
)


# --------------------------------------------------
# API 요청
# --------------------------------------------------

params = {
    "key": KOBIS_KEY,
    "targetDt": target_dt
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

    st.markdown(
        """
        <div class="help-box">
        <b>확인할 것</b><br>
        • 인터넷 연결 상태<br>
        • KOBIS API 서버 상태<br>
        • 잠시 후 다시 실행해 보기
        </div>
        """,
        unsafe_allow_html=True
    )

    st.stop()

except requests.exceptions.RequestException as e:

    st.error("🌐 KOBIS API에 연결하지 못했습니다.")

    st.markdown(
        f"""
        <div class="help-box">
        <b>확인할 것</b><br>
        • KOBIS API 주소가 정상인지<br>
        • Streamlit Cloud의 인터넷 연결 상태<br>
        • 잠시 후 다시 실행해 보기<br><br>

        <b>오류 내용:</b> {e}
        </div>
        """,
        unsafe_allow_html=True
    )

    st.stop()

except ValueError:

    st.error("📦 KOBIS에서 정상적인 데이터를 받지 못했습니다.")

    st.markdown(
        """
        <div class="help-box">
        <b>확인할 것</b><br>
        • KOBIS API 서버 상태<br>
        • 인증키가 정상인지<br>
        • 잠시 후 다시 실행해 보기
        </div>
        """,
        unsafe_allow_html=True
    )

    st.stop()


# --------------------------------------------------
# KOBIS API 오류 확인
# --------------------------------------------------

if "faultInfo" in data:

    fault_info = data["faultInfo"]

    error_code = fault_info.get(
        "errorCode",
        "알 수 없음"
    )

    error_message = fault_info.get(
        "errorMessage",
        "KOBIS API 오류가 발생했습니다."
    )

    st.error("🔑 KOBIS API 인증 또는 요청 오류가 발생했습니다.")

    st.markdown(
        f"""
        <div class="help-box">
        <b>무엇을 확인해야 하나요?</b><br><br>

        • Streamlit Cloud의 <b>Secrets</b>에
        <code>KOBIS_KEY</code>가 있는지 확인하세요.<br>

        • 인증키를 복사할 때 앞뒤에 불필요한 공백이 없는지 확인하세요.<br>

        • KOBIS에서 발급받은 인증키가 맞는지 확인하세요.<br>

        • 잠시 후 다시 실행해 보세요.<br><br>

        <b>KOBIS 오류 코드:</b> {error_code}<br>
        <b>KOBIS 오류 메시지:</b> {error_message}
        </div>
        """,
        unsafe_allow_html=True
    )

    st.stop()


# --------------------------------------------------
# boxOfficeResult 확인
# --------------------------------------------------

if "boxOfficeResult" not in data:

    st.error("⚠️ KOBIS 응답에서 boxOfficeResult를 찾을 수 없습니다.")

    st.markdown(
        """
        <div class="help-box">
        KOBIS API 응답 형식이 예상과 다릅니다.<br><br>

        <b>확인할 것</b><br>
        • KOBIS API 서버 상태<br>
        • API 요청 주소<br>
        • 인증키<br>
        • 잠시 후 다시 실행하기
        </div>
        """,
        unsafe_allow_html=True
    )

    st.stop()


box_office_result = data["boxOfficeResult"]


# --------------------------------------------------
# 영화 목록 가져오기
# --------------------------------------------------

movie_list = box_office_result.get(
    "dailyBoxOfficeList",
    []
)


# --------------------------------------------------
# 영화 목록이 없는 경우
# --------------------------------------------------

if not movie_list:

    st.warning("🎬 해당 날짜의 영화 목록이 없습니다.")

    st.markdown(
        f"""
        <div class="help-box">
        <b>조회 날짜:</b> {display_date}<br><br>

        <b>다음 사항을 확인해 주세요.</b><br>

        • KOBIS에서 해당 날짜의 일일 박스오피스가 집계되었는지<br>
        • API 인증키가 정상인지<br>
        • KOBIS API 서버에 문제가 없는지<br>
        • 잠시 후 다시 실행해 보기
        </div>
        """,
        unsafe_allow_html=True
    )

    st.stop()


# --------------------------------------------------
# 문자열 숫자를 정수로 변환하는 함수
# --------------------------------------------------

def to_int(value):
    try:
        return int(
            str(value)
            .replace(",", "")
            .strip()
        )

    except (ValueError, TypeError):
        return 0


# --------------------------------------------------
# 영화 데이터 정리
# --------------------------------------------------

movies = []

for movie in movie_list:

    movies.append(
        {
            "순위": to_int(movie.get("rank")),
            "영화명": movie.get(
                "movieNm",
                "영화명 없음"
            ),
            "개봉일": movie.get(
                "openDt",
                ""
            ),
            "관객수": to_int(
                movie.get("audiCnt")
            ),
            "누적관객": to_int(
                movie.get("audiAcc")
            ),
            "스크린수": to_int(
                movie.get("scrnCnt")
            )
        }
    )


# --------------------------------------------------
# 순위순으로 정렬
# --------------------------------------------------

movies = sorted(
    movies,
    key=lambda x: x["순위"]
)


# --------------------------------------------------
# 1위 영화 정보
# --------------------------------------------------

first_movie = movies[0]

first_movie_name = first_movie["영화명"]
first_audience = first_movie["관객수"]
first_total = first_movie["누적관객"]
first_screens = first_movie["스크린수"]


# --------------------------------------------------
# 날짜 표시
# --------------------------------------------------

st.caption(
    f"📅 조회 날짜: {display_date} · 한국 시간 기준 '어제'"
)


# --------------------------------------------------
# 1위 영화 표시
# --------------------------------------------------

st.markdown(
    """
    <div class="number-one-box">
        <div class="number-one-label">
            🏆 어제의 박스오피스 1위
        </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    f"""
        <div class="movie-name">
            🥇 {first_movie_name}
        </div>

        <div class="movie-info">
            개봉일 {first_movie["개봉일"]}
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


# --------------------------------------------------
# 1위 영화 지표 카드 3개
# --------------------------------------------------

card1, card2, card3 = st.columns(3)


with card1:

    st.markdown(
        f"""
        <div class="metric-box">
            <div class="metric-title">
                🎟️ 어제 관객수
            </div>

            <div class="metric-value">
                {first_audience:,}명
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


with card2:

    st.markdown(
        f"""
        <div class="metric-box">
            <div class="metric-title">
                👥 누적 관객수
            </div>

            <div class="metric-value">
                {first_total:,}명
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


with card3:

    st.markdown(
        f"""
        <div class="metric-box">
            <div class="metric-title">
                🎞️ 스크린 수
            </div>

            <div class="metric-value">
                {first_screens:,}개
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


# --------------------------------------------------
# 관객수 TOP 5
# --------------------------------------------------

top5 = sorted(
    movies,
    key=lambda x: x["관객수"],
    reverse=True
)[:5]


# --------------------------------------------------
# 건물 높이 그래프 제목
# --------------------------------------------------

st.markdown(
    '<div class="section-title">🏢 관객수 TOP 5 · 빌딩 높이로 비교</div>',
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="building-guide">
        💡 막대가 높을수록 관객수가 많습니다.
        <b>관객수가 많을수록 더 높은 건물</b>이라고 생각해 보세요!
    </div>
    """,
    unsafe_allow_html=True
)


# --------------------------------------------------
# 그래프 데이터
# --------------------------------------------------

chart_names = []

chart_audience = []

for movie in top5:

    chart_names.append(
        f'{movie["순위"]}위 · {movie["영화명"]}'
    )

    chart_audience.append(
        movie["관객수"]
    )


# --------------------------------------------------
# 막대그래프 생성
# --------------------------------------------------

fig = px.bar(
    x=chart_names,
    y=chart_audience,
    text=chart_audience,
    labels={
        "x": "영화",
        "y": "관객수(명)"
    },
    title="어제 관객수 TOP 5"
)


# --------------------------------------------------
# 그래프 세부 디자인
# --------------------------------------------------

fig.update_traces(
    texttemplate="%{text:,}명",
    textposition="outside",
    width=0.55,
    hovertemplate=(
        "<b>%{x}</b><br>"
        "관객수: %{y:,}명"
        "<extra></extra>"
    )
)


fig.update_layout(
    height=500,
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(
        family="Arial, sans-serif",
        size=14
    ),
    title=dict(
        font=dict(size=22)
    ),
    xaxis=dict(
        title="",
        tickangle=-15
    ),
    yaxis=dict(
        title="관객수(명)",
        gridcolor="rgba(100,100,100,0.12)",
        rangemode="tozero"
    ),
    margin=dict(
        l=50,
        r=30,
        t=80,
        b=100
    ),
    showlegend=False
)


st.plotly_chart(
    fig,
    use_container_width=True
)


# --------------------------------------------------
# 전체 박스오피스 표
# --------------------------------------------------

st.markdown(
    '<div class="section-title">📋 전체 박스오피스</div>',
    unsafe_allow_html=True
)


table_data = []

for movie in movies:

    table_data.append(
        {
            "순위": movie["순위"],
            "영화명": movie["영화명"],
            "개봉일": movie["개봉일"],
            "관객수": f'{movie["관객수"]:,}명',
            "누적관객": f'{movie["누적관객"]:,}명',
            "스크린수": f'{movie["스크린수"]:,}개'
        }
    )


st.dataframe(
    table_data,
    use_container_width=True,
    hide_index=True,
    column_config={
        "순위": st.column_config.NumberColumn(
            "순위",
            format="%d위"
        ),
        "영화명": st.column_config.TextColumn(
            "영화명",
            width="large"
        ),
        "개봉일": st.column_config.TextColumn(
            "개봉일"
        ),
        "관객수": st.column_config.TextColumn(
            "관객수"
        ),
        "누적관객": st.column_config.TextColumn(
            "누적관객"
        ),
        "스크린수": st.column_config.TextColumn(
            "스크린수"
        )
    }
)


# --------------------------------------------------
# 하단 출처
# --------------------------------------------------

st.markdown(
    """
    <div class="footer">
        데이터 출처: 영화관입장권통합전산망(KOBIS) 일일 박스오피스 API<br>
        조회 날짜는 한국 시간(Asia/Seoul)을 기준으로 자동 계산됩니다.
    </div>
    """,
    unsafe_allow_html=True
)
