FROM python:3.9-slim

WORKDIR /app

# Install system dependencies for audio processing
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install -r requirements.txt

# Add Chatterbox TTS installation here
# RUN pip install chatterbox-tts

COPY . .

RUN mkdir -p /app/outputs

EXPOSE 8002

CMD ["python", "main.py"]