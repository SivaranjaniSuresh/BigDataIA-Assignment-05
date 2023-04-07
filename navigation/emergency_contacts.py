import os

import openai
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.environ.get("OPEN_AI_API")

# GPT-3 model settings
model_engine = "davinci"
max_tokens = 60
temperature = 0.8


def generate_emergency_contacts(city):
    prompt = f"Generate a list of emergency contacts for {city} "
    openai_api_key = openai.api_key
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openai_api_key}",
    }

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

    return response_json["choices"][0]["message"]["content"].strip().split("\n")


def emergency_contacts(city):
    if city:
        # Retrieve the emergency contacts for the city
        emergency_contacts = generate_emergency_contacts(city)

        # Display the emergency contacts
        if emergency_contacts:
            st.write(f"Emergency contacts for {city}:")
            for contact in emergency_contacts:
                st.write(f"- {contact}")
        else:
            st.write(f"No emergency contacts found for {city}")


def emergency():
    st.markdown(
        """
    <h1 style="text-align:center;">Emergency Contacts</h1>
    """,
        unsafe_allow_html=True,
    )
    city = st.text_input("Enter the city where you are located")
    if st.button("Get Emergency Contacts"):
        language = emergency_contacts(city)


if __name__ == "__main__":
    emergency_contacts()
