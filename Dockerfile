# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY pyproject.toml .
COPY uv.lock* .

# Install pip and dependencies
RUN pip install --no-cache-dir --upgrade pip

# Install dependencies from pyproject.toml
RUN pip install --no-cache-dir \
    "fastapi>=0.128.0" \
    "openai-agents>=0.6.7" \
    "uvicorn>=0.40.0" \
    "httpx>=0.28.1" \
    "python-dotenv>=1.0.1"

# Copy application code
COPY . .

# Expose port
EXPOSE 7860

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
