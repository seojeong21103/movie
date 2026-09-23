# pages/chat.py
# AI 채팅 페이지
# 초보자도 이해할 수 있도록 각 부분에 설명을 적었습니다.

import streamlit as st
from openai import OpenAI


# --------------------------------------------------
# 1. 페이지 기본 설정
# --------------------------------------------------

st.set_page_config(
    page_title="AI 채팅",
    page_icon="💬",
    layout="centered"
)


# --------------------------------------------------
# 2. 화면 꾸미기
# --------------------------------------------------

st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(135deg, #fff7fb 0%, #f4f0ff 100%);
    }

    .title {
        text-align: center;
        font-size: 42px;
        font-weight: 800;
        margin-bottom: 5px;
    }

    .subtitle {
        text-align: center;
        color: #777777;
        margin-bottom: 25px;
    }

    .stChatMessage {
        border-radius: 18px;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# --------------------------------------------------
# 3. 제목
# --------------------------------------------------

st.markdown(
    '<div class="title">💬 AI 채팅</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">AI와 자유롭게 대화해 보세요</div>',
    unsafe_allow_html=True
)


# --------------------------------------------------
# 4. Gemini API 연결
# --------------------------------------------------
# API 주소와 API 키는 코드에 직접 적지 않습니다.
# API 키는 Streamlit의 secrets에서 가져옵니다.

try:
    api_key = st.secrets["GEMINI_API_KEY"]

    client = OpenAI(
        api_key=api_key,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
    )

except Exception:
    st.info("AI 연결 정보를 확인할 수 없습니다. 관리자에게 설정을 확인해 달라고 해주세요.")
    st.stop()


# --------------------------------------------------
# 5. AI의 성격 설정
# --------------------------------------------------
# 화면에는 표시하지 않고 AI에게만 전달합니다.

SYSTEM_PROMPT = """
너는 중고등학생에게 설명하는 친절하지 않고 성가시고 무시를 잘하는 친구야.
쉬운 말은 어려운 말로 바꿔 줘.
반드시 순수 한국어로만 답해.
말 끝마다 우끼를 넣어.
"""


# --------------------------------------------------
# 6. 이전 대화 저장 공간 만들기
# --------------------------------------------------
# session_state를 사용하면 사용자가 채팅하는 동안
# 이전 대화 내용을 계속 기억할 수 있습니다.

if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []


# --------------------------------------------------
# 7. 이전에 나눈 대화 화면에 표시
# --------------------------------------------------

for message in st.session_state.chat_messages:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# --------------------------------------------------
# 8. 채팅 입력창
# --------------------------------------------------

user_input = st.chat_input("메시지를 입력하세요...")


# 사용자가 메시지를 입력했을 때 실행됩니다.
if user_input:

    # 사용자의 메시지를 대화 기록에 저장합니다.
    st.session_state.chat_messages.append(
        {
            "role": "user",
            "content": user_input
        }
    )

    # 사용자의 말풍선을 바로 보여줍니다.
    with st.chat_message("user"):
        st.markdown(user_input)

    # AI의 답변을 표시할 말풍선을 만듭니다.
    with st.chat_message("assistant"):

        answer_box = st.empty()

        try:
            # API에 보낼 전체 대화 내용을 만듭니다.
            messages = [
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                }
            ]

            # 지금까지의 이전 대화를 모두 추가합니다.
            messages.extend(st.session_state.chat_messages)

            # Gemini API에 요청합니다.
            # stream=True를 사용해서 답변이 조금씩 나오도록 합니다.
            response = client.chat.completions.create(
                model="gemini-3.5-flash-lite",
                messages=messages,
                stream=True
            )

            # 실시간으로 들어오는 글자를 저장할 변수입니다.
            full_answer = ""

            # 답변 조각을 하나씩 받아 화면에 표시합니다.
            for chunk in response:

                # 답변 내용이 있는지 확인합니다.
                if chunk.choices and chunk.choices[0].delta.content:

                    piece = chunk.choices[0].delta.content

                    # 받은 글자를 계속 이어 붙입니다.
                    full_answer += piece

                    # 지금까지 받은 답변을 화면에 표시합니다.
                    answer_box.markdown(full_answer)

            # 완성된 AI 답변을 대화 기록에 저장합니다.
            st.session_state.chat_messages.append(
                {
                    "role": "assistant",
                    "content": full_answer
                }
            )

        except Exception:
            # API 요청이 실패해도 빨간색 오류 화면 대신
            # 사용자가 이해하기 쉬운 안내 문구만 보여줍니다.
            answer_box.info(
                "AI와 연결하는 중 문제가 발생했어요. 잠시 후 다시 시도해 주세요."
            )
