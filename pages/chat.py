import streamlit as st
from openai import OpenAI


# --------------------------------------------------
# 페이지 기본 설정
# --------------------------------------------------
st.set_page_config(
    page_title="AI 채팅",
    page_icon="💬",
    layout="centered"
)


# --------------------------------------------------
# 화면 꾸미기
# --------------------------------------------------
st.markdown(
    """
    <style>
    .main {
        background: linear-gradient(180deg, #fff8fc 0%, #f8f5ff 100%);
    }

    .chat-title {
        text-align: center;
        font-size: 2.2rem;
        font-weight: 800;
        margin-top: 10px;
        margin-bottom: 5px;
    }

    .chat-subtitle {
        text-align: center;
        color: #777777;
        margin-bottom: 25px;
    }

    /* 채팅 말풍선 */
    [data-testid="stChatMessage"] {
        border-radius: 18px;
        margin-bottom: 10px;
    }

    /* 입력창 */
    [data-testid="stChatInput"] {
        border-radius: 18px;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# --------------------------------------------------
# 제목
# --------------------------------------------------
st.markdown(
    '<div class="chat-title">💬 AI 친구와 채팅</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="chat-subtitle">궁금한 것을 편하게 물어보세요 ✨</div>',
    unsafe_allow_html=True
)


# --------------------------------------------------
# Gemini API 키 확인
# 비밀 금고의 GEMINI_API_KEY를 사용합니다.
# --------------------------------------------------
if "GEMINI_API_KEY" not in st.secrets:
    st.warning("Gemini API 키가 설정되지 않았어요. 비밀 금고의 GEMINI_API_KEY를 확인해 주세요.")
    st.stop()

api_key = st.secrets["GEMINI_API_KEY"]


# --------------------------------------------------
# OpenAI 라이브러리를 이용해 Gemini에 연결
# --------------------------------------------------
client = OpenAI(
    api_key=api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)


# --------------------------------------------------
# AI의 성격 설정
# 화면에는 표시하지 않고 API 요청에만 사용합니다.
# --------------------------------------------------
SYSTEM_PROMPT = """
너는 중고등학생에게 설명하는 성격은 평범하고 말 끝마다 우끼를 넣는 친구야.
쉬운 말은 어려운 말로 바꿔 주고, 반드시 순수 한국어로만 답해.
"""


# --------------------------------------------------
# 채팅 기록 저장
# 사용자가 페이지를 새로고침하기 전까지 이전 대화를 기억합니다.
# --------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []


# --------------------------------------------------
# 지금까지의 채팅 내용을 화면에 표시
# --------------------------------------------------
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# --------------------------------------------------
# 사용자가 메시지를 입력하는 곳
# --------------------------------------------------
user_message = st.chat_input("메시지를 입력하세요...")


if user_message:

    # 사용자의 메시지를 기록합니다.
    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_message
        }
    )

    # 사용자 말풍선을 바로 보여줍니다.
    with st.chat_message("user"):
        st.markdown(user_message)

    # AI 말풍선을 만듭니다.
    with st.chat_message("assistant"):
        answer_box = st.empty()

        # 시스템 지침 + 지금까지의 대화를 함께 보냅니다.
        api_messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            }
        ]

        api_messages.extend(st.session_state.messages)

        try:
            # stream=True로 AI 답변을 실시간으로 받습니다.
            response = client.chat.completions.create(
                model="gemini-3.5-flash-lite",
                messages=api_messages,
                stream=True
            )

            full_answer = ""

            # 답변이 도착하는 대로 한 글자씩 이어서 보여줍니다.
            for chunk in response:
                if not chunk.choices:
                    continue

                content = chunk.choices[0].delta.content

                if content:
                    full_answer += content
                    answer_box.markdown(full_answer + "▌")

            # 마지막에는 커서 표시를 제거합니다.
            answer_box.markdown(full_answer)

            # AI 답변도 채팅 기록에 저장합니다.
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": full_answer
                }
            )

        except Exception:
            # API 오류가 발생해도 빨간 오류 화면 대신
            # 사용자에게 간단한 한국어 안내만 보여줍니다.
            answer_box.info(
                "잠시 문제가 생겼어요. 잠시 후 다시 메시지를 보내 주세요."
            )
