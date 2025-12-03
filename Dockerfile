FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema (tesseract)
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    libleptonica-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalarlos
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto
COPY . .

EXPOSE 8000

# Arrancar con el puerto que Railway pasa en $PORT
CMD ["sh", "-c", "uvicorn app:app --host 0.0.0.0 --port ${PORT:-8000}"]
