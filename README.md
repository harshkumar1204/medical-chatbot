# 🏥 Medical Assistant Chatbot

An AI-powered medical assistant chatbot built with Python and Streamlit that helps users
identify possible medical conditions, suggests over-the-counter medicines, provides dosage
guidance and recommends when to see a doctor — based on described symptoms.

## 🔗 Live Demo
👉 [https://medical-chatbot-afkybfaayykwtrqtpyuubd.streamlit.app](https://medical-chatbot-afkybfaayykwtrqtpyuubd.streamlit.app)

---

## ✨ Features

- 🩺 **Symptom Analysis** — Describe symptoms and get instant AI-powered medical guidance
- 💊 **Medicine Suggestions** — Recommends common over-the-counter medicines with dosage
- 🚨 **Emergency Detection** — Detects emergency keywords and shows emergency helpline numbers
- 👤 **Patient Profile** — Personalized responses based on age, gender and existing conditions
- 🌐 **Multi-Language Support** — Supports English, Hindi and Bengali
- 🏥 **Nearby Doctor Finder** — Find hospitals, clinics and pharmacies via Google Maps
- 👍 **Feedback System** — Rate each chatbot response with thumbs up/down
- 💾 **Download Chat History** — Save your conversation as a text file
- 🗑️ **Clear Chat** — Reset conversation anytime

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend UI | Streamlit |
| Backend | Python |
| AI Model | LLaMA 3.3 70B via Groq API |
| Deployment | Streamlit Cloud |

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10 or above
- Groq API Key (free at [console.groq.com](https://console.groq.com))

### Installation

1. **Clone the repository**
```bash
   git clone https://github.com/harshkumar1204/medical-chatbot.git
   cd medical-chatbot
```

2. **Install dependencies**
```bash
   pip install -r requirements.txt
```

3. **Set up your API key**

   Create a `.streamlit/secrets.toml` file:
```toml
   GROQ_API_KEY = "your-groq-api-key-here"
```

4. **Run the app**
```bash
   streamlit run app.py
```

5. Open your browser at `http://localhost:8501`

---

## 📁 Project Structure
