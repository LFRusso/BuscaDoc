FROM python:3.8-slim

COPY . /app
WORKDIR /app


RUN apt-get update \
    && apt-get -y install libpq-dev gcc 
    
RUN pip install --upgrade pip
RUN pip3 install -r requirements.txt

CMD ["source", ".env"]
CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]
EXPOSE 5001
