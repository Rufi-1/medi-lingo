import streamlit as st
import google.generativeai as genai
from PIL import Image
import json
from gtts import gTTS  # <--- NEW IMPORT
import os

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Medi-Lingo", page_icon="💊")

st.markdown("""
    <style>
    .main-header {font-size: 2.5rem; color: #4285F4; font-weight: 700;}
    .warning-box {background-color: #fce8e6; padding: 15px; border-radius: 5px; border-left: 5px solid #d93025;}
    </style>
""", unsafe_allow_html=True)

# --- 2. SIDEBAR ---
with st.sidebar:
    st.title("Settings")
    api_key = st.text_input("Enter Google API Key", type="password")
    # Helpful link for the judges
    st.markdown("[Get a free Gemini API key here](https://aistudio.google.com/app/apikey)")
    
    st.markdown("---")
    st.markdown("**Note for Judges:**\nThis app requires an API key to prevent quota exhaustion. Please use your own key to test.")
# --- 3. MAIN APP ---
st.markdown('<p class="main-header">💊 Medi-Lingo: The Patient Advocate</p>', unsafe_allow_html=True)
st.write("Upload a photo of a medicine strip to understand its usage in Hindi.")

uploaded_file = st.file_uploader("📸 Take a photo of the medicine", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption='Uploaded Medicine', use_column_width=True)

    if st.button("🔍 Analyze Medicine", type="primary"):
        if not api_key:
            st.error("Please enter your API Key!")
        else:
            with st.spinner("Consulting the AI Doctor..."):
                try:
                    genai.configure(api_key=api_key)
                    # Use the standard model version
                    model = genai.GenerativeModel('gemini-2.5-flash')

                    prompt = """
                    Analyze this medicine image. Return ONLY a JSON response with these keys:
                    {
                        "medicine_name": "Name of medicine",
                        "usage_simple": "What it cures in 1 simple sentence",
                        "schedule_advice": "General advice on when to take it",
                        "side_effects": "Top 2 side effects",
                        "summary_translated": "A comforting summary in Hindi"
                    }
                    """
                    
                    response = model.generate_content([prompt, image])
                    text = response.text.replace("```json", "").replace("```", "")
                    data = json.loads(text)

                    # --- DISPLAY RESULTS ---
                    st.success("Analysis Complete!")
                    st.subheader(f"🏷️ {data.get('medicine_name', 'Unknown')}")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.info(f"**Usage:** {data.get('usage_simple')}")
                    with col2:
                        st.info(f"**When:** {data.get('schedule_advice')}")

                    st.markdown(f'<div class="warning-box"><b>⚠️ Side Effects:</b><br>{data.get("side_effects")}</div>', unsafe_allow_html=True)
                    
                    st.markdown("---")
                    st.header("🇮🇳 Hindi Audio")
                    hindi_text = data.get('summary_translated', 'No text')
                    st.write(hindi_text)
                    
                    # --- NEW AUDIO FIX ---
                    # Create audio file in memory
                    tts = gTTS(text=hindi_text, lang='hi')
                    tts.save("audio.mp3")
                    
                    # Play the audio file
                    st.audio("audio.mp3", format="audio/mp3")

                except Exception as e:
                    st.error(f"Error: {e}")

