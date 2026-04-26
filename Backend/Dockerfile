# Use Python 3.12 slim image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies including Tesseract OCR
RUN apt-get update && \
    apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-eng \
    libtesseract-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p uploads database/vectorstore database/embeddings

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV TESSERACT_CMD=/usr/bin/tesseract
ENV FLASK_ENV=production

# Expose port (Render will set PORT env var)
EXPOSE 5000

# Run with Gunicorn (Render sets PORT env var automatically)
CMD gunicorn --bind 0.0.0.0:$PORT --workers 1 --timeout 120 app:app