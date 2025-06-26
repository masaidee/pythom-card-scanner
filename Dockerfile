# Use official Python image as base
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        tesseract-ocr \
        libglib2.0-0 \
        libsm6 \
        libxrender1 \
        libxext6 \
        libgl1 \
        build-essential \
        python3-dev \
        python3-pip \
        && rm -rf /var/lib/apt/lists/*

# (Optional) Install tesseract language data for Thai
RUN apt-get update && apt-get install -y tesseract-ocr-tha && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt ./

# Install Python dependencies
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Expose port
EXPOSE 8000

# Run the app
CMD ["python", "app.py"]
