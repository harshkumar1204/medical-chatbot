from groq import Groq

API_KEY = "your-api-key-here"

SYSTEM_PROMPT = """
You are a helpful medical assistant chatbot. When the user describes their symptoms, you must respond in this exact format:

1. Possible Condition – Name the most likely condition based on the symptoms.
2. Suggested Medicine – Recommend common over-the-counter medicines for relief.
3. Dosage – Provide general dosage guidance.
4. When to See a Doctor – Clearly state warning signs that need immediate medical attention.

Always end with:
⚠️ This is not a substitute for professional medical advice. Please consult a doctor for proper diagnosis.
"""

def run_chatbot():
    client = Groq(api_key=API_KEY)
    conversation_history = []

    print("=" * 50)
    print("   🏥 Medical Assistant Chatbot")
    print("   Type your symptoms below.")
    print("   Type 'quit' to exit.")
    print("=" * 50)

    while True:
        user_input = input("\nYou: ").strip()

        if user_input.lower() in ["quit", "exit", "bye"]:
            print("Chatbot: Take care! Goodbye. 👋")
            break

        if not user_input:
            continue

        conversation_history.append({
            "role": "user",
            "content": user_input
        })

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": SYSTEM_PROMPT}] + conversation_history
        )

        bot_reply = response.choices[0].message.content

        conversation_history.append({
            "role": "assistant",
            "content": bot_reply
        })

        print(f"\nChatbot:\n{bot_reply}")

if __name__ == "__main__":
    run_chatbot()