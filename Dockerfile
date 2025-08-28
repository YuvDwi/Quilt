FROM python:3.11-slim

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy Python backend files
COPY *.py ./

# Copy static directory
COPY static/ ./static/

# Expose port (Railway uses PORT env var)
EXPOSE $PORT
EXPOSE 8005

# Start the simple API for testing
CMD ["python3", "simple_api.py"]
