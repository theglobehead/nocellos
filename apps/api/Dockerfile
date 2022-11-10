FROM python:3.9.8-slim

WORKDIR /src/app

RUN apt-get update \
    && apt-get -y install libpq-dev gcc \
    && pip install psycopg2

RUN pip install --upgrade pip

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY . .

EXPOSE $PORT

CMD uvicorn main:app --host 0.0.0.0 --port $PORT
