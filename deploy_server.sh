#! /usr/bin/env bash

# Exit on any error
set -e

# Check for uncommitted changes (including staged, unstaged, and untracked files)
if [[ -n $(git status --porcelain) ]]; then
    echo "Uncommitted changes detected. Please commit, stash, or discard them before pulling."
    exit 1
fi

# No changes – safe to pull
git pull

# Remove running instance
docker compose down

# Bring up new instance
docker compose up --force-recreate --build

