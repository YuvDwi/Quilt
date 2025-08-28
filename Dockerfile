FROM python:3.11-slim

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy Python backend files
COPY *.py ./

# Expose port
EXPOSE 8005

# Start the API only
CMD ["python3", "quilt_react_api.py"]
