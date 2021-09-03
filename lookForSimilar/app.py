from ast import literal_eval
import json
import csv
from io import StringIO
from flask import Flask, request, jsonify, Response
import psycopg2
from numpy import transpose, array

from bm25 import BM25L
from preprocessing import preprocess

SELECT_CORPUS_FIELDS = "SELECT code, name, txt_ementa FROM corpus;"
SELECT_CORPUS = "SELECT text_preprocessed FROM corpus;"
INSERT_DATA = "INSERT INTO corpus (code, name, txt_ementa, text, text_preprocessed) VALUES ('{}','{}','{}','{}','{}');"

def load_data(con):
    with con.cursor() as cursor:
        cursor.execute(SELECT_CORPUS_FIELDS)
        try:
            (codes, names, ementas) = (array(x) for x in transpose( cursor.fetchall() ))
            
            cursor.execute(SELECT_CORPUS)
            tokenized_corpus = cursor.fetchall()
            tokenized_corpus = ["[" + entry[0][1:-1] + "]" for entry in tokenized_corpus]
        except:
            (codes, names, ementas, tokenized_corpus) = [],[],[],[]

        tokenized_corpus = [literal_eval(i) for i in tokenized_corpus]

    print("Loaded", len(codes), "documents")
    return (codes, names, ementas, tokenized_corpus)


app = Flask(__name__)

# Loading data
print("Loading corpus...")
connection = psycopg2.connect(host="0.0.0.0", database="admin",user="admin", password="admin", port=5432)
(codes, names, ementas, tokenized_corpus) = load_data(connection)

# Loading model with dataset
model = BM25L(tokenized_corpus)

print("===IT'S ALIVE!===")

@app.route('/', methods=["POST"])
def lookForSimilar():
    args = request.json

    try:
        query = args["text"]
    except:
        return ""
    try:
        k = args["num_proposicoes"]
    except:
        k = 20

    preprocessed_query = preprocess(query)
    
    indexes = list(range(len(codes)))
    slice_indexes, scores = model.get_top_n(preprocessed_query, indexes, n=k)

    selected_codes = codes[slice_indexes]
    selected_ementas = ementas[slice_indexes]
    selected_names = names[slice_indexes]
    
    resp = list()
    for i  in range(k):
        resp.append({"id": selected_names[i], "score": scores[i], 
        "ementa": selected_ementas[i], "code": selected_codes[i]})

    return jsonify(resp)


@app.route('/insert', methods=["POST"])
def insertDocs():
    content = request.data.decode("utf-8")
    io = StringIO(content)
    reader = csv.reader(io, delimiter=',')
    
    data = [row for row in reader]
    columns = data[0]
    data = data[1:]
    
    try:
        idx_text = columns.index("text")
        idx_ementa = columns.index("txt_ementa")
        idx_code = columns.index("code")
        idx_name = columns.index("name")

        data = transpose( data )

        text = data[idx_text]
        txt_ementa = data[idx_ementa]
        code = data[idx_code]
        name = data[idx_name]
        text_preprocessed = ['{' + ','.join(['"'+str(entry)+'"' for entry in preprocess(txt)]) + '}' for txt in text]

        data_insert = transpose( [code, name, txt_ementa, text, text_preprocessed] )
        with connection.cursor() as cursor:
            for d in data_insert:
                cursor.execute(INSERT_DATA.format(*d))
            connection.commit()

        # Reloading model
        print("RELOADING...")
        (codes, names, ementas, tokenized_corpus) = load_data(connection)
        model = BM25L(tokenized_corpus)
        print("RELOAD DONE")
    except:
        return Response(status=500)

    return Response(status=201)

if __name__=="__main__":
    app.run(host="0.0.0.0", debug=True, use_reloader=False)