# Simple Python image for the SWAPI loader
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY swapi_to_mysql.py ./

# default command is provided by docker-compose