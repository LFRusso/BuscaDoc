from flask import Flask, render_template, url_for, request, redirect
from datetime import datetime
from uuid import uuid4
import json

app = Flask(__name__)
app.run()

# Loading data
import pandas as pd

print("Loading corpus...")
df = pd.read_json("docsdb.json", encoding="utf-8")
df = df.dropna()
df  = df.reset_index(drop=True)

corpus = df.ementa.to_numpy()
tokenized_corpus = df.tokenized_content

# Building BM25 pre-processing and model building
from bm25 import BM25Okapi
from preprocessing import *

print("Building VSM...")
bm25 = BM25Okapi(tokenized_corpus)

print("===IT'S ALIVE!===")

# Routes

@app.route('/', methods=["GET"])
def index():
    return render_template("index.html", docs=None, names=None, len=0)

@app.route('/search', methods=["POST"])
def search():
    query = request.form['query']
    return redirect(url_for("search_doc", query=query))

@app.route('/search/<query>', methods=["GET", "POST"])
def search_doc(query):
    with open("log.dat", "a+") as fp:
        fp.write(f"{query}\n")
    tokenized_query = preprocess(query)
    top_docs = bm25.get_top_n(tokenized_query, corpus, n=10)
    labels = [get_name(df,d, in_field="ementa") for d in top_docs]
    
    ids = [get_name(df,d, in_field="ementa", out_field="id") for d in top_docs]
    base_url = "https://www.camara.leg.br/proposicoesWeb/fichadetramitacao?idProposicao="

    return render_template("index.html", docs=top_docs, names=labels, query=query, ids=ids, len=len(labels))

@app.route("/submit/<query>", methods=["POST"])
def submit(query):
    data = {
                "_id": str(uuid4()), 
                "query": query, 
                "matches": dict(request.form), 
                "datetime": datetime.today().strftime("%d/%m/%Y %H:%M:%S")
            }
    print()
    print(data)
    print()

    with open("output.json", "a+") as fp:
        fp.write(json.dumps(data))

    return redirect(url_for("index"))

if __name__=="__main__":
    app.run()
