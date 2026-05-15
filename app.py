from groq import Groq
import streamlit as st

API_KEY = st.secrets["GROQ_API_KEY"]

SYSTEM_PROMPT = """
You are a helpful medical assistant chatbot. When the user describes their symptoms, you must respond in this exact format:

1. Possible Condition – Name the most likely condition based on the symptoms.
2. Suggested Medicine – Recommend common over-the-counter medicines for relief.
3. Dosage – Provide general dosage guidance.
4. When to See a Doctor – Clearly state warning signs that need immediate medical attention.

Always end with:
⚠️ This is not a substitute for professional medical advice. Please consult a doctor for proper diagnosis.
"""

st.set_page_config(page_title="Medical Assistant", page_icon="🏥", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    html, body, [class*="css"], .stApp {
        background-color: #f0f7f4 !important;
        color: #111111 !important;
    }
    [data-testid="stChatMessage"] {
        background-color: #ffffff !important;
        border-radius: 10px !important;
        padding: 12px !important;
        margin: 6px 0 !important;
        color: #111111 !important;
    }
    [data-testid="stChatMessage"] p,
    [data-testid="stChatMessage"] li,
    [data-testid="stChatMessage"] span {
        color: #111111 !important;
    }
    [data-testid="stSidebar"] {
        background-color: #1a5c3a !important;
    }
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] li,
    [data-testid="stSidebar"] span {
        color: #ffffff !important;
    }
    .main-header {
        background-color: #1a5c3a;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 20px;
    }
    .main-header h1 { color: #ffffff !important; font-size: 28px; margin: 0; }
    .main-header p { color: rgba(255,255,255,0.85) !important; margin: 5px 0 0 0; font-size: 14px; }
    </style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## 🏥 Medical Assistant")
    st.markdown("---")
    st.markdown("### ℹ️ About")
    st.markdown("This AI chatbot helps you understand your symptoms and suggests over-the-counter medicines.")
    st.markdown("---")
    st.markdown("### 📋 How to use")
    st.markdown("""
    - Type your symptoms in the chat box
    - Get instant medical guidance
    - Follow dosage instructions carefully
    - See a doctor if symptoms are severe
    """)
    st.markdown("---")
    st.markdown("### ⚠️ Disclaimer")
    st.markdown("This app is not a substitute for professional medical advice.")
    st.markdown("---")
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.messages.append({
            "role": "assistant",
            "content": "Hello! I'm your medical assistant. Please describe your symptoms and I'll help you understand what might be going on. 😊"
        })
        st.rerun()

st.markdown("""
    <div class="main-header">
        <h1>🏥 Medical Assistant Chatbot</h1>
        <p>Describe your symptoms and get instant guidance</p>
    </div>
""", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({
        "role": "assistant",
        "content": "Hello! I'm your medical assistant. Please describe your symptoms and I'll help you understand what might be going on. 😊"
    })

for message in st.session_state.messages:
    avatar = "🏥" if message["role"] == "assistant" else "🧑"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

if user_input := st.chat_input("Describe your symptoms here..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user", avatar="🧑"):
        st.markdown(user_input)

    client = Groq(api_key=API_KEY)

    with st.chat_message("assistant", avatar="🏥"):
        with st.spinner("Analyzing your symptoms..."):
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": SYSTEM_PROMPT}] + [
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ]
            )
            bot_reply = response.choices[0].message.content
            st.markdown(bot_reply)

    st.session_state.messages.append({"role": "assistant", "content": bot_reply})