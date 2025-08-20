FROM bitnami/python:3.10

WORKDIR /app

# Variables de entorno para una mejor gestión de la memoria
ENV PYTHONUNBUFFERED=1
ENV PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:256
ENV TRANSFORMERS_CACHE=/app/.cache/transformers
ENV HF_HOME=/app/.cache/huggingface

RUN pip install --upgrade pip
RUN apt-get update && apt-get install -y git curl && apt-get clean && rm -rf /var/lib/apt/lists/*

# Directorios de cache
RUN mkdir -p /app/.cache/transformers /app/.cache/huggingface

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ app/

# Crear directorio pdf
RUN mkdir -p pdf/

# Crear directorio chroma_db
RUN mkdir -p chroma_db/

EXPOSE 8501

HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8501/_stcore/health

CMD ["streamlit", "run", "app/app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.maxUploadSize=200"]