#!/bin/bash
set -e

python3 database.py

if [[ -z "$PROJECT_HOST" || -z "$PROJECT_PORT" ]]; then
  echo "HOST or PORT variables are not set!"
  exit 1
fi

python3 -m gunicorn --name file_service -k uvicorn.workers.UvicornWorker -w 1 -b $PROJECT_HOST:$PROJECT_PORT  main:app
