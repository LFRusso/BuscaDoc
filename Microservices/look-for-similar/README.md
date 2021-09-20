# lookForSimilar
lookForSimilar information retrieval microservice API


## Running the API

The file `docsdb.json` containing the corpus (raw and tokenized) is required.

On the root folder, execute the command:

```
$ docker-compose up
```

Sample request with *cURL*:

```
$ curl -X POST -H "Content-Type: application/json" --data '{"text": "Exemplo de texto de entrada", "num_proposicoes": 10}' http://localhost:5000/
```

Sample response:

```json
[{"id":"PEC 492/2010","score":11.277917457877507},{"id":"PL 3893/2015","score":9.667946934868343},{"id":"PL 1887/2011","score":8.817249399736536},{"id":"PEC 323/2004","score":8.630745108031093},{"id":"PL 4339/2019","score":8.450954494240786},{"id":"PL 2443/2011","score":8.402197822873275},{"id":"PL 1474/2019","score":8.331690504368183},{"id":"PL 5124/2019","score":8.300593893790658},{"id":"PEC 150/2015","score":8.299482189773013},{"id":"PL 4032/2004","score":8.26707488229632}]
```
