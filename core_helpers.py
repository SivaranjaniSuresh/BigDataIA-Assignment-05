import os

import openai
import requests
import streamlit as st
from googletrans import LANGUAGES, Translator
from pydub import AudioSegment
from pytube import YouTube

openai.api_key = os.environ.get("OPEN_AI_API")


def get_language_code(language_name):
    for code, name in LANGUAGES.items():
        if name.lower() == language_name.lower():
            return code
    return None


def translate_latin_text(input_text, target_language):
    openai_api_key = openai.api_key
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openai_api_key}",
    }
    prompt = (
        f"Translate the following English text to {target_language} and write the text in Latin script and not in target language. "
        f"Please provide the LATIN TEXT of the translation on a separate line with the header 'Latin Script:'.\n\n"
        f"{input_text}"
    )
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "system", "content": prompt}],
        "max_tokens": 1024,
        "temperature": 0.5,
    }
    response = requests.post(
        "https://api.openai.com/v1/chat/completions", headers=headers, json=data
    )
    response_json = response.json()

    translated_message = response_json["choices"][0]["message"]["content"].strip()

    # Extract the translated text
    translated_text = translated_message.split("\n")[0]

    return translated_text


def translate_text(input_text, target_language):
    openai_api_key = openai.api_key
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openai_api_key}",
    }
    prompt = (
        f"Translate the following English text to {target_language} and also write the text in Latin script. "
        f"Please provide the translation on a separate line with the header '{target_language}:', followed by a line break, and then the Latin script on the next line with the header 'Latin Script:'.\n\n"
        f"{input_text}"
    )
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "system", "content": prompt}],
        "max_tokens": 1024,
        "temperature": 1,
    }
    response = requests.post(
        "https://api.openai.com/v1/chat/completions", headers=headers, json=data
    )
    response_json = response.json()

    translated_message = response_json["choices"][0]["message"]["content"].strip()

    # Extract the translated text
    translated_text = translated_message.split("\n")[0]
    translated_text_latin = translated_message.split("\n")[1]

    # Get the target language code
    target_language_code = get_language_code(target_language)

    return translated_text, translated_text_latin, target_language_code


def download_audio(yt_url):
    yt = YouTube(yt_url)
    audio_stream = yt.streams.filter(only_audio=True, file_extension="mp4").first()
    audio_file = audio_stream.download(filename="temp_audio")
    mp4_audio = AudioSegment.from_file(audio_file, format="mp4")
    mp3_file = "temp_audio.mp3"
    mp4_audio.export(mp3_file, format="mp3")
    os.remove(audio_file)
    return mp3_file


def chat_with_gpt(itinerary, user_question):
    openai_api_key = openai.api_key
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openai_api_key}",
    }
    prompt = f"The following is a travel itinerary:\n\n{itinerary}\n\nUser: {user_question}\n\nAssistant:"
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "system", "content": prompt}],
        "max_tokens": 1024,
        "temperature": 0.6,
    }
    response = requests.post(
        "https://api.openai.com/v1/chat/completions", headers=headers, json=data
    )
    response_json = response.json()

    return response_json["choices"][0]["message"]["content"].strip()


def generate_itinerary_by_youtube(transcript, days):
    transcript_data = transcript
    prompt = f"Based on the following information from the travel vlog transcript which is obtained from a youtube video, create a very detailed {days}-day travel itinerary with time stamp.\n\n Youtube Video Transcript: {transcript_data}\n\nItinerary:"
    openai_api_key = openai.api_key
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openai_api_key}",
    }
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "system", "content": prompt}],
        "max_tokens": 1024,
        "temperature": 0.6,
    }
    response = requests.post(
        "https://api.openai.com/v1/chat/completions", headers=headers, json=data
    )
    response_json = response.json()

    return response_json["choices"][0]["message"]["content"].strip()


def generate_itinerary_by_user_specs(city, days):
    prompt = f"Create a detailed {days}-day travel itinerary with time for a trip to {city}. Include various attractions, activities, and places to visit that are popular in the city.\n\nItinerary:"
    openai_api_key = openai.api_key
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openai_api_key}",
    }
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "system", "content": prompt}],
        "max_tokens": 1024,
        "temperature": 0.6,
    }
    response = requests.post(
        "https://api.openai.com/v1/chat/completions", headers=headers, json=data
    )
    response_json = response.json()

    return response_json["choices"][0]["message"]["content"].strip()


# Define function to transcribe audio using OpenAI API
def transcribe_audio(audio_file):
    with open(audio_file, "rb") as audio:
        response = openai.Audio.transcribe("whisper-1", audio)
        return response["text"]


def render_conversation(qa, role):
    if role == "user":
        st.markdown(
            f'<p style="color:#1abc9c;font-size:18px;font-weight:bold;margin-bottom:2px;">{role.capitalize()}:</p>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<p style="color:#ffffff;font-size:16px;margin-top:0px;">{qa[len(role) + 2:]}</p>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f'<p style="color:#f63366;font-size:18px;font-weight:bold;margin-bottom:2px;">{role.capitalize()}:</p>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<p style="color:#ffffff;font-size:16px;margin-top:0px;">{qa[len(role) + 2:]}</p>',
            unsafe_allow_html=True,
        )


def get_gpt_answer(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.6,
    )
    return response.choices[0].message["content"].strip()
