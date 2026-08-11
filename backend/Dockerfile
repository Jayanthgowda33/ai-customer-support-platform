FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev curl \
    && rm -rf /var/lib/apt/lists/*

ENV PIP_DEFAULT_TIMEOUT=120

COPY requirements.txt .

RUN pip install --no-cache-dir --retries 10 torch --index-url https://download.pytorch.org/whl/cpu

RUN pip install --no-cache-dir --retries 10 -r requirements.txt

# Pre-download the embedding model at build time so the first real
# chat request doesn't have to download it (which was causing timeouts).
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]