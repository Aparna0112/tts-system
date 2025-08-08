FROM python:3.9-slim

WORKDIR /app

# Install system dependencies for audio processing
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install -r requirements.txt

# Add Kokkoro TTS installation here
# RUN pip install kokkoro-tts

COPY . .

RUN mkdir -p /app/outputs

EXPOSE 8001

CMD ["python", "main.py"]