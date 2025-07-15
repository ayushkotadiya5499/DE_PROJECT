import streamlit as st
from PIL import Image
import pytesseract
from deep_translator import GoogleTranslator
from langchain_core.prompts import PromptTemplate
from langchain_community.llms import OpenAI
from gtts import gTTS
from dotenv import load_dotenv
import os
import tempfile

import os
# Optional: load .env file in local dev environment
try:
    from dotenv import load_dotenv
    load_dotenv()
except:
    pass

# Access your secrets
openai_api_key = os.getenv("OPENAI_API_KEY")
google_api_key = os.getenv("GOOGLE_API_KEY")


# Load environment variables
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

if openai_api_key:
    os.environ["OPENAI_API_KEY"] = openai_api_key
else:
    st.warning("⚠️ Please set OPENAI_API_KEY in your .env file.")

# Path to Tesseract (update if needed)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

st.title("🆔 ID Card OCR + Translate + Speak + AI Summary")

# Language options
languages = {
    "English": "en",
    "Hindi": "hi",
    "Gujarati": "gu",
    "Tamil": "ta",
    "Telugu": "te",
    "Bengali": "bn",
    "Marathi": "mr"
}

# Upload image
uploaded_file = st.file_uploader("📤 Upload ID Card Image", type=["png", "jpg", "jpeg"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="📸 Uploaded Image", use_container_width=True)

    # OCR
    extracted_text = pytesseract.image_to_string(image)
    st.subheader("📄 Extracted Text:")
    st.text(extracted_text)

    # Translate & Speak
    target_lang_name = st.selectbox("🌍 Translate and Speak in Language:", list(languages.keys()))
    target_lang_code = languages[target_lang_name]

    if st.button("🌐 Translate + 🔊 Speak"):
        try:
            translated_text = GoogleTranslator(source='auto', target=target_lang_code).translate(extracted_text)
            st.subheader("🔤 Translated Text:")
            st.text(translated_text)

            tts = gTTS(text=translated_text, lang=target_lang_code)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_audio:
                tts.save(tmp_audio.name)
                st.audio(tmp_audio.name, format="audio/mp3")

            st.success("✅ Translation and speech complete!")
            st.toast("🎉 Translated and Spoken!")
            st.balloons()

        except Exception as e:
            st.error(f"❌ Error in translation or speech: {e}")

    # AI Summary + Speak
    with st.expander("💡 AI Summary (OpenAI)", expanded=False):
        try:
            llm = OpenAI(temperature=0.7)
            prompt = PromptTemplate(
                input_variables=["text"],
                template="Summarize the following ID card information:\n{text}"
            )
            chain = prompt | llm
            summary = chain.invoke({"text": extracted_text})

            st.subheader("🧠 AI Summary:")
            st.write(summary)

            # English summary audio
            tts_summary = gTTS(text=summary, lang='en')
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_summary_audio:
                tts_summary.save(tmp_summary_audio.name)
                st.audio(tmp_summary_audio.name, format="audio/mp3")

            st.success("✅ AI Summary Complete!")
            st.toast("🧠 AI Summary Done!")
            st.snow()

            # 🔁 Translate Summary to another language and speak
            st.subheader("🌐 Translate AI Summary + 🔊 Speak")
            summary_lang_name = st.selectbox("🗣️ Choose Language for Summary:", list(languages.keys()), key="summary_lang")
            summary_lang_code = languages[summary_lang_name]

            if st.button("🔁 Translate & Speak Summary"):
                translated_summary = GoogleTranslator(source='auto', target=summary_lang_code).translate(summary)
                st.text(translated_summary)

                tts_translated_summary = gTTS(text=translated_summary, lang=summary_lang_code)
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_translated_summary_audio:
                    tts_translated_summary.save(tmp_translated_summary_audio.name)
                    st.audio(tmp_translated_summary_audio.name, format="audio/mp3")

                st.success("✅ Summary translation and speech done!")

        except Exception as e:
            st.warning(f"⚠️ AI Summary failed: {e}")
