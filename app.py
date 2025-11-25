import streamlit as st
from openai import OpenAI
from pypdf import PdfReader
import requests

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
        "You are acting as Alessandro Frullani's agent. Answer questions about Alessandro's career, background, skills, and experience. "
        "Be professional and engaging; use the profile below for fact-based answers. "
        "Be polite and ask 
        "If the user asks how to contact Alessandro, provide the professional email: alessandro.frullani@email.com. "
        "If unsure, say so politely and invite the user to connect via email.\n\n"
        "### Profile Information ###\n"
        + profile_text
    )

def notify_pushover(message):
    requests.post(
        "https://api.pushover.net/1/messages.json",
        data={
            "token": st.secrets["PUSHOVER_TOKEN"],
            "user": st.secrets["PUSHOVER_USER"],
            "message": message,
        }
    )
    
if "started" not in st.session_state:
    st.session_state["started"] = False

user_input = st.chat_input("Type your message here...")

if user_input and not st.session_state["started"]:
    notify_pushover("A new recruiter has started a chat session with Alessandro's Agent!")
    st.session_state["started"] = True
st.set_page_config(page_title="Alessandro Frullani Agent", layout="centered")
st.title("Chat with Alessandro Frullani's Agent")

API_KEY = st.secrets["OPENAI_API_KEY"]
openai = OpenAI(api_key=API_KEY)

if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

# Display all messages (user and agent)
for msg in st.session_state["chat_history"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("Type your message here...")

if user_input:
    st.session_state["chat_history"].append({"role": "user", "content": user_input})
    # Compose messages for OpenAI, including all context
    messages = [{"role": "system", "content": build_system_prompt(PROFILE_TEXT)}]
    for msg in st.session_state["chat_history"]:
        messages.append({"role": msg["role"], "content": msg["content"]})

    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )
    agent_reply = response.choices[0].message.content

    st.session_state["chat_history"].append({"role": "assistant", "content": agent_reply})
    with st.chat_message("assistant"):
        st.markdown(agent_reply)

    # Notify for recruiter intent (email
# Detect if recruiter provides an email/contact detail
    if ("contact" in agent_reply.lower() or "email" in agent_reply.lower()) and "@" in user_input:
        notify_pushover(f"Recruiter wants to reach out: {user_input}")
    # Notify if recruiter asks odd/personal questions (add more as needed)
    if any(keyword in user_input.lower() for keyword in ["height", "weight", "age"]):
        notify_pushover(f"Recruiter asked odd question: {user_input}")

