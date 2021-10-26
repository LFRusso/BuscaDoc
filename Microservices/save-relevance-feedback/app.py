from flask import Flask, request, Response, jsonify
from datetime import datetime
import psycopg2
import json

VALID_CLASSES = ["r", "i", "vr", "d", "pr"] # relevante; irrelevante; muito relevante; duvida; pouco relevante
INSERT_ENTRY = "INSERT INTO feedback(query, user_feedback, extra_results, date_created) VALUES ('{}', '{}', '{}', '{}');"

app = Flask(__name__)

connection = psycopg2.connect(host="ulyssesdb", database="admin",user="admin", password="admin", port=5432)

def isResultValid(result):
    try:
        keys = list(result.keys())
        if (len(keys) != 5):
            return False

        score = float(result["score"])
        score_normalized = float(result["score_normalized"])
        classification = result["class"]
        code = result["id"]
        tipo = result["tipo"]

        if (classification not in VALID_CLASSES):
            return False
    except:
        return False
    return True


def isValid(entry):
    try:
        keys = list(entry.keys())
        if (len(keys) != 3):
            return False
        
        query = entry["query"]
        results = entry["results"]
        extra_results = entry["extra_results"]
        if (type(results) != list):
            results = json.loads(results)

        for result in results:
            if (not isResultValid(result)):
                return False
    except: 
        return False
    return True

@app.route('/', methods=["POST"])
def registerScores():
    data = request.json

    if(isValid(data)):
        try:
            query = data["query"]
            results = data["results"]
            extra_results = data["extra_results"]
            date = datetime.utcnow()
            print(results, flush=True)
            with connection.cursor() as cursor:
                cursor.execute( INSERT_ENTRY.format(query, json.dumps(results), json.dumps(extra_results), date) )
                connection.commit()
        except:
            return Response(status=500) 

    return Response(status=201)

if __name__=="__main__":
    app.run(host="0.0.0.0", port=5001)