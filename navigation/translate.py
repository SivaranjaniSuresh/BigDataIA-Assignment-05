import base64
import os
import tempfile
from io import BytesIO

import streamlit as st
from dotenv import load_dotenv
from google.cloud import texttospeech

from core_helpers import translate_text

load_dotenv()
GOOGLE_APPLICATION_CREDENTIALS = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")


def synthesize_speech(text, language):
    client = texttospeech.TextToSpeechClient()

    input_text = texttospeech.SynthesisInput(text=text)
    voice = texttospeech.VoiceSelectionParams(
        language_code=language,
        ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL,
    )
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )

    response = client.synthesize_speech(
        request={"input": input_text, "voice": voice, "audio_config": audio_config}
    )

    audio_content = response.audio_content
    audio_file = BytesIO(audio_content)

    return audio_file


def translate():
    st.markdown(
        """
    <h1 style="text-align:center;">The Tower of Babel:  Speak Like a Local, Wherever You Go</h1>
    """,
        unsafe_allow_html=True,
    )
    st.write(
        "Traveling to a new country can be an adventure, but it can also be a challenge if you don't speak the language. Enter Tower of Babel, your personal translator and text-to-speech companion. With Tower of Babel, you can speak like a local, wherever you go. Enter your text, select your target language, and hear your words come to life in stunning text-to-speech. From ordering at a restaurant to asking for directions, Tower of Babel makes it easy to communicate with the locals and immerse yourself in the culture."
    )

    # Get user inputs
    input_text = st.text_input("Enter text to translate:")
    target_language = st.text_input(
        "Enter target language (e.g., French, German, Spanish, etc.):"
    )

    # Translate button
    if st.button("Translate"):
        if input_text and target_language:
            (
                translated_text,
                translated_latin_text,
                target_language_code,
            ) = translate_text(input_text, target_language)
            st.write(f"Translated text in {target_language}:")
            st.write(translated_text)
            st.write(translated_latin_text)
            translated_text = translated_text.split(":", 1)[-1].strip()
            audio_content = synthesize_speech(translated_text, target_language_code)
            st.audio(audio_content, format="audio/wav")

        else:
            st.warning("Please provide both input text and target language.")


if __name__ == "__main__":
    translate()
