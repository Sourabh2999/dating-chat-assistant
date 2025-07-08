import streamlit as st
import openai
from openai import RateLimitError

# Load your OpenAI key securely
client = openai.OpenAI()  # new OpenAI client object

# ----------- Step: Clean and Format the Chat Text -----------
def clean_chat_text(raw_text):
    lines = raw_text.split('\n')
    cleaned = [line.strip() for line in lines if line.strip() and len(line) > 2]
    return "\n".join(cleaned)

# ----------- Step: Generate Response via GPT -----------
def generate_response(user_profile, match_profile, goal, chat_history, model):
    prompt = f"""
You are an AI assistant helping a user engage in an ongoing dating app conversation.

User Details:
Name: {user_profile['name']}, Age: {user_profile['age']}, Profession: {user_profile['profession']}, City: {user_profile['city']}, Looking for: {user_profile['looking_for']}

Match Details:
Name: {match_profile['name']}, Age: {match_profile['age']}, Profession: {match_profile['profession']}, City: {match_profile['city']}, Looking for: {match_profile['looking_for']}

Chat Goal: {goal}

Chat History:
{chat_history}

Based on all the context above, suggest the user's best next line:
"""

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": f"You are a dating assistant who helps users craft {goal} replies in dating app conversations."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=300
        )
        return response.choices[0].message.content
    except RateLimitError:
        st.error("OpenAI API rate limit reached. Please wait a few seconds and try again.")
        return None

# ----------- Streamlit App -----------
st.set_page_config(page_title="Dating Chat Assistant", layout="centered")
st.title("\U0001F4AC Dating Chat Assistant")

if "step" not in st.session_state:
    st.session_state.step = 1

# Step 1: User Info
if st.session_state.step == 1:
    st.markdown("### Step 1: Tell us about yourself")
    with st.form("user_form"):
        user_name = st.text_input("Your Name")
        user_age = st.text_input("Your Age")
        user_profession = st.text_input("Your Profession")
        user_city = st.text_input("Your City")
        user_goal = st.text_input("What are you looking for?")
        submitted_user = st.form_submit_button("Continue")

    if submitted_user:
        st.session_state.user_profile = {
            "name": user_name,
            "age": user_age,
            "profession": user_profession,
            "city": user_city,
            "looking_for": user_goal
        }
        st.session_state.step = 2
        st.rerun()

# Step 2: Match Info
elif st.session_state.step == 2:
    st.markdown("### Step 2: Tell us about your match")
    with st.form("match_form"):
        match_name = st.text_input("Match's Name")
        match_age = st.text_input("Match's Age")
        match_profession = st.text_input("Match's Profession")
        match_city = st.text_input("Match's City")
        match_goal = st.text_input("What is your match looking for?")
        submitted_match = st.form_submit_button("Continue")

    if submitted_match:
        st.session_state.match_profile = {
            "name": match_name,
            "age": match_age,
            "profession": match_profession,
            "city": match_city,
            "looking_for": match_goal
        }
        st.session_state.step = 3
        st.rerun()

# Step 3: Chat Goal
elif st.session_state.step == 3:
    st.markdown("### Step 3: What is your goal for this chat?")
    intent = st.selectbox("Select chat goal", [
        "funny and warm",
        "flirty but respectful",
        "genuine and serious",
        "casual and witty",
        "friendly and polite"
    ])
    model_choice = st.selectbox("Choose model", ["gpt-4o", "gpt-3.5-turbo"], index=0)
    if st.button("Continue"):
        st.session_state.intent = intent
        st.session_state.model = model_choice
        st.session_state.step = 4
        st.rerun()

# Step 4: Chat History
elif st.session_state.step == 4:
    st.markdown("### Step 4: Paste your ongoing chat")
    chat_input = st.text_area("Paste the most recent messages (including your replies if any):", height=200)
    if chat_input:
        if st.button("Generate Response"):
            st.session_state.chat_history = clean_chat_text(chat_input)
            suggestion = generate_response(
                st.session_state.user_profile,
                st.session_state.match_profile,
                st.session_state.intent,
                st.session_state.chat_history,
                st.session_state.model
            )
            if suggestion:
                st.session_state.suggestion = suggestion
                st.session_state.step = 5
                st.rerun()

# Step 5: Show Result
elif st.session_state.step == 5:
    st.markdown("### Chat History")
    st.text(st.session_state.chat_history)
    st.markdown("### \U0001F4A1 Suggested Next Line")
    st.markdown(f"**{st.session_state.suggestion.strip()}**")

st.markdown("---")
st.caption("Made with ❤️ using GPT-4 and Streamlit")
