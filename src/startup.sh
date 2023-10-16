#!/bin/bash
set -e

python3 database.py

if [[ -z "$PROJECT_HOST" || -z "$PROJECT_PORT" ]]; then
  echo "HOST or PORT variables are not set!"
  exit 1
fi

uvicorn main:app --host $PROJECT_HOST --port $PROJECT_PORT
