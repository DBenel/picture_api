FROM python:3.11

ENV MYSQL_HOST=$MYSQL_HOST

RUN apt update

COPY requirements.txt /tmp/

RUN pip3 install -r /tmp/requirements.txt

WORKDIR /opt/
COPY ../../application application/
