import os
import streamlit as st
from dotenv import load_dotenv
from google import genai

# Load API key
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("Gemini API key not found.")
    st.stop()

client = genai.Client(api_key=api_key)

# Privacy instructions
SYSTEM_INSTRUCTION = """
You are an AI Privacy Risk and Blind-Spot Detection Assistant.

Analyze applications and digital systems for:
- Personal data
- Sensitive or potentially sensitive data
- Privacy risks
- Missing information
- Privacy blind spots
- Follow-up questions

Rules:
- Never assume information not provided by the user.
- Mark missing information as Unknown.
- Separate confirmed facts, unknown information, and potential risks.
- Use conditional language for possible risks.
- Do not give legal advice.
- Answer follow-up questions using the conversation context.
- Keep responses clear and concise.
"""

# Page
st.set_page_config(
    page_title="AI Privacy Risk Chatbot",
    page_icon="🔐"
)

st.title("🔐 AI Privacy Risk & Blind-Spot Detection Chatbot")

st.write(
    "Describe an application or digital system to identify "
    "privacy risks and blind spots."
)

# Store conversation
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display conversation
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Describe an application..."):

    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    with st.chat_message("user"):
        st.markdown(prompt)

    # Build conversation in one request
    conversation = ""

    for message in st.session_state.messages[-8:]:
        conversation += (
            message["role"].upper()
            + ": "
            + message["content"]
            + "\n\n"
        )

    with st.chat_message("assistant"):

        with st.spinner("Analyzing..."):

            try:
                response = client.models.generate_content(
                    model="gemini-3.5-flash",
                    contents=SYSTEM_INSTRUCTION
                    + "\n\nConversation:\n"
                    + conversation
                    + "\n\nAnswer the latest user message directly."
                )

                answer = response.text

                st.markdown(answer)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer
                })

            except Exception as e:

                if "503" in str(e) or "UNAVAILABLE" in str(e):

                    st.warning(
                        "⚠️ Gemini is temporarily busy. "
                        "Please try again in a few seconds."
                    )

                else:

                    st.error(
                        "Unable to get a response from Gemini."
                    )

                st.caption(str(e))

# Clear chat
if st.button("🗑️ Clear Chat"):
    st.session_state.messages = []
    st.rerun()