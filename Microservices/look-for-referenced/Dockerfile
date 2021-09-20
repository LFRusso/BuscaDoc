FROM python:3.8.3-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN apt-get clean && apt-get update \
    && apt-get -y install libpq-dev gcc \
    && pip install psycopg2
RUN pip install --upgrade pip
RUN pip3 install -r requirements.txt

COPY . .

CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0", "--port=5002"]
EXPOSE 5002
