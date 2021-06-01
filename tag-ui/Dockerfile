FROM python:3.8-slim-buster

WORKDIR /app

COPY requirements.txt  ./ 
RUN pip3 install --requirement requirements.txt

COPY backend.py test_backend.py ./
