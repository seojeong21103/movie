import streamlit as st
import requests
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import html


# ============================================================
# 1. 기본 설정
# ============================================================

st.set_page_config(
    page_title="🥒 어제의 박스오피스",
    page_icon="🥒",
    layout="wide"
)


# ============================================================
# 2. 화면 디자인
# ============================================================

st.markdown("""
<style>
    .main-title {
        text-align: center;
        font-size: 42px;
        font-weight: 800;
        margin-bottom: 5px;
    }

    .sub-title {
        text-align: center;
        color: #666;
        font-size: 17px;
        margin-bottom: 30px;
    }

    .movie-card {
        background: linear-gradient(135deg, #f7fff7, #eaffea);
        border-radius: 18px;
        padding: 24px;
        border: 2px solid #c9edc9;
        margin-bottom: 20px;
    }

    .movie-number {
        font-size: 20px;
        font-weight: 700;
        color: #348a34;
    }

    .movie-name {
        font-size: 28px;
        font-weight: 800;
        margin: 5px 0 15px 0;
    }

    .cucumber-chart {
        background: #f8fff8;
        border-radius: 18px;
        padding: 22px;
        border: 2px solid #d7efd7;
        margin-top: 10px;
    }

    .chart-row {
        margin-bottom: 20px;
    }

    .chart-label {
        font-weight: 700;
        font-size: 16px;
        margin-bottom: 6px;
    }

    .cucumber-bar {
        font-size: 23px;
        line-height: 1.4;
        letter-spacing: -5px;
        word-break: break-all;
    }

    .help-box {
        background: #fff9e6;
        border: 1px solid #f0d77b;
        border-radius: 14px;
        padding: 18px;
        margin: 15px 0;
    }

    .error-box {
        background: #fff0f0;
        border: 1px solid #f0aaaa;
        border-radius: 14px;
        padding: 18px;
        margin: 15px 0;
    }

    .success-box {
        background: #f1fff1;
        border: 1px solid #b9e6b9;
        border-radius: 14px;
        padding: 15px;
        margin: 15px 0;
    }
</style>
""", unsafe_allow_html=True)


# ============================================================
# 3. 제목
# ============================================================

st.markdown(
    '<div class="main-title">🥒 어제의 박스오피스</div>',
    unsafe_allow_html=True
)


# ============================================================
# 4. 한국 시간 기준으로 '어제' 계산
# ============================================================
# 배포 서버가 미국이나 다른 나라 시간이어도
# 한국 시간(KST)을 기준으로 날짜를 계산합니다.

KST = ZoneInfo("Asia/Seoul")

now_kst = datetime.now(KST)
yesterday_kst = now_kst - timedelta(days=1)

target_date = yesterday_kst.strftime("%Y%m%d")
display_date = yesterday_kst.strftime("%Y년 %m월 %d일")


st.markdown(
    f'<div class="sub-title">📅 {display_date} 기준 KOBIS 일일 박스오피스</div>',
    unsafe_allow_html=True
)


# ============================================================
# 5. KOBIS API 주소
# ============================================================

API_URL = (
    "https://www.kobis.or.kr/"
    "kobisopenapi/webservice/rest/boxoffice/"
    "searchDailyBoxOfficeList.json"
)


# ============================================================
# 6. Secrets에서 인증키 가져오기
# ============================================================
# Streamlit Cloud의 Secrets에
# KOBIS_KEY = "발급받은키"
# 형태로 저장해 두어야 합니다.
#
# 실제 인증키는 코드에 작성하지 않습니다.

try:
    KOBIS_KEY = st.secrets["KOBIS_KEY"]
except Exception:
    st.markdown("""
    <div class="error-box">
        <h3>🔑 KOBIS 인증키를 찾을 수 없습니다.</h3>
        <p><b>확인할 것:</b></p>
        <ol>
            <li>Streamlit Cloud의 앱 관리 화면으로 이동하세요.</li>
            <li>Settings → Secrets를 확인하세요.</li>
            <li>아래와 같은 형태로 입력했는지 확인하세요.</li>
        </ol>
        <pre>KOBIS_KEY = "여기에_발급받은_인증키"</pre>
        <p>인증키 자체는 main.py 코드에 넣지 마세요.</p>
    </div>
    """, unsafe_allow_html=True)

    st.stop()


# ============================================================
# 7. API 요청
# ============================================================

params = {
    "key": KOBIS_KEY,
    "targetDt": target_date
}


try:
    response = requests.get(
        API_URL,
        params=params,
        timeout=15
    )

except requests.exceptions.Timeout:
    st.markdown("""
    <div class="error-box">
        <h3>⏰ KOBIS API 요청 시간이 초과되었습니다.</h3>
        <p>
        인터넷 연결 상태를 확인한 뒤 잠시 후 다시 실행해 보세요.
        KOBIS 서버가 일시적으로 응답하지 않는 경우에도 발생할 수 있습니다.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.stop()

except requests.exceptions.RequestException as e:
    st.markdown(f"""
    <div class="error-box">
        <h3>🌐 KOBIS API에 연결하지 못했습니다.</h3>
        <p>
        인터넷 연결 또는 KOBIS API 서버 상태를 확인해 주세요.
        </p>
        <p>오류 내용: {html.escape(str(e))}</p>
    </div>
    """, unsafe_allow_html=True)

    st.stop()


# ============================================================
# 8. HTTP 상태 확인
# ============================================================

if response.status_code != 200:
    st.markdown(f"""
    <div class="error-box">
        <h3>🚨 API 서버에서 정상적인 응답을 받지 못했습니다.</h3>
        <p>HTTP 상태 코드: <b>{response.status_code}</b></p>
        <p>
        잠시 후 다시 실행하거나 KOBIS API 서버 상태를 확인해 주세요.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.stop()


# ============================================================
# 9. JSON 데이터 읽기
# ============================================================

try:
    data = response.json()

except ValueError:
    st.markdown("""
    <div class="error-box">
        <h3>📦 API 응답을 읽을 수 없습니다.</h3>
        <p>
        KOBIS API가 JSON 형식의 정상적인 데이터를 보내지 않았습니다.
        잠시 후 다시 시도해 주세요.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.stop()


# ============================================================
# 10. KOBIS faultInfo 확인
# ============================================================
# KOBIS는 인증키가 잘못되어도 HTTP 상태코드가 200일 수 있습니다.
# 따라서 faultInfo가 있는지 반드시 확인합니다.

if "faultInfo" in data and data["faultInfo"]:
    fault = data["faultInfo"]

    fault_code = fault.get("errorCode", "알 수 없음")
    fault_message = fault.get("message", "알 수 없는 오류")

    st.markdown(f"""
    <div class="error-box">
        <h3>🔑 KOBIS API에서 오류를 반환했습니다.</h3>
        <p><b>오류 코드:</b> {html.escape(str(fault_code))}</p>
        <p><b>오류 내용:</b> {html.escape(str(fault_message))}</p>

        <hr>

        <p><b>확인할 것:</b></p>
        <ul>
            <li>Streamlit Secrets의 <b>KOBIS_KEY</b> 이름이 정확한지 확인하세요.</li>
            <li>인증키에 불필요한 공백이나 따옴표가 들어가지 않았는지 확인하세요.</li>
            <li>KOBIS에서 발급받은 인증키가 정상적으로 활성화되어 있는지 확인하세요.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    st.stop()


# ============================================================
# 11. boxOfficeResult 확인
# ============================================================

if "boxOfficeResult" not in data:
    st.markdown("""
    <div class="error-box">
        <h3>📭 박스오피스 데이터를 찾을 수 없습니다.</h3>
        <p>
        KOBIS API 응답에 boxOfficeResult가 없습니다.
        API 응답이나 인증키 설정을 확인해 주세요.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.stop()


box_office = data["boxOfficeResult"]


# ============================================================
# 12. 영화 목록 가져오기
# ============================================================

movies = box_office.get("dailyBoxOfficeList", [])


if not movies:
    st.markdown(f"""
    <div class="help-box">
        <h3>📭 {display_date} 영화 목록이 없습니다.</h3>

        <p>
        KOBIS에서 해당 날짜의 일일 박스오피스 목록을 보내지 않았습니다.
        </p>

        <p><b>확인할 것:</b></p>

        <ul>
            <li>조회 날짜가 정상적으로 계산되었는지 확인하세요.</li>
            <li>KOBIS 일일 박스오피스에서 해당 날짜의 데이터가 존재하는지 확인하세요.</li>
            <li>인증키가 정상인지 확인하세요.</li>
            <li>잠시 후 다시 실행해 보세요.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    st.stop()


# ============================================================
# 13. 숫자를 보기 좋게 변환하는 함수
# ============================================================

def to_int(value):
    """KOBIS에서 문자열로 받은 숫자를 정수로 변환합니다."""
    try:
        return int(str(value).replace(",", ""))
    except (ValueError, TypeError):
        return 0


def comma(value):
    """숫자를 1,234 형태로 표시합니다."""
    return f"{to_int(value):,}"


# ============================================================
# 14. 데이터 정리
# ============================================================

for movie in movies:
    movie["rank_num"] = to_int(movie.get("rank"))
    movie["audiCnt_num"] = to_int(movie.get("audiCnt"))
    movie["audiAcc_num"] = to_int(movie.get("audiAcc"))
    movie["scrnCnt_num"] = to_int(movie.get("scrnCnt"))


# 순위 기준으로 정렬
movies.sort(key=lambda x: x["rank_num"])


# ============================================================
# 15. 1위 영화
# ============================================================

first_movie = movies[0]

first_name = first_movie.get("movieNm", "영화명 없음")
first_audience = first_movie["audiCnt_num"]
first_acc = first_movie["audiAcc_num"]
first_screen = first_movie["scrnCnt_num"]


# ============================================================
# 16. 1위 영화 크게 보여주기
# ============================================================

st.markdown(
    f"""
    <div class="movie-card">
        <div class="movie-number">🥒 어제의 박스오피스 1위</div>
        <div class="movie-name">🎬 {html.escape(first_name)}</div>
        <div>
            개봉일: {html.escape(first_movie.get("openDt", "-") or "-")}
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# 17. 지표 카드 3개
# ============================================================

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "🥒 어제 관객수",
        f"{first_audience:,}명"
    )

with col2:
    st.metric(
        "🥒 누적 관객수",
        f"{first_acc:,}명"
    )

with col3:
    st.metric(
        "🥒 스크린수",
        f"{first_screen:,}개"
    )


st.write("")


# ============================================================
# 18. 관객수 상위 5편 추출
# ============================================================

top5 = sorted(
    movies,
    key=lambda x: x["audiCnt_num"],
    reverse=True
)[:5]


# 가장 많은 관객수를 기준으로 오이 개수 계산
max_audience = max(
    movie["audiCnt_num"] for movie in top5
)

if max_audience <= 0:
    max_audience = 1


# ============================================================
# 19. 오이 막대그래프
# ============================================================

st.subheader("🥒 관객수 상위 5편")

st.caption(
    "오이 1개가 일정한 관객수를 의미하는 것은 아니며, "
    "상위 5편의 관객수를 서로 비교하기 위한 시각화입니다."
)

chart_html = '<div class="cucumber-chart">'

for movie in top5:

    name = html.escape(movie.get("movieNm", "영화명 없음"))
    audience = movie["audiCnt_num"]
    rank = movie["rank_num"]

    # 가장 큰 값은 최대 30개의 오이로 표현
    cucumber_count = max(
        1,
        round((audience / max_audience) * 30)
    )

    cucumbers = "🥒" * cucumber_count

    chart_html += f"""
    <div class="chart-row">

        <div class="chart-label">
            {rank}위 · {name}
            <span style="color:#777;">
                — {audience:,}명
            </span>
        </div>

        <div class="cucumber-bar">
            {cucumbers}
        </div>

    </div>
    """


chart_html += "</div>"

st.markdown(
    chart_html,
    unsafe_allow_html=True
)


# ============================================================
# 20. 전체 영화 데이터 표
# ============================================================

st.subheader("🎬 전체 박스오피스")

table_data = []

for movie in movies:

    table_data.append({
        "순위": movie["rank_num"],
        "영화명": movie.get("movieNm", "-"),
        "개봉일": movie.get("openDt", "-") or "-",
        "관객수": movie["audiCnt_num"],
        "누적관객": movie["audiAcc_num"],
        "스크린수": movie["scrnCnt_num"]
    })


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
            "영화명"
        ),
        "개봉일": st.column_config.TextColumn(
            "개봉일"
        ),
        "관객수": st.column_config.NumberColumn(
            "관객수",
            format="%d명"
        ),
        "누적관객": st.column_config.NumberColumn(
            "누적관객",
            format="%d명"
        ),
        "스크린수": st.column_config.NumberColumn(
            "스크린수",
            format="%d개"
        )
    }
)


# ============================================================
# 21. 데이터 정상 표시 안내
# ============================================================

st.markdown(
    f"""
    <div class="success-box">
        ✅ <b>{display_date}</b> KOBIS 박스오피스 데이터를 정상적으로 불러왔습니다.
        <br>
        조회 날짜: <b>{target_date}</b>
    </div>
    """,
    unsafe_allow_html=True
)
