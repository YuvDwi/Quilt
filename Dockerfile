# Dockerfile for Quilt API (Render deployment)
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY cloud_requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY cloud_updated_quilt_api.py updated_quilt_api.py
COPY .env* ./

# Expose port
EXPOSE $PORT

# Start command (Render will override this)
CMD ["python", "-m", "uvicorn", "updated_quilt_api:app", "--host", "0.0.0.0", "--port", "$PORT"]
