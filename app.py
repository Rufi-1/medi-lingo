import streamlit as st
import google.generativeai as genai
from PIL import Image
import json

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Medi-Lingo", page_icon="💊")

# Custom CSS to make it look nicer
st.markdown("""
    <style>
    .main-header {font-size: 2.5rem; color: #4285F4; font-weight: 700;}
    .sub-header {font-size: 1.5rem; color: #333;}
    .warning-box {background-color: #fce8e6; padding: 15px; border-radius: 5px; border-left: 5px solid #d93025;}
    </style>
""", unsafe_allow_html=True)

# --- 2. SIDEBAR (API KEY) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3063/3063822.png", width=80)
    st.title("Settings")
    api_key = st.text_input("Enter Google API Key", type="password")
    st.caption("Get your key from [Google AI Studio](https://aistudio.google.com/)")
    st.markdown("---")
    st.markdown("**About:**\nThis app helps elderly patients understand medicine labels in their local language using Gemini AI.")

# --- 3. MAIN APP INTERFACE ---
st.markdown('<p class="main-header">💊 Medi-Lingo: The Patient Advocate</p>', unsafe_allow_html=True)
st.write("Upload a photo of a medicine strip to understand its usage, schedule, and side effects in simple language.")

uploaded_file = st.file_uploader("📸 Take a photo of the medicine", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Show the image
    image = Image.open(uploaded_file)
    st.image(image, caption='Uploaded Medicine', use_column_width=True)

    # --- 4. THE MAGIC BUTTON ---
    if st.button("🔍 Analyze Medicine", type="primary"):
        if not api_key:
            st.error("Please enter your Google API Key in the sidebar to continue.")
        else:
            with st.spinner("Consulting the AI Doctor... (This may take a few seconds)"):
                try:
                    # Configure Gemini
                    genai.configure(api_key=api_key)
                    # Use standard stable model
                    model = genai.GenerativeModel('gemini-2.5-flash')

                    # The Golden Prompt (Same as you tested)
                    prompt = """
                    You are an empathetic Medical Assistant.
                    Analyze this medicine image. Return ONLY a JSON response with these keys:
                    {
                        "medicine_name": "Name of medicine",
                        "usage_simple": "What it cures in 1 simple sentence",
                        "schedule_advice": "General advice on when to take it",
                        "side_effects": "Top 2 side effects as a list",
                        "summary_translated": "A comforting summary in Hindi"
                    }
                    """
                    
                    # Call Gemini API
                    response = model.generate_content([prompt, image])
                    
                    # Clean the response (Remove markdown if present)
                    raw_text = response.text.strip()
                    clean_text = raw_text.replace("```json", "").replace("```", "")
                    data = json.loads(clean_text)

                    # --- 5. DISPLAY RESULTS ---
                    st.success("Analysis Complete!")
                    
                    # Medicine Name
                    st.subheader(f"🏷️ {data.get('medicine_name', 'Unknown Medicine')}")
                    
                    # Usage & Schedule
                    col1, col2 = st.columns(2)
                    with col1:
                        st.info(f"**Usage:**\n{data.get('usage_simple', 'N/A')}")
                    with col2:
                        st.info(f"**When to take:**\n{data.get('schedule_advice', 'Consult Doctor')}")

                    # Side Effects (Warning Box)
                    side_effects_list = data.get('side_effects', [])
                    if isinstance(side_effects_list, list):
                        effects_text = "\n".join([f"- {effect}" for effect in side_effects_list])
                    else:
                        effects_text = side_effects_list
                    
                    st.markdown(f"""
                        <div class="warning-box">
                        <b>⚠️ Common Side Effects:</b><br>
                        {effects_text}
                        </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown("---")
                    
                    # Hindi Translation Section
                    st.header("🇮🇳 Hindi Summary")
                    hindi_text = data.get('summary_translated', 'Translation unavailable')
                    st.success(hindi_text)
                    
                    # Audio Player (Text-to-Speech)
                    # We use a simple trick to generate audio for the prototype
                    # (Note: In a real startup, you'd use Google Cloud TTS, but this works for hackathons)
                    import urllib.parse
                    encoded_text = urllib.parse.quote(hindi_text)
                    audio_url = f"https://translate.google.com/translate_tts?ie=UTF-8&client=tw-ob&q={encoded_text}&tl=hi"
                    st.audio(audio_url, format='audio/mp3')

                except Exception as e:

                    st.error(f"An error occurred: {e}")
