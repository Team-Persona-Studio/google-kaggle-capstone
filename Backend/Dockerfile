FROM python:3.10-slim

WORKDIR /app

# Install system dependencies if needed (e.g. for mysql)
# RUN apt-get update && apt-get install -y default-libmysqlclient-dev build-essential

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Default port for Render is 10000, but we use the PORT env var
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
