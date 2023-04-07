import os
import requests
import openai
import streamlit as st
from dotenv import load_dotenv
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
import base64
import io
from io import BytesIO

from core_helpers import (
    download_audio,
    generate_itinerary_by_youtube,
    get_gpt_answer,
    render_conversation,
    transcribe_audio,
)

load_dotenv()
openai.api_key = os.environ.get("OPEN_AI_API")
unsplash_api_key = os.environ.get("UNSPLASH_API_KEY")


def extract_locations_from_itinerary(itinerary):
    prompt = f"Please list the locations mentioned in the following itinerary, ignoring the day labels:\n\n{itinerary}\n\nLocations:\n"
    response = get_gpt_answer(prompt)
    locations = response.strip().split("\n")
    return locations


def get_unsplash_image(query, api_key):
    headers = {"Authorization": f"Client-ID {api_key}"}
    params = {"query": query, "orientation": "landscape", "per_page": 1}
    response = requests.get(
        "https://api.unsplash.com/search/photos", headers=headers, params=params
    )

    if response.status_code == 200:
        data = response.json()
        if data["results"]:
            return data["results"][0]["urls"]["small"]
    return None


def generate_pdf(itinerary, image_paths):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()

    # Add a title to the PDF
    title_style = styles["Heading1"]
    title_style.fontSize = 24
    title_style.spaceAfter = 20
    story.append(Paragraph("Travel Itinerary", title_style))

    # Add the itinerary text with adjusted styling
    itinerary_style = styles["BodyText"]
    itinerary_style.spaceAfter = 20
    itinerary_style.fontSize = 12
    for line in itinerary.split("\n"):
        story.append(Paragraph(line, itinerary_style))

    # Iterate over the image_paths and add the images and captions to the PDF
    for i in range(0, len(image_paths), 2):
        img1_url, img1_caption = image_paths[i]
        img1 = Image(requests.get(img1_url, stream=True).raw)
        img1.drawHeight = 200
        img1.drawWidth = 270
        img1.hAlign = "LEFT"
        caption1 = Paragraph(img1_caption, styles["BodyText"])

        if i + 1 < len(image_paths):
            img2_url, img2_caption = image_paths[i + 1]
            img2 = Image(requests.get(img2_url, stream=True).raw)
            img2.drawHeight = 200
            img2.drawWidth = 270
            img2.hAlign = "RIGHT"
            caption2 = Paragraph(img2_caption, styles["BodyText"])

            # Create a row with two images and their captions
            image_row = [[img1, img2], [caption1, caption2]]
        else:
            image_row = [[img1], [caption1]]

        # Add the row to the story
        table = Table(
            image_row, colWidths=[img1.drawWidth + 10 * inch / 72, img2.drawWidth]
        )
        table.setStyle(
            [
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("GRID", (0, 0), (-1, -1), 1, colors.transparent),
                ("BOX", (0, 0), (-1, -1), 1, colors.transparent),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ]
        )
        story.append(table)
        story.append(Spacer(1, 20))

    doc.build(story)
    buffer.seek(0)
    return buffer


def get_binary_file_downloader_link(file_path, file_label="File"):
    with open(file_path, "rb") as f:
        data = f.read()
    b64 = base64.b64encode(data).decode()
    return f'<a href="data:application/octet-stream;base64,{b64}" download="{file_label}.pdf">Download {file_label} as PDF</a>'


def youtube():
    # Set up Streamlit app
    st.title("Get Itenary Based on a YouTube Vlog")
    # Get user input for YouTube video URL
    url = st.text_input("Enter YouTube video URL:")
    days = st.number_input(
        "Enter the number of days for the travel itinerary:", min_value=1, value=3
    )

    # Initialize session state variables
    if "itinerary" not in st.session_state:
        st.session_state.itinerary = None

    # If URL is provided, extract the audio, transcribe it, and display the result
    if st.button("Get Itinerary"):
        # Download audio from YouTube video
        audio_content = download_audio(url)
        st.write(audio_content)
        # Transcribe audio using OpenAI API
        transcript = transcribe_audio(audio_content)
        # Display transcript
        itinerary = generate_itinerary_by_youtube(transcript, days)
        st.session_state.itinerary = itinerary
        st.success("Itinerary Generated!")

    # New section: Ask questions about the itinerary
    if st.session_state.itinerary:
        st.write(
            "<h1 style='color: #4FB0AE; font-size: 36px; font-weight: bold; text-align: center;'>Travel Itinerary</h1>",
            unsafe_allow_html=True,
        )

        itinerary_days = st.session_state.itinerary.split("\n")
        formatted_itinerary = ""
        for day in itinerary_days:
            if day.startswith("Day"):
                formatted_itinerary += (
                    f"<span style='color: #cfd4d3; font-weight: bold;'>{day}</span><br>"
                )
            else:
                formatted_itinerary += (
                    f"<span style='color: #4FB0AE; font-weight: bold;'>{day}</span><br>"
                )

        st.write(
            f"<div style='border: 3px solid #39FF14; padding: 10px; border-radius: 5px;'>{formatted_itinerary}</div>",
            unsafe_allow_html=True,
        )

        locations_list = extract_locations_from_itinerary(st.session_state.itinerary)
        # Check if the locations are concatenated in a single string or spread across a list
        if len(locations_list) == 1 and "," in locations_list[0]:
            locations = locations_list[0].split(", ")
        else:
            locations = locations_list

        st.header("Locations with Images")

        location_iter = iter(locations)
        for location in location_iter:
            cleaned_location1 = location.strip("- ").strip()
            image_url1 = get_unsplash_image(cleaned_location1, unsplash_api_key)

            try:
                location = next(location_iter)
                cleaned_location2 = location.strip("- ").strip()
                image_url2 = get_unsplash_image(cleaned_location2, unsplash_api_key)
            except StopIteration:
                cleaned_location2 = None
                image_url2 = None

            col1, col2 = st.columns(2)

            if cleaned_location1 and image_url1:
                col1.image(image_url1, caption=cleaned_location1, use_column_width=True)

            if cleaned_location2 and image_url2:
                col2.image(image_url2, caption=cleaned_location2, use_column_width=True)
        image_paths = []
        for location in locations:
            cleaned_location = location.strip("- ").strip()
            image_url = get_unsplash_image(cleaned_location, unsplash_api_key)
            image_paths.append((image_url, cleaned_location))

        pdf_path = "itinerary.pdf"
        pdf_buffer = generate_pdf(st.session_state.itinerary, image_paths)
        b64_pdf = base64.b64encode(pdf_buffer.getvalue()).decode()
        pdf_display = f'<a href="data:application/pdf;base64,{b64_pdf}" download="itinerary.pdf">Download Itinerary</a>'
        st.markdown(pdf_display, unsafe_allow_html=True)
        if "conversation_history" not in st.session_state:
            st.session_state.conversation_history = []

        # Display previous questions and answers
        st.header("Intelligent Chat")
        for i, qa in enumerate(st.session_state.conversation_history):
            role = "user" if i % 2 == 0 else "gpt-3.5-turbo"
            render_conversation(qa, role)

        user_question = st.text_input("Enter your question about the itinerary:")
        if st.button("Ask Question"):
            prompt = f"My travel itinerary is\n{st.session_state.itinerary}\n\n"
            for qa in st.session_state.conversation_history:
                prompt += f"{qa}\n"
            prompt += f"User: {user_question}\ngpt-3.5-turbo:"
            answer = get_gpt_answer(prompt)

            st.session_state.conversation_history.append(f"User: {user_question}")
            st.session_state.conversation_history.append(f"gpt-3.5-turbo: {answer}")
            st.text_area(f"gpt-3.5-turbo:", value=answer)


if __name__ == "__main__":
    youtube()
