FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV HF_HOME=/opt/huggingface

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY database ./database
COPY ingestion ./ingestion
COPY data/chroma ./data/chroma
COPY ipo_intelligence.db ./ipo_intelligence.db

# Download BGE-M3 during image build so Cloud Run does not
# need to download the model during every cold start.
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('BAAI/bge-m3')"

EXPOSE 8080

CMD ["sh", "-c", "uvicorn app.api.main:app --host 0.0.0.0 --port ${PORT:-8080}"]