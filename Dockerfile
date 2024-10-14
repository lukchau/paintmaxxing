FROM python:3.11.2-slim

ENV APP_HOME myapp

RUN mkdir -p "$APP_HOME"
WORKDIR "$APP_HOME"

COPY src/*.py ./

RUN python app.py

EXPOSE 1232



