# syntax=docker/dockerfile:1
FROM python:3.9

ENV PYTHONUNBUFFERED=1

RUN /usr/local/bin/python -m pip install --upgrade pip

# need postgres client to wait until db is available when container boots
RUN apt update && apt install -y postgresql-client

WORKDIR /code
COPY requirements.txt /code/
RUN pip install -r requirements.txt
COPY . /code/

ENTRYPOINT ["/code/entrypoint.sh"]