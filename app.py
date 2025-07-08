import streamlit as st
import openai

# Load your OpenAI key securely
client = openai.OpenAI()  # new OpenAI client object

# ----------- Step: Clean and Format the Chat Text -----------
def clean_chat_text(raw_text):
    lines = raw_text.split('\n')
    cleaned = [line.strip() for line in lines if line.strip() and len(line) > 2]
    return "\n".join(cleaned)

# ----------- Step: Generate Response via GPT -----------
def generate_response(user_profile, match_profile, goal, chat_history):
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

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": f"You are a dating assistant who helps users craft {goal} replies in dating app conversations."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=300
    )

    return response.choices[0].message.content

# ----------- Streamlit App -----------
st.set_page_config(page_title="Dating Chat Assistant", layout="centered")
st.title("\U0001F4AC Dating Chat Assistant")

st.markdown("Step 1: Tell us about yourself")
with st.form("user_form"):
    user_name = st.text_input("Your Name")
    user_age = st.text_input("Your Age")
    user_profession = st.text_input("Your Profession")
    user_city = st.text_input("Your City")
    user_goal = st.text_input("What are you looking for?")
    submitted_user = st.form_submit_button("Continue")

if submitted_user:
    st.markdown("Step 2: Tell us about your match")
    with st.form("match_form"):
        match_name = st.text_input("Match's Name")
        match_age = st.text_input("Match's Age")
        match_profession = st.text_input("Match's Profession")
        match_city = st.text_input("Match's City")
        match_goal = st.text_input("What is your match looking for?")
        submitted_match = st.form_submit_button("Continue")

    if submitted_match:
        st.markdown("Step 3: What is your goal for this chat?")
        intent = st.selectbox("Select chat goal", [
            "funny and warm",
            "flirty but respectful",
            "genuine and serious",
            "casual and witty",
            "friendly and polite"
        ])

        st.markdown("Step 4: Paste your ongoing chat")
        chat_input = st.text_area("Paste the most recent messages (including your replies if any):", height=200)

        if chat_input:
            formatted_text = clean_chat_text(chat_input)

            st.subheader("\U0001F4DD Chat History")
            st.text(formatted_text)

            if st.button("Generate Response"):
                user_profile = {
                    "name": user_name,
                    "age": user_age,
                    "profession": user_profession,
                    "city": user_city,
                    "looking_for": user_goal
                }
                match_profile = {
                    "name": match_name,
                    "age": match_age,
                    "profession": match_profession,
                    "city": match_city,
                    "looking_for": match_goal
                }

                suggestion = generate_response(user_profile, match_profile, intent, formatted_text)

                st.subheader("\U0001F4A1 Suggested Next Line")
                st.markdown(f"**{suggestion.strip()}**")

st.markdown("---")
st.caption("Made with ❤️ using GPT-4 and Streamlit")
