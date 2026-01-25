# Local Pastebin

A lightweight, local network Pastebin alternative using Flask and SQLite, designed to run in Docker. This is still a work in progress and not meant for deployment on the open internet. Ideally works for a local area network.

## Features
- **Web Interface:** Create and view pastes with a simple UI.
- **API:** Create and retrieve pastes via JSON or raw text.
- **Persistence:** SQLite database storage.

## Usage


### 1. Run the compose file
Run the container, mapping port 3636 and mounting a volume for persistent storage.

```bash
docker compose up -d
```
*Note: The application stores the database in a docker volume called local-pastebin_pastebin-data*

To clear the database:

```bash
docker volume rm local-pastebin_pastebin-data
```

### 3. Access
- **Web UI:** Open [http://localhost:3636](http://localhost:3636)
- **API Example:**
  ```bash
  curl -X POST -d "My paste content" http://localhost:3636/api/paste
  ```

## Development
To run locally without Docker, use [Python Poetry](https://python-poetry.org/docs/#installation):

1. Install dependencies: `poetry install`
2. Run app: `poetry run python app.py`

