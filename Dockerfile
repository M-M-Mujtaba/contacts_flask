FROM python:3

ADD . /app
WORKDIR /app
Run pip install -r requirements.txt

CMD python backend.py
