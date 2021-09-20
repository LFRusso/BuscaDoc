import json
import re
import datetime
from flask import Flask, request, jsonify, Response
import urllib.parse as parse
import requests
import psycopg2

FIND_BY_NAME_CORPUS = 'SELECT txt_ementa FROM corpus WHERE name IN %s'
FIND_BY_NAME_ST = 'SELECT text FROM solicitacoes WHERE name IN %s'

PL_REGEX = "[0-9]+"
LABELS = ["ADD","ANEXO","APJ","ATC","AV","CN","EMS","INC","MPV","MSC","PL","PEC","PLP",
            "PLV","PDC","PRC","PRN","PFC","REP","REQ","RIC","RCP","SIT","ST"]

connection = psycopg2.connect(host="ulyssesdb", database="admin",user="admin", password="admin", port=5432)
app = Flask(__name__)

print("===IT'S ALIVE!===")

# Retrieves the text from the corpus and the STs based on the referenced name
def searchByName(name_parts):

    query_expansion = ""
    if (len(name_parts)==2):
        code = name_parts[0]
        code_year = name_parts[1]
        if (len(code_year) == 2):
            if (int(code_year) <= (datetime.now().year % 100)):  # Cheking for 2-digit year (ex 2019 -> 19, 1998 -> 98)
                code_year = "20"+code_year
            else:
                code_year = "19"+code_year
        code = code + "/" + code_year

        labeled_codes = tuple(map(lambda x: x + " " + code, LABELS))

        with connection.cursor() as cursor:
            cursor.execute(FIND_BY_NAME_CORPUS, (labeled_codes,))
            results = [text[0] for text in cursor.fetchall()]
            query_expansion += ' '.join(results)

            cursor.execute(FIND_BY_NAME_ST, (labeled_codes,))
            results = [text[0] for text in cursor.fetchall()]
            query_expansion += ' '.join(results)

    return query_expansion
            

@app.route('/', methods=["POST"])
def queryExpansion():

    args = request.json
    try:
        query = args["query"]
    except:
        return Response(status=500)

    resp = requests.post("http://look-for-referenced:5002", json={"text": query})
    data = json.loads(resp.content)
    for entity in data["entities"]:
        string, score = entity[0], entity[1]
        name_parts = re.findall(PL_REGEX, string)
        expansion = searchByName(name_parts)
        
        query += " " + expansion
        query = query.strip()

    resp = {'query': query, 'entities': data["entities"]}
    return jsonify(resp)


if __name__=="__main__":
    app.run(host="0.0.0.0", debug=True, use_reloader=False, port=5003)