FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create a directory for persistent data if used with a volume
RUN mkdir -p /data
VOLUME /data

EXPOSE 3636

CMD ["python", "app.py"]
