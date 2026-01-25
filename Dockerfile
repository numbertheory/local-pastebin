FROM python:3.11-slim

WORKDIR /app
RUN apt update && \
    apt install -y pipx && \
    pipx install poetry && \
    ln -s /root/.local/bin/poetry /usr/local/bin/poetry
COPY . .
RUN poetry install

# Create a directory for persistent data if used with a volume
RUN mkdir -p /data
VOLUME /data

EXPOSE 3636

CMD ["poetry", "run", "python", "app.py"]
