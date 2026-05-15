from groq import Groq
import streamlit as st

API_KEY = st.secrets["GROQ_API_KEY"]

# ─────────────────────────────────────────────
# EMERGENCY KEYWORDS
# ─────────────────────────────────────────────
EMERGENCY_KEYWORDS = [
    "chest pain", "can't breathe", "cannot breathe", "not breathing",
    "heart attack", "stroke", "unconscious", "fainted", "seizure",
    "bleeding heavily", "overdose", "suicide", "poisoning",
    "severe allergic", "anaphylaxis", "choking", "no pulse",
    "stopped breathing", "severe burn", "drowning", "electrocution",
    "head injury", "spinal injury", "severe bleeding", "coughing blood",
    "vomiting blood", "loss of vision", "sudden blindness", "paralysis",
    "can't move", "face drooping", "arm weakness", "speech difficulty",
    "high fever convulsion", "infant not breathing", "baby not moving"
]

def is_emergency(text):
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in EMERGENCY_KEYWORDS)

# ─────────────────────────────────────────────
# SYSTEM PROMPT (dynamic based on profile)
# ─────────────────────────────────────────────
def get_system_prompt(profile=None, language="English"):
    lang_instruction = {
        "English": "Always respond in English.",
        "Hindi": "Always respond in Hindi (हिंदी में जवाब दें).",
        "Bengali": "Always respond in Bengali (বাংলায় উত্তর দিন).",
    }.get(language, "Always respond in English.")

    profile_context = ""
    if profile:
        profile_context = f"""
The patient has the following profile:
- Name: {profile.get('name', 'Unknown')}
- Age: {profile.get('age', 'Unknown')}
- Gender: {profile.get('gender', 'Unknown')}
- Existing Conditions: {profile.get('conditions', 'None')}
- Allergies: {profile.get('allergies', 'None')}

Use this profile to personalize your response. Adjust dosage based on age (child < 12, adult 12-60, senior > 60).
For children and seniors, be extra cautious with medicine suggestions.
"""

    return f"""
You are a helpful medical assistant chatbot. {lang_instruction}

{profile_context}

When the user describes their symptoms, first ask 2-3 short follow-up questions to better understand the situation, such as:
- How long have you had this symptom?
- Is it getting worse or staying the same?
- Do you have any fever, nausea, or other symptoms along with it?

After the user answers the follow-up questions, respond in this exact format:

1. Possible Condition – Name the most likely condition based on the symptoms.
2. Suggested Medicine – Recommend common over-the-counter medicines for relief.
3. Dosage – Provide age-appropriate dosage guidance with timing (e.g., "Take at 8am, 2pm, 8pm").
4. When to See a Doctor – Clearly state warning signs that need immediate medical attention.

Always end with:
⚠️ This is not a substitute for professional medical advice. Please consult a doctor for proper diagnosis.
"""

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(page_title="Medical Assistant", page_icon="🏥", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    html, body, [class*="css"], .stApp {
        background-color: #f0f7f4 !important;
        color: #111111 !important;
    }
    .main-bg {
        background-image: url("https://img.freepik.com/free-photo/stethoscope-medical-equipment_23-2147965781.jpg");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
        position: fixed;
        top: 0; left: 0;
        width: 100%; height: 100%;
        opacity: 0.08;
        z-index: 0;
        pointer-events: none;
    }
    .block-container { position: relative; z-index: 1; }
    [data-testid="stChatMessage"] {
        background-color: rgba(255,255,255,0.92) !important;
        border-radius: 10px !important;
        padding: 12px !important;
        margin: 6px 0 !important;
        color: #111111 !important;
        backdrop-filter: blur(5px);
        border: 1px solid rgba(26,92,58,0.15) !important;
    }
    [data-testid="stChatMessage"] p,
    [data-testid="stChatMessage"] li,
    [data-testid="stChatMessage"] span { color: #111111 !important; }
    [data-testid="stSidebar"] { background-color: #1a5c3a !important; }
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] li,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] label { color: #ffffff !important; }
    .main-header {
        background: linear-gradient(135deg, #1a5c3a 0%, #2d8a5e 100%);
        padding: 25px;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 20px;
        border: 1px solid rgba(255,255,255,0.2);
        box-shadow: 0 4px 15px rgba(26,92,58,0.3);
    }
    .main-header h1 { color: #ffffff !important; font-size: 28px; margin: 0; }
    .main-header p { color: rgba(255,255,255,0.85) !important; margin: 5px 0 0 0; font-size: 14px; }
    .heartbeat { display: flex; align-items: center; justify-content: center; margin-top: 10px; }
    .heartbeat-line {
        color: #90EE90; font-size: 24px; letter-spacing: 2px;
        animation: pulse 1.5s infinite;
    }
    @keyframes pulse {
        0% { opacity: 1; } 50% { opacity: 0.3; } 100% { opacity: 1; }
    }
    .stats-bar { display: flex; justify-content: center; gap: 20px; margin: 10px 0; }
    .stat-item {
        background: rgba(255,255,255,0.15);
        padding: 5px 15px; border-radius: 20px;
        color: white !important; font-size: 12px;
    }
    .profile-box {
        background: rgba(255,255,255,0.08);
        border-radius: 10px;
        padding: 10px;
        margin-top: 5px;
        border: 1px solid rgba(255,255,255,0.2);
    }
    </style>
    <div class="main-bg"></div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SESSION STATE INIT
# ─────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "profile" not in st.session_state:
    st.session_state.profile = None
if "profile_saved" not in st.session_state:
    st.session_state.profile_saved = False
if "language" not in st.session_state:
    st.session_state.language = "English"

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🏥 Medical Assistant")
    st.markdown("---")

    # Language selector
    st.markdown("### 🌐 Language")
    language = st.selectbox(
        "Choose your language",
        ["English", "Hindi", "Bengali"],
        index=["English", "Hindi", "Bengali"].index(st.session_state.language),
        label_visibility="collapsed"
    )
    if language != st.session_state.language:
        st.session_state.language = language
        st.rerun()

    st.markdown("---")

    # Patient profile
    st.markdown("### 👤 Patient Profile")
    with st.form("profile_form"):
        name = st.text_input("Name", value=st.session_state.profile.get("name", "") if st.session_state.profile else "")
        age = st.number_input("Age", min_value=0, max_value=120, value=int(st.session_state.profile.get("age", 25)) if st.session_state.profile else 25)
        gender = st.selectbox("Gender", ["Male", "Female", "Other"],
                              index=["Male", "Female", "Other"].index(st.session_state.profile.get("gender", "Male")) if st.session_state.profile else 0)
        conditions = st.text_input("Existing Conditions (e.g. diabetes)", value=st.session_state.profile.get("conditions", "") if st.session_state.profile else "")
        allergies = st.text_input("Allergies (e.g. penicillin)", value=st.session_state.profile.get("allergies", "") if st.session_state.profile else "")
        save_profile = st.form_submit_button("💾 Save Profile", use_container_width=True)

    if save_profile:
        st.session_state.profile = {
            "name": name,
            "age": age,
            "gender": gender,
            "conditions": conditions if conditions else "None",
            "allergies": allergies if allergies else "None"
        }
        st.session_state.profile_saved = True
        # Reset chat with personalized greeting
        st.session_state.messages = [{
            "role": "assistant",
            "content": f"Hello {name}! 👋 I'm your personal medical assistant. I've saved your profile. Please describe your symptoms and I'll give you personalized guidance. 😊"
        }]
        st.rerun()

    if st.session_state.profile_saved and st.session_state.profile:
        p = st.session_state.profile
        st.markdown(f"""
        <div class="profile-box">
        ✅ <b>{p['name']}</b> | {p['age']} yrs | {p['gender']}<br>
        🩺 {p['conditions']}<br>
        ⚠️ Allergies: {p['allergies']}
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 🚨 Emergency Numbers")
    st.markdown("""
    - 🚑 Ambulance: **102**
    - 🆘 Emergency: **112**
    - 🧠 Mental Health: **iCall 9152987821**
    - 🔥 Fire: **101**
    - 👮 Police: **100**
    """)
    st.markdown("---")
    st.markdown("### 📋 How to use")
    st.markdown("""
    - Fill your profile above
    - Type your symptoms
    - Answer follow-up questions
    - Get personalized guidance
    """)
    st.markdown("---")
    st.markdown("### ⚠️ Disclaimer")
    st.markdown("This app is not a substitute for professional medical advice.")
    st.markdown("---")
    if st.button("🗑️ Clear Chat", use_container_width=True):
        name = st.session_state.profile.get("name", "") if st.session_state.profile else ""
        greeting = f"Hello {name}! 👋 Chat cleared. Please describe your symptoms. 😊" if name else "Hello! I'm your medical assistant. Please describe your symptoms. 😊"
        st.session_state.messages = [{"role": "assistant", "content": greeting}]
        st.rerun()

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.markdown("""
    <div class="main-header">
        <h1>🏥 Medical Assistant Chatbot</h1>
        <p>Describe your symptoms and get instant personalized guidance</p>
        <div class="heartbeat">
            <span class="heartbeat-line">♥ ─ ─ /\\ ─ /\\\\─ ─ ♥</span>
        </div>
        <div class="stats-bar">
            <span class="stat-item">❤️ AI Powered</span>
            <span class="stat-item">💊 Medicine Guide</span>
            <span class="stat-item">🩺 24/7 Available</span>
            <span class="stat-item">🌐 3 Languages</span>
        </div>
    </div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# INITIAL GREETING
# ─────────────────────────────────────────────
if not st.session_state.messages:
    if st.session_state.profile:
        greeting = f"Hello {st.session_state.profile['name']}! 👋 Please describe your symptoms and I'll give you personalized guidance. 😊"
    else:
        greeting = "Hello! 👋 I'm your medical assistant. Please fill in your profile in the sidebar for personalized advice, or just describe your symptoms to get started. 😊"
    st.session_state.messages.append({"role": "assistant", "content": greeting})

# ─────────────────────────────────────────────
# CHAT HISTORY
# ─────────────────────────────────────────────
for message in st.session_state.messages:
    avatar = "🏥" if message["role"] == "assistant" else "🧑"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# ─────────────────────────────────────────────
# CHAT INPUT
# ─────────────────────────────────────────────
placeholder_text = {
    "English": "Describe your symptoms here...",
    "Hindi": "अपने लक्षण यहाँ लिखें...",
    "Bengali": "আপনার লক্ষণ এখানে লিখুন..."
}.get(st.session_state.language, "Describe your symptoms here...")

if user_input := st.chat_input(placeholder_text):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user", avatar="🧑"):
        st.markdown(user_input)

    # 🚨 Emergency check FIRST
    if is_emergency(user_input):
        emergency_msg = {
            "English": """🚨 **EMERGENCY DETECTED — Please call for help immediately!**

| Service | Number |
|--------|--------|
| 🚑 Ambulance | **102** |
| 🆘 National Emergency | **112** |
| 👮 Police | **100** |
| 🔥 Fire | **101** |
| 🧠 Mental Health (iCall) | **9152987821** |

**Do NOT wait — call now or ask someone nearby to help you.**

---
I'll still try to assist you below, but please prioritize emergency services first.""",

            "Hindi": """🚨 **आपातकालीन स्थिति पहचानी गई — कृपया तुरंत मदद के लिए कॉल करें!**

| सेवा | नंबर |
|------|------|
| 🚑 एम्बुलेंस | **102** |
| 🆘 राष्ट्रीय आपातकाल | **112** |
| 👮 पुलिस | **100** |
| 🧠 मानसिक स्वास्थ्य | **9152987821** |

**देरी न करें — अभी कॉल करें।**""",

            "Bengali": """🚨 **জরুরি অবস্থা শনাক্ত হয়েছে — অবিলম্বে সাহায্যের জন্য কল করুন!**

| সেবা | নম্বর |
|------|-------|
| 🚑 অ্যাম্বুলেন্স | **102** |
| 🆘 জাতীয় জরুরি | **112** |
| 👮 পুলিশ | **100** |
| 🧠 মানসিক স্বাস্থ্য | **9152987821** |

**দেরি করবেন না — এখনই কল করুন।**"""
        }.get(st.session_state.language, "")

        with st.chat_message("assistant", avatar="🏥"):
            st.error(emergency_msg)
        st.session_state.messages.append({"role": "assistant", "content": emergency_msg})

    # Normal AI response (always runs)
    client = Groq(api_key=API_KEY)
    with st.chat_message("assistant", avatar="🏥"):
        with st.spinner("🩺 Analyzing your symptoms..."):
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": get_system_prompt(st.session_state.profile, st.session_state.language)}] + [
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ]
            )
            bot_reply = response.choices[0].message.content
            st.markdown(bot_reply)

    st.session_state.messages.append({"role": "assistant", "content": bot_reply})