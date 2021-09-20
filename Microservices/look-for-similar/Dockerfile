FROM python:3.8.3-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN apt-get clean
RUN apt-get update --allow-unauthenticated --allow-insecure-repositories
RUN apt-get -y install libpq-dev gcc
RUN pip install --upgrade pip
RUN pip3 install -r requirements.txt
RUN python -m nltk.downloader punkt
RUN python -m nltk.downloader stopwords

COPY . .

CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0", "--port=5000"]
EXPOSE 5000
