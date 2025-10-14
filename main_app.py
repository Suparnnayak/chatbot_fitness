import streamlit as st
from groq import Groq
import os
from dotenv import load_dotenv

# ==============================
# 🌟 INITIAL SETUP
# ==============================
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    st.error("❌ Missing GROQ_API_KEY in .env or environment variables.")
    st.stop()

client = Groq(api_key=api_key)

st.set_page_config(
    page_title="💪 Fitness Chatbot (Groq LLaMA)",
    page_icon="💪",
    layout="wide"
)

# ==============================
# 💬 SESSION STATE
# ==============================
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ==============================
# 🧍 SIDEBAR (USER PROFILE)
# ==============================
st.sidebar.title("🏋️‍♂️ Fitness Profile")

gender = st.sidebar.radio("Gender:", ["Male", "Female"])
user_height = st.sidebar.slider("Height (cm):", 100, 250, 170)
user_weight = st.sidebar.slider("Weight (kg):", 30, 200, 70)

st.sidebar.markdown("---")
if st.sidebar.button("🧹 Clear Chat History"):
    st.session_state.chat_history = []
    st.experimental_rerun()

# ==============================
# 💬 MAIN CHAT UI
# ==============================
st.title("💬 Carefolio Chatbot ")
st.caption("Ask me about workouts, nutrition, fat loss, muscle gain, or general health advice!")

# Display past conversation
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input
user_query = st.chat_input("Type your fitness question...")

# ==============================
# ⚙️ CHAT LOGIC WITH CONTEXT MEMORY
# ==============================
if user_query:
    # Add user's message to history
    st.session_state.chat_history.append({"role": "user", "content": user_query})

    # Construct full conversation context
    messages = [
        {"role": "system", "content": f"""
        You are a professional fitness and nutrition expert.
        Stay in character and only answer questions related to:
        workouts, exercise routines, weight management, nutrition, diet, health, or body composition.

        - Always be encouraging, clear, and easy to understand.
        - Use user data (gender: {gender}, height: {user_height} cm, weight: {user_weight} kg) to personalize advice.
        - If the user says 'yes', 'continue', or 'tell me more', continue naturally from your last answer.
        - If the question is NOT fitness-related, reply with:
          "🚫 I can only answer fitness-related questions. Please ask about exercise, health, or nutrition."
        """}
    ]

    # Add previous messages for context
    for msg in st.session_state.chat_history[:-1]:  # everything before the latest user input
        messages.append({"role": msg["role"], "content": msg["content"]})

    # Add latest user message
    messages.append({"role": "user", "content": user_query})

    # Generate the response
    try:
        with st.chat_message("assistant"):
            with st.spinner("Thinking... 💭"):
                response = client.chat.completions.create(
                    messages=messages,
                    model="llama-3.1-8b-instant",  # ✅ Updated working model
                    max_tokens=1024,
                )
                answer = response.choices[0].message.content
                st.markdown(answer)

        # Save assistant response
        st.session_state.chat_history.append({"role": "assistant", "content": answer})

    except Exception as e:
        error_msg = f"⚠️ API Error: {str(e)}"
        st.error(error_msg)
        st.session_state.chat_history.append({"role": "assistant", "content": error_msg})
