import json
import re
from flask import Flask, request, jsonify, Response
from CRF import CRF

app = Flask(__name__)

ner_model = CRF()
try:
    ner_model.set_model_file("model.crf.tagger.app")
except:
    ner_model = None
    
print("===IT'S ALIVE!===")

@app.route('/', methods=["POST"])
def lookForReferenced():
    if (ner_model == None):
        return Response(status=500)

    args = request.json
    try:
        query = args["text"]
    except:
        query = ''
    
    tokenized_query = re.findall(r"[\w']+|[.,!?;]", query)
    try:
        named_entities = ner_model.return_docs(tokenized_query)
    except:
        named_entities = []
    response = {"entities": named_entities}
    return jsonify(response)


if __name__=="__main__":
    app.run(host="0.0.0.0", debug=True, use_reloader=False, port=5002)