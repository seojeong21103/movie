import streamlit as st
import requests
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import html


# ============================================================
# 1. 페이지 기본 설정
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


/* ========================================================
   오이 막대그래프
   ======================================================== */

.cucumber-chart {
    background: #f8fff8;
    border-radius: 18px;
    padding: 25px;
    border: 2px solid #d7efd7;
}

.cucumber-row {
    margin-bottom: 28px;
}

.cucumber-title {
    font-weight: 700;
    font-size: 16px;
    margin-bottom: 8px;
}

.cucumber-track {
    width: 100%;
    height: 44px;
    background: #edf7ed;
    border-radius: 24px;
    overflow: hidden;
    position: relative;
}

.cucumber-fill {
    height: 44px;
    min-width: 45px;
    border-radius: 24px;
    background: linear-gradient(
        90deg,
        #4caf50,
        #79c95b
    );
    position: relative;
    box-shadow:
        inset 0 3px 5px rgba(255,255,255,0.45),
        0 2px 4px rgba(0,0,0,0.12);
}

/* 오이의 하이라이트 */
.cucumber-fill::before {
    content: "";
    position: absolute;
    top: 8px;
    left: 14px;
    right: 14px;
    height: 5px;
    background: rgba(255,255,255,0.38);
    border-radius: 5px;
}

/* 오이의 작은 돌기 */
.cucumber-fill::after {
    content: "•  •  •  •  •  •  •  •";
    position: absolute;
    top: 14px;
    left: 22px;
    color: rgba(20,90,20,0.35);
    font-size: 10px;
    letter-spacing: 8px;
    white-space: nowrap;
}

