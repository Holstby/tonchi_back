FROM python:3.11-slim-bullseye
WORKDIR /app
COPY ./requirements.txt .
RUN pip install -r /app/requirements.txt