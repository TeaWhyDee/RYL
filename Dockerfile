# syntax=docker/dockerfile:1

FROM python:3.13-slim-bookworm

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY ./app/ .
COPY ./sample_data/ ./app/sample_data/

EXPOSE 5000

CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]
