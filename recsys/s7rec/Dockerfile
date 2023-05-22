FROM python:3.7-slim-buster

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY s7rec ./s7rec
COPY data ./data

RUN mkdir -p ./log

ENV PYTHONPATH "${PYTHONPATH}:/app"