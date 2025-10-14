import streamlit as st
from groq import Groq
import os
from dotenv import load_dotenv

# Constants
U_NAME = "User"
A_NAME = "Assistant"

# Initialize Groq API client
load_dotenv()
api_key = os.environ.get("GROQ_API_KEY")
if not api_key:
    st.error("API Key for Groq is missing.")
    st.stop()

client = Groq(api_key=api_key)

# Streamlit page configurationo
st.set_page_config(
    page_title="Fitness Chatbot with Groq LLaMA",
    page_icon=":muscle:",
    layout="wide"
)

# Initialize session state for chat history and user data
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'user_height' not in st.session_state:
    st.session_state.user_height = None
if 'user_weight' not in st.session_state:
    st.session_state.user_weight = None

# Sidebar inputs
st.sidebar.title("Fitness Chatbot")

# Gender
gender = st.sidebar.radio("Choose your gender:", ["Male", "Female"])
st.session_state.gender = gender

# Height slider
user_height = st.sidebar.slider("Height (cm)", min_value=100, max_value=250, value=170)
st.session_state.user_height = user_height

# Weight slider
user_weight = st.sidebar.slider("Weight (kg)", min_value=30, max_value=200, value=70)
st.session_state.user_weight = user_weight

if st.sidebar.button("Clear Chat History"):
    st.session_state.chat_history = []
    st.experimental_rerun()

# List of fitness-related keywords
FITNESS_KEYWORDS = [
    "exercise", "workout", "gym", "calories", "weight loss", "muscle",
    "strength", "fitness", "nutrition", "diet", "cardio", "training",
    "protein", "healthy", "fat loss", "BMI", "running", "yoga",
    "hydration", "stretching", "flexibility", "body fat", "recovery", "HIIT",
    "lifting", "crossfit", "wellness", "resistance training", "metabolism",
    "pushups", "pullups", "squats", "deadlifts", "bench press", "cycling",
    "marathon", "heart rate", "strength training", "warm-up", "cool-down",
    "sports", "weightlifting", "bodybuilding", "caloric intake", "macro tracking"
]

def is_fitness_related(query):
    """Checks if the user query is related to fitness."""
    return any(keyword in query.lower() for keyword in FITNESS_KEYWORDS)

# Show chat interface after height and weight are entered
if st.session_state.user_height is not None and st.session_state.user_weight is not None:
    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message(name=message["role"], avatar="user" if message["role"] == "user" else "assistant"):
            st.markdown(message["content"])

    # Chat input
    user_text = st.chat_input("Ask a fitness question...")

    if user_text:
        if not is_fitness_related(user_text):
            st.warning("🚨 **Only fitness-related questions are allowed!** Please ask about health or exercise.")
            st.stop()  # 🚨 STOP EXECUTION IMMEDIATELY

        # Proceed with chatbot response generation
        st.session_state.chat_history.append({"role": "user", "content": user_text})
        with st.chat_message(U_NAME, avatar="user"):
            st.markdown(user_text)

        # Add user data for context
        user_data_message = f"User Data: Gender: {gender}, Height: {user_height} cm, Weight: {user_weight} kg."
        st.session_state.chat_history.append({"role": "system", "content": user_data_message})

        # Call Groq API for response
        try:
            response = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a strict fitness chatbot. ONLY answer fitness-related questions. If a question is unrelated, respond with: 'I only provide fitness-related information.'"},
                    {"role": "user", "content": user_text}
                ],
                model="llama3-8b-8192",
                max_tokens=1024
            )
            answer = response.choices[0].message.content

            # Ensure the model does not respond to non-fitness queries
            if "I only provide fitness-related information" in answer:
                st.warning("🚨 **Please ask fitness-related questions only!**")
                st.stop()

        except Exception as e:
            st.error(f"Error in generating response: {str(e)}")
            st.stop()

        # Append assistant's response to chat history
        st.session_state.chat_history.append({"role": "assistant", "content": answer})
        with st.chat_message(A_NAME, avatar="assistant"):
            st.markdown(answer)

        # Add a divider
        st.divider()
else:
    st.sidebar.warning("Please select both height and weight to start chatting!")
