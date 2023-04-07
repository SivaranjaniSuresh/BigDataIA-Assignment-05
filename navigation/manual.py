import os

import openai
import requests
import streamlit as st
from dotenv import load_dotenv

from core_helpers import translate_latin_text, translate_text

load_dotenv()
# load_dotenv()
openai.api_key = os.environ.get("OPEN_AI_API")
unsplash_api_key = os.environ.get("UNSPLASH_API_KEY")


def get_city_language(city):
    """Get the language spoken in a particular city."""
    prompt = f"What language is spoken in {city}?"
    openai_api_key = openai.api_key
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openai_api_key}",
    }
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "system", "content": prompt}],
        "max_tokens": 1024,
        "temperature": 1,
    }
    response = requests.post(
        "https://api.openai.com/v1/chat/completions", headers=headers, json=data
    )
    language = response.json()
    return language["choices"][0]["message"]["content"].strip()


# Define the create_phrasebook() function
def generate_phrasebook(city_name, language):
    openai_api_key = openai.api_key
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openai_api_key}",
    }
    prompt = (
        f"Please provide common phrases in {city_name} used by the locals for better understanding. Maintain decorum and language at all times."
        f"Please provide the phrase in the original language followed by a colon (:) and then the latin text translation in {language} separated by a line break.\n\n"
        f"For example:\nHello: {translate_latin_text('Hello', language)}\nGoodbye: {translate_latin_text('Goodbye', language)}"
    )
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "system", "content": prompt}],
        "temperature": 0.5,
        "max_tokens": 1024,
    }
    response = requests.post(
        "https://api.openai.com/v1/chat/completions", headers=headers, json=data
    )
    response_json = response.json()

    phrasebook = response_json["choices"][0]["message"]["content"].strip()

    phrasebook_lines = phrasebook.split("\n")

    st.write(
        "<h1 style='color: #4FB0AE; font-size: 36px; font-weight: bold; text-align: center;'>PHRASEBOOK</h1>",
        unsafe_allow_html=True,
    )

    phrasebook_text = "<div style='border: 2px solid #39FF14; padding: 10px;'>"
    for line in phrasebook_lines:
        try:
            english_word, translation = line.split(":")
            phrasebook_text += f"<p style='line-height: 1.5;'><span style='color: #cfd4d3; font-weight: bold;'>{english_word}</span>: <span style='color: #4FB0AE; font-weight: bold;'>{translation.strip()}</span></p>"
        except ValueError:
            continue
    phrasebook_text += "</div>"

    st.markdown(phrasebook_text, unsafe_allow_html=True)


def manual():
    # Set up Streamlit app
    st.markdown(
        """
    <h1 style="text-align:center;">Get a Phrasebook for Places you are Visiting, so you are aware of Local Lingo and Ettiquets</h1>
    """,
        unsafe_allow_html=True,
    )
    # Get user input for YouTube video URL
    city = st.text_input("Enter Cities you want to explore")
    if st.button("Generate Phrasebook"):
        language = get_city_language(city)
        generate_phrasebook(city, language)


if __name__ == "__main__":
    manual()
