FROM python:3.9-slim
RUN apt-get update -y && apt-get install -y --no-install-recommends libpq-dev build-essential
WORKDIR /app
COPY requirements.txt .
RUN pip install --upgrade pip && pip3 install -r requirements.txt --no-cache-dir
COPY . .
RUN chmod +x ./startup.sh
CMD ["./startup.sh"]
