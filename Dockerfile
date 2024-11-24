FROM python:3.11-slim

WORKDIR /usr/src/app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip &&  \
    pip install --no-cache-dir -r requirements.txt

COPY . .

ENTRYPOINT ["/bin/sh", "-c", "cd /usr/src/app && python -m app"]
