import streamlit as st
import openai
import requests
from PIL import Image
import tempfile
import json

# Load your OpenAI key securely
client = openai.OpenAI()  # new OpenAI client object
ocr_api_key = st.secrets["OCR_API_KEY"]        # Store your OCR.space API key here too

# ----------- Step 1: Extract Text from Screenshot via OCR.space API -----------
def extract_text_from_screenshot(image):
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
        image.convert("RGB").save(tmp_file.name, format='JPEG', quality=80)
        with open(tmp_file.name, 'rb') as f:
            try:
                r = requests.post(
                    'https://api.ocr.space/parse/image',
                    files={'filename': f},
                    data={'apikey': ocr_api_key, 'language': 'eng'}
                )
                result = r.json()
                st.write(result)  # Debug: Show full OCR response
                text = result['ParsedResults'][0]['ParsedText'] if 'ParsedResults' in result else "OCR failed."
            except (json.JSONDecodeError, requests.exceptions.RequestException) as e:
                st.error("OCR request failed or returned invalid JSON.")
                st.stop()
            return text

# ----------- Step 2: Clean and Format the Chat Text -----------
def clean_chat_text(raw_text):
    lines = raw_text.split('\n')
    cleaned = [line.strip() for line in lines if line.strip() and len(line) > 2]
    return "\n".join(cleaned)

# ----------- Step 3: Generate Response via GPT -----------
def generate_response(chat_history, goal="flirty but respectful"):
    prompt = f"""
You are an AI assistant helping a user engage in an ongoing dating app conversation. Based on the chat history below, suggest 1 best context-aware next line the user can send. Match the user's intent which is: {goal}.

Chat History:
{chat_history}

Suggestion:
"""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a witty and helpful dating conversation assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=300
    )

    return response.choices[0].message.content

# ----------- Streamlit App -----------
st.set_page_config(page_title="Dating Chat Assistant", layout="centered")
st.title("\U0001F4AC Dating Chat Assistant")

st.markdown("Upload a screenshot of your dating app chat and get the perfect next line!")

uploaded_file = st.file_uploader("Upload Chat Screenshot", type=["png", "jpg", "jpeg"])

intent = st.selectbox("What is your goal for this chat?", [
    "funny and warm",
    "flirty but respectful",
    "genuine and serious",
    "casual and witty",
    "friendly and polite"
])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Chat Screenshot", use_column_width=True)

    with st.spinner("Extracting chat and generating suggestion..."):
        raw_text = extract_text_from_screenshot(image)
        formatted_text = clean_chat_text(raw_text)

        st.subheader("\U0001F4DD Extracted Chat History")
        st.text(formatted_text)

        suggestion = generate_response(formatted_text, goal=intent)

        st.subheader("\U0001F4A1 Suggested Next Line")
        st.markdown(f"**{suggestion.strip()}**")

st.markdown("---")
st.caption("Made with ❤️ using GPT-4, Streamlit, and OCR.space")
