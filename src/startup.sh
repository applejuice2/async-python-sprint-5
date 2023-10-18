#!/bin/bash
set -e


if [[ -z "$PROJECT_HOST" || -z "$PROJECT_PORT" ]]; then
  echo "HOST or PORT variables are not set!"
  exit 1
fi

alembic upgrade head
python3 -m gunicorn --name file_service -k uvicorn.workers.UvicornWorker -w 1 -b $PROJECT_HOST:$PROJECT_PORT  main:app
