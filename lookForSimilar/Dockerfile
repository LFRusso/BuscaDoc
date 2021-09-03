FROM ubuntu:20.04

RUN apt-get update -y && apt-get -y upgrade
RUN apt-get install -y python3-pip
RUN DEBIAN_FRONTEND="noninteractive" apt-get install -y libapache2-mod-wsgi

COPY . /app
WORKDIR /app

RUN pip3 install -r requirements.txt
RUN python3 -m nltk.downloader punkt
RUN python3 -m nltk.downloader stopwords

CMD uwsgi --ini wsgi.ini
EXPOSE 5000
