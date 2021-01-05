FROM ubuntu:trusty
RUN sudo apt-get -y update
RUN sudo apt-get -y upgrade
RUN sudo apt-get install -y sqlite3 libsqlite3-dev

FROM python:3
ADD . /app
WORKDIR /app
Run pip install -r requirements.txt

CMD python backend.py
