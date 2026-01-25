# Local Pastebin

A lightweight, local network Pastebin alternative using Flask and SQLite, designed to run in Docker.

## Features
- **Web Interface:** Create and view pastes with a simple UI.
- **API:** Create and retrieve pastes via JSON or raw text.
- **Persistence:** SQLite database storage.

## Usage

### 1. Build the Docker Image
```bash
docker build -t local-pastebin .
```

### 2. Run the Container
Run the container, mapping port 3636 and mounting a volume for persistent storage.

```bash
docker run -d \
  -p 3636:3636 \
  -v $(pwd)/data:/data \
  --name my-pastebin \
  local-pastebin
```
*Note: The application stores the database at `/data/pastes.db` if the `/data` directory exists.*

### 3. Access
- **Web UI:** Open [http://localhost:3636](http://localhost:3636)
- **API Example:**
  ```bash
  curl -X POST -d "My paste content" http://localhost:3636/api/paste
  ```

## Development
To run locally without Docker:
1. Install dependencies: `pip install -r requirements.txt`
2. Run app: `python app.py`

