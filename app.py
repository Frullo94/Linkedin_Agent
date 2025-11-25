import streamlit as st
from openai import OpenAI
from pypdf import PdfReader

def get_profile_text(pdf_path):
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text

PROFILE_TEXT = get_profile_text("Profile.pdf")

def build_system_prompt(profile_text):
    return (
        "You are acting as Alessandro Frullani's agent. Answer questions about his career, background, skills, and experience. "
        "Be professional and engaging; use the profile below for fact-based answers. "
        "If unsure, say so politely and invite the user to connect via email.\n\n"
        "### Profile Information ###\n"
        + profile_text
    )

st.set_page_config(page_title="Alessandro Frullani Agent", layout="centered")
st.title("Chat with Alessandro's Agent")

API_KEY = st.secrets["OPENAI_API_KEY"]
openai = OpenAI(api_key=API_KEY)

if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

# Display full flowing chat, oldest at top
for msg in st.session_state["chat_history"]:
    with st.chat_message(msg['role']):
        st.markdown(msg['content'])

user_input = st.chat_input("Type your message here...")

if user_input:
    # Add user input
    st.session_state["chat_history"].append({"role": "user", "content": user_input})

    # Compose chat with system prompt and history
    messages = [{"role": "system", "content": build_system_prompt(PROFILE_TEXT)}]
    for msg in st.session_state["chat_history"]:
        messages.append({"role": msg["role"], "content": msg["content"]})

    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )
    agent_reply = response.choices[0].message.content

    # Add agent response and instantly show it
    st.session_state["chat_history"].append({"role": "assistant", "content": agent_reply})
    with st.chat_message("assistant"):
        st.markdown(agent_reply)
