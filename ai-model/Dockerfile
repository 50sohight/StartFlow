FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    N_GPU_LAYERS=0 \
    N_CTX=2048 \
    MODEL_DIR=/service/models

WORKDIR /service

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    libgomp1 \
    curl \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.docker.txt ./requirements.txt

RUN pip install --upgrade pip && \
    pip install -r requirements.txt

COPY app ./app
RUN mkdir -p /service/models

# Healthcheck for container orchestration
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
  CMD curl --fail http://127.0.0.1:8000/ || exit 1

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]