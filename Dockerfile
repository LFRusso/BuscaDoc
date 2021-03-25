FROM ubuntu:20.04

RUN apt-get update -y && \
    apt-get install -y python3-pip

COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip3 install -r requirements.txt
RUN python3 -m nltk.downloader punkt
RUN python3 -m nltk.downloader stopwords

COPY . /app
RUN python3 /app/createdb.py

EXPOSE 5000
CMD ["uwsgi", "--ini", "/app/wsgi.ini"]
