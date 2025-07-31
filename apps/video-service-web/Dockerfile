# Use an official Python 3.11 image as the base
FROM python:3.11.2-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    POETRY_VERSION=1.7.0 \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1

# Set the working directory
WORKDIR /app

# Install system dependencies, ffmpeg, and Poetry
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    ninja-build \
    pkg-config \
    ffmpeg \
    && curl -sSL https://install.python-poetry.org | python3 - \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Add Poetry to PATH
ENV PATH="/root/.local/bin:$PATH"

# Copy project files
COPY video-service-web/pyproject.toml video-service-web/poetry.lock ./
COPY shared ./shared

# Install dependencies
RUN poetry config virtualenvs.create false && \
    poetry install --no-root --only main

# Copy the rest of the application
COPY video-service-web/src ./src

# Create HLS directory for video segments and manifest
RUN mkdir -p /app/hls

# Add to python path
ENV PYTHONPATH="/app/src"
ENV HLS_DIR="/app/hls"
ENV UDP_PORT="4001"
ENV UDP_URL="0.0.0.0"

# Expose the application port
EXPOSE 4000

# Command to run the application
CMD ["sh", "-c", "uvicorn video_service_web.main:app --host 0.0.0.0 --port 4000 --reload"]
