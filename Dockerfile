FROM python:3.10.6

RUN pip install --upgrade pip

WORKDIR /app

ADD userinterface.py requirements.txt core_helpers.py __init__.py temp_audio.mp3 inductive-world-378421-15002e5d37b5.json /app/

RUN pip install -r requirements.txt

RUN apt-get update && \
    apt-get install -y ffmpeg

RUN python -m spacy download en_core_web_sm

ADD navigation /app/navigation/
ADD navigation/forex.py /app/navigation/
ADD navigation/manual.py /app/navigation/
ADD navigation/translate.py /app/navigation/
ADD navigation/youtube.py /app/navigation/
ADD navigation/__init__.py /app/navigation/
ADD navigation/emergency_contacts.py /app/navigation/


EXPOSE 8080

CMD ["streamlit", "run", "userinterface.py", "--server.port", "8080"]