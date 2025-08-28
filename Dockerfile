FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
EXPOSE 8002

# Create a startup script
RUN echo '#!/bin/bash\npython3 quilt_api.py &\npython3 quilt_github_app.py &\nwait' > start.sh && chmod +x start.sh

CMD ["./start.sh"]
