FROM python:3.11-slim

WORKDIR /app

COPY . .
RUN poetry install

# Create a directory for persistent data if used with a volume
RUN mkdir -p /data
VOLUME /data

EXPOSE 3636

CMD ["python", "app.py"]
