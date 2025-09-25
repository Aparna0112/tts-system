FROM nvidia/cuda:11.8-runtime-ubuntu20.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y \
    python3.11 \
    python3.11-pip \
    python3.11-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip3.11 install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
RUN pip3.11 install --no-cache-dir -r requirements.txt

COPY app.py .

EXPOSE 8000

CMD ["python3.11", "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]