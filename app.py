import streamlit as st
from openai import OpenAI
from pypdf import PdfReader

# --- Read profile from PDF ---
def get_profile_text(pdf_path):
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text

PROFILE_TEXT = get_profile_text("Profile.pdf")

# --- Build agent system prompt ---
def build_system_prompt(profile_text):
    return (
        "You are acting as Alessandro Frullani's agent. You answer questions about Alessandro's career, background, skills, and experience. "
        "Be professional and engaging, as if talking to a potential client or recruiter who visited his profile. "
        "Use the information from the user's profile below to answer questions as accurately as possible. "
        "If you don't know the answer, say so politely, and encourage the user to provide their email if they wish to connect.\n\n"
        "### Profile Information ###\n"
        + profile_text
    )

st.set_page_config(page_title="Alessandro Frullani Agent", layout="centered")
st.title("Chat with Alessandro Frullani's Agent")
st.markdown("## Professional Profile (for agent context only)")

# You may choose to show just a teaser of your profile, or hide it
st.markdown(PROFILE_TEXT[:600])

API_KEY = st.secrets["OPENAI_API_KEY"]
openai = OpenAI(api_key=API_KEY)

if "history" not in st.session_state:
    st.session_state["history"] = []

user_input = st.text_input("Type your question for Alessandro's agent:")

if user_input:
    system_prompt = build_system_prompt(PROFILE_TEXT)
    messages = [{"role": "system", "content": system_prompt}]
    for turn in st.session_state["history"]:
        messages.append({"role": "user", "content": turn["user"]})
        messages.append({"role": "assistant", "content": turn["agent"]})
    messages.append({"role": "user", "content": user_input})

    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )
    agent_reply = response.choices[0].message.content
    st.write("Agent:", agent_reply)
    st.session_state["history"].append({"user": user_input, "agent": agent_reply})

if st.session_state["history"]:
    st.subheader("Conversation History")
    for h in st.session_state["history"]:
        st.write("You:", h["user"])
        st.write("Agent:", h["agent"])