.cucumber-value {
    font-weight: 700;
    color: #388e3c;
    margin-top: 6px;
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
# Streamlit Cloud 서버가 한국 시간이 아닐 수도 있기 때문에
# 반드시 한국 시간(KST)을 기준으로 날짜를 계산합니다.

KST = ZoneInfo("Asia/Seoul")

now_kst = datetime.now(KST)

yesterday_kst = now_kst - timedelta(days=1)

target_date = yesterday_kst.strftime("%Y%m%d")

display_date = yesterday_kst.strftime("%Y년 %m월 %d일")


st.markdown(
    f'<div class="sub-title">'
    f'📅 {display_date} 기준 KOBIS 일일 박스오피스'
    f'</div>',
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
# Streamlit Cloud의 Secrets에 아래처럼 입력해야 합니다.
#
# KOBIS_KEY = "발급받은_인증키"
#
# 실제 인증키는 이 코드에 작성하지 않습니다.

try:

    KOBIS_KEY = st.secrets["KOBIS_KEY"]

except Exception:

    st.markdown("""
    <div class="error-box">

        <h3>🔑 KOBIS 인증키를 찾을 수 없습니다.</h3>

        <p><b>다음 내용을 확인해 주세요.</b></p>

        <ol>
            <li>Streamlit Cloud에서 앱의 Settings를 엽니다.</li>
            <li>Secrets 메뉴로 들어갑니다.</li>
            <li><b>KOBIS_KEY</b>라는 이름으로 인증키를 등록합니다.</li>
        </ol>

        <pre>KOBIS_KEY = "여기에_발급받은_인증키"</pre>

        <p>
        ⚠️ 인증키는 <b>main.py 코드에 직접 입력하지 마세요.</b>
        </p>

    </div>
    """, unsafe_allow_html=True)

    st.stop()


# ============================================================
# 7. KOBIS API 요청
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
        KOBIS 서버가 늦게 응답했거나 일시적인 문제가 있을 수 있습니다.
        </p>

        <p>
        잠시 후 페이지를 새로고침해 주세요.
        </p>

    </div>
    """, unsafe_allow_html=True)

    st.stop()


except requests.exceptions.RequestException as e:

    st.markdown(
        f"""
        <div class="error-box">

            <h3>🌐 KOBIS API에 연결하지 못했습니다.</h3>

            <p>
            인터넷 연결 또는 KOBIS API 서버 상태를 확인해 주세요.
            </p>

            <p>
            오류 내용:
            {html.escape(str(e))}
            </p>

        </div>
        """,
        unsafe_allow_html=True
    )

    st.stop()


# ============================================================
# 8. HTTP 상태 코드 확인
# ============================================================

if response.status_code != 200:

    st.markdown(
        f"""
        <div class="error-box">

            <h3>🚨 API 서버에서 정상적인 응답을 받지 못했습니다.</h3>

            <p>
            HTTP 상태 코드:
            <b>{response.status_code}</b>
            </p>

            <p>
            잠시 후 다시 실행해 주세요.
            </p>

        </div>
        """,
        unsafe_allow_html=True
    )

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
        KOBIS API가 정상적인 JSON 데이터를 보내지 않았습니다.
        </p>

        <p>
        잠시 후 다시 실행해 주세요.
        </p>

    </div>
    """, unsafe_allow_html=True)

    st.stop()


# ============================================================
# 10. KOBIS faultInfo 확인
# ============================================================
# KOBIS는 인증키가 잘못되어도 HTTP 상태코드가 200일 수 있습니다.
# 따라서 faultInfo를 반드시 확인합니다.

if "faultInfo" in data and data["faultInfo"]:

    fault = data["faultInfo"]

    fault_code = fault.get(
        "errorCode",
        "알 수 없음"
    )

    fault_message = fault.get(
        "message",
        "알 수 없는 오류"
    )

    st.markdown(
        f"""
        <div class="error-box">

            <h3>🔑 KOBIS API에서 오류를 반환했습니다.</h3>

            <p>
            <b>오류 코드:</b>
            {html.escape(str(fault_code))}
            </p>

            <p>
            <b>오류 내용:</b>
            {html.escape(str(fault_message))}
            </p>

            <hr>

            <p><b>확인할 것:</b></p>

            <ul>
                <li>
                    Streamlit Secrets의 이름이
                    <b>KOBIS_KEY</b>인지 확인하세요.
                </li>

                <li>
                    인증키에 불필요한 공백이 들어가지 않았는지 확인하세요.
                </li>

                <li>
                    KOBIS에서 발급받은 인증키가 정상적으로 활성화되어
                    있는지 확인하세요.
                </li>
            </ul>

        </div>
        """,
        unsafe_allow_html=True
    )

    st.stop()


# ============================================================
# 11. boxOfficeResult 확인
# ============================================================

if "boxOfficeResult" not in data:

    st.markdown("""
    <div class="error-box">

        <h3>📭 박스오피스 데이터를 찾을 수 없습니다.</h3>

        <p>
        API 응답에 boxOfficeResult가 없습니다.
        </p>

        <p>
        인증키와 KOBIS API 상태를 확인해 주세요.
        </p>

    </div>
    """, unsafe_allow_html=True)

    st.stop()


box_office = data["boxOfficeResult"]


# ============================================================
# 12. 영화 목록 가져오기
# ============================================================

movies = box_office.get(
    "dailyBoxOfficeList",
    []
)


# 영화 목록이 비어 있을 경우
if not movies:

    st.markdown(
        f"""
        <div class="help-box">

            <h3>📭 영화 목록이 없습니다.</h3>

            <p>
            <b>{display_date}</b>의 일일 박스오피스 목록을
            가져오지 못했습니다.
            </p>

            <p><b>확인할 것:</b></p>

            <ul>
                <li>
                    KOBIS에서 해당 날짜의 박스오피스 데이터가
                    존재하는지 확인하세요.
                </li>

                <li>
                    KOBIS 인증키가 정상인지 확인하세요.
                </li>

                <li>
                    잠시 후 페이지를 새로고침해 보세요.
                </li>
            </ul>

        </div>
        """,
        unsafe_allow_html=True
    )

    st.stop()


# ============================================================
# 13. 숫자를 정수로 변환하는 함수
# ============================================================
# KOBIS API의 숫자 값은 문자열로 전달됩니다.
# 예: "12345"

def to_int(value):

    try:

        return int(
            str(value).replace(",", "")
        )

    except (ValueError, TypeError):

        return 0


# ============================================================
# 14. 영화 데이터 정리
# ============================================================

for movie in movies:

    movie["rank_num"] = to_int(
        movie.get("rank")
    )

    movie["audiCnt_num"] = to_int(
        movie.get("audiCnt")
    )

    movie["audiAcc_num"] = to_int(
        movie.get("audiAcc")
    )

    movie["scrnCnt_num"] = to_int(
        movie.get("scrnCnt")
    )


# 순위 순서대로 정렬
movies.sort(
    key=lambda x: x["rank_num"]
)


# ============================================================
# 15. 1위 영화 가져오기
# ============================================================

first_movie = movies[0]

first_name = first_movie.get(
    "movieNm",
    "영화명 없음"
)

first_audience = first_movie[
    "audiCnt_num"
]

first_acc = first_movie[
    "audiAcc_num"
]

first_screen = first_movie[
    "scrnCnt_num"
]


# ============================================================
# 16. 1위 영화 카드
# ============================================================

st.markdown(
    f"""
    <div class="movie-card">

        <div class="movie-number">
            🥒 어제의 박스오피스 1위
        </div>

        <div class="movie-name">
            🎬 {html.escape(first_name)}
        </div>

        <div>
            개봉일:
            {html.escape(
                first_movie.get("openDt", "-") or "-"
            )}
        </div>

    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# 17. 1위 영화 지표 카드 3개
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
# 18. 관객수 상위 5편
# ============================================================

top5 = sorted(
    movies,
    key=lambda x: x["audiCnt_num"],
    reverse=True
)[:5]


# 가장 관객수가 많은 영화
max_audience = max(
    movie["audiCnt_num"]
    for movie in top5
)


# 혹시 관객수가 모두 0일 경우 대비
if max_audience <= 0:

    max_audience = 1


# ============================================================
# 19. 오이 길이로 표현하는 막대그래프
# ============================================================

st.subheader("🥒 관객수 상위 5편")

st.caption(
    "관객수가 많을수록 오이가 길어집니다."
)


chart_html = """
<div class="cucumber-chart">
"""


for movie in top5:

    name = html.escape(
        movie.get(
            "movieNm",
            "영화명 없음"
        )
    )

    audience = movie[
        "audiCnt_num"
    ]

    rank = movie[
        "rank_num"
    ]


    # 가장 많은 관객수를 100%로 설정합니다.
    # 나머지 영화는 관객수 비율에 맞춰 오이 길이가 정해집니다.

    width_percent = (
        audience / max_audience
    ) * 100


    chart_html += f"""
    <div class="cucumber-row">

        <div class="cucumber-title">
            {rank}위 · {name}
        </div>

        <div class="cucumber-track">

            <div
                class="cucumber-fill"
                style="width: {width_percent:.1f}%;">
            </div>

        </div>

        <div class="cucumber-value">
            👥 {audience:,}명
        </div>

    </div>
    """


chart_html += """
</div>
"""


st.markdown(
    chart_html,
    unsafe_allow_html=True
)


# ============================================================
# 20. 전체 영화 표
# ============================================================

st.subheader("🎬 전체 박스오피스")


table_data = []


for movie in movies:

    table_data.append(
        {
            "순위": movie["rank_num"],

            "영화명": movie.get(
                "movieNm",
                "-"
            ),

            "개봉일": movie.get(
                "openDt",
                "-"
            ) or "-",

            "관객수": movie[
                "audiCnt_num"
            ],

            "누적관객": movie[
                "audiAcc_num"
            ],

            "스크린수": movie[
                "scrnCnt_num"
            ]
        }
    )


# Streamlit 표로 표시
st.dataframe(
    table_data,

    use_container_width=True,

    hide_index=True,

    column_config={

        "순위":
            st.column_config.NumberColumn(
                "순위",
                format="%d위"
            ),

        "영화명":
            st.column_config.TextColumn(
                "영화명"
            ),

        "개봉일":
            st.column_config.TextColumn(
                "개봉일"
            ),

        "관객수":
            st.column_config.NumberColumn(
                "관객수",
                format="%d명"
            ),

        "누적관객":
            st.column_config.NumberColumn(
                "누적관객",
                format="%d명"
            ),

        "스크린수":
            st.column_config.NumberColumn(
                "스크린수",
                format="%d개"
            )
    }
)


# ============================================================
# 21. 정상적으로 데이터를 불러왔다는 안내
# ============================================================

st.markdown(
    f"""
    <div class="success-box">

        ✅ <b>{display_date}</b>
        KOBIS 박스오피스 데이터를 정상적으로 불러왔습니다.

        <br>

        조회 날짜:
        <b>{target_date}</b>

    </div>
    """,
    unsafe_allow_html=True
)
