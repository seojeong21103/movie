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
# 화면 제목
# --------------------------------------------------
st.title("💬 AI 채팅")
st.caption("AI와 편하게 대화를 이어가 보세요.")


# --------------------------------------------------
# Gemini API 연결
# API 키는 Streamlit Secrets에서 가져옵니다.
# 코드에 API 키를 직접 적지 않습니다.
# --------------------------------------------------
try:
    api_key = st.secrets["GEMINI_API_KEY"]

    client = OpenAI(
        api_key=api_key,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
    )

except Exception:
    st.info("AI 연결 정보를 확인할 수 없습니다. 잠시 후 다시 시도해 주세요.")
    st.stop()


# --------------------------------------------------
# AI의 성격을 정합니다.
# 화면에는 이 문장이 표시되지 않습니다.
# --------------------------------------------------
SYSTEM_PROMPT = """
너는 중고등학생에게 설명하는 친절하지 않고 성가시고 무시를 잘하는 나쁜 친구야.
쉬운 말은 어려운 말로 바꿔 주고, 반드시 순수 한국어로만 답해.
"""


# --------------------------------------------------
# 대화 기록을 처음 한 번만 만듭니다.
# 이 기록이 있기 때문에 AI가 이전 대화를 기억할 수 있습니다.
# --------------------------------------------------
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        }
    ]


# --------------------------------------------------
# 지금까지의 대화를 화면에 표시합니다.
# system 메시지는 화면에 표시하지 않습니다.
# --------------------------------------------------
for message in st.session_state.chat_messages:
    if message["role"] == "system":
        continue

    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# --------------------------------------------------
# 채팅 입력창
# --------------------------------------------------
user_message = st.chat_input("메시지를 입력하세요...")


# --------------------------------------------------
# 사용자가 메시지를 보냈을 때 실행됩니다.
# --------------------------------------------------
if user_message:

    # 사용자의 메시지를 대화 기록에 저장합니다.
    st.session_state.chat_messages.append(
        {
            "role": "user",
            "content": user_message
        }
    )

    # 사용자의 말풍선을 바로 보여줍니다.
    with st.chat_message("user"):
        st.markdown(user_message)

    # AI 답변을 받을 공간을 만듭니다.
    with st.chat_message("assistant"):
        answer_box = st.empty()

        try:
            # Gemini API에 이전 대화 전체를 함께 보냅니다.
            response = client.chat.completions.create(
                model="gemini-3.5-flash-lite",
                messages=st.session_state.chat_messages,
                stream=True
            )

            # AI가 보내는 글을 조금씩 받아 화면에 표시합니다.
            full_answer = ""

            for chunk in response:
                # 이번에 새로 들어온 글자를 가져옵니다.
                if chunk.choices and chunk.choices[0].delta.content:
                    full_answer += chunk.choices[0].delta.content

                    # 지금까지 받은 내용을 화면에 표시합니다.
                    answer_box.markdown(full_answer + "▌")

            # 마지막 커서를 제거합니다.
            answer_box.markdown(full_answer)

            # AI의 답변도 대화 기록에 저장합니다.
            st.session_state.chat_messages.append(
                {
                    "role": "assistant",
                    "content": full_answer
                }
            )

        except Exception:
            # API 요청에 문제가 생겨도 빨간 오류 화면 대신
            # 간단한 한국어 안내 문구만 보여줍니다.
            answer_box.info(
                "AI가 답변을 가져오지 못했어요. 잠시 후 다시 시도해 주세요."
            )
