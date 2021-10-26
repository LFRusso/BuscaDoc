from ast import literal_eval
import json
import requests
import csv
from io import StringIO
from flask import Flask, request, jsonify, Response
import psycopg2
from numpy import transpose, array

from bm25 import BM25L
from preprocessing import preprocess

SELECT_CORPUS_FIELDS = "SELECT code, name, txt_ementa FROM corpus;"
SELECT_ST_FIELDS = "SELECT name, text FROM solicitacoes;"
SELECT_CORPUS = "SELECT text_preprocessed FROM corpus;"
SELECT_ST = "SELECT text_preprocessed FROM solicitacoes;"
INSERT_DATA_CORPUS = "INSERT INTO corpus (code, name, txt_ementa, text, text_preprocessed) VALUES ('{}','{}','{}','{}','{}');"
SELECT_ROOT_BY_PROPOSICAO = "SELECT cod_proposicao_raiz FROM arvore_proposicoes WHERE cod_proposicao = {}"
SELECT_AVORE_BY_RAIZ = "SELECT * FROM arvore_proposicoes WHERE cod_proposicao_raiz IN {}"

session = requests.Session()
session.trust_env = False

connection = psycopg2.connect(host="ulyssesdb", database="admin",user="admin", password="admin", port=5432)
app = Flask(__name__)

def load_corpus(con):
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

    print("Loaded", len(names), "documents")
    return (codes, names, ementas, tokenized_corpus)

def load_solicitacoes(con):
    with con.cursor() as cursor:
        cursor.execute(SELECT_ST_FIELDS)
        try:
            (names, texts) = (array(x) for x in transpose( cursor.fetchall() ))
            
            cursor.execute(SELECT_ST)
            tokenized_sts = cursor.fetchall()
            tokenized_sts = ["[" + entry[0][1:-1] + "]" for entry in tokenized_sts]
        except:
            (names, texts, tokenized_sts) = [],[],[],[]

        tokenized_sts = [literal_eval(i) for i in tokenized_sts]

    print("Loaded", len(names), "Solicitações de Trabalho")
    return (names, texts, tokenized_sts)


# Loading data
print("Loading corpus...")
(codes, names, ementas, tokenized_corpus) = load_corpus(connection)
(names_sts, texto_sts, tokenized_sts) = load_solicitacoes(connection)

# Loading model with dataset
try:
    model = BM25L(tokenized_corpus)
except:
    model = None

try:
    model_st = BM25L(tokenized_sts)
except:
    model_st = None
    
print("===IT'S ALIVE!===")

def retrieveDocuments(query, n):
    indexes = list(range(len(codes)))

    slice_indexes, scores, scores_normalized = model.get_top_n(query, indexes, n=n)

    selected_codes = codes[slice_indexes]
    selected_ementas = ementas[slice_indexes]
    selected_names = names[slice_indexes]

    return selected_codes, selected_ementas, selected_names, scores, scores_normalized

def retrieveSTs(query, n):
    indexes = list(range(len(names_sts)))

    slice_indexes, scores, scores_normalized = model_st.get_top_n(query, indexes, n=n)

    selected_sts = texto_sts[slice_indexes]
    selected_names = names_sts[slice_indexes]

    return selected_names, selected_sts, scores, scores_normalized


def getRelationsFromTree(retrieved_doc):
    with connection.cursor() as cursor:
        cursor.execute(SELECT_ROOT_BY_PROPOSICAO.format(retrieved_doc))
        roots = cursor.fetchall()
        
        # Considerando que documento seja uma raiz
        if (len(roots) == 0):
            roots.append((retrieved_doc,))
        
        roots = [str(i[0]) for i in roots]
        cursor.execute(SELECT_AVORE_BY_RAIZ.format("(%s)" % ",".join(roots)))
        results = cursor.fetchall()
        
        results = list(map(lambda x: {"numero_sequencia": x[0],"nivel": x[1],"cod_proposicao": x[2],
                                     "cod_proposicao_referenciada": x[3],"cod_proposicao_raiz": x[4], 
                                     "tipo_referencia": x[5]}, results))
        return results


@app.route('/', methods=["POST"])
def lookForSimilar():
    if (model == None):
        return Response(status=500)

    args = request.json

    try:
        query = args["text"]
    except:
        return ""
    try:
        k = args["num_proposicoes"]
    except:
        k = 20
    try: 
        query_expansion = int(args["expansao"])
        if (query_expansion == 0):
            query_expansion = False
        else:
            query_expansion = True
    except:
        query_expansion = True     

    k = min(k, len(codes), len(names_sts))

    if (query_expansion):
        resp = session.post("http://expand-query:5003", json={"query": query})
        if (resp.status_code == 200):
            query = json.loads(resp.content)["query"]
    preprocessed_query = preprocess(query)

    # Recuperando das solicitações de trabalho
    selected_names_sts, selected_sts, scores_sts, scores_sts_normalized = retrieveSTs(preprocessed_query, k)
    resp_results_sts = list()
    for i  in range(k):
        resp_results_sts.append({"name": selected_names_sts[i], "texto": selected_sts[i].strip(), 
                    "score": scores_sts[i], "score_normalized": scores_sts_normalized[i], "tipo": "ST"})
    

    # Recuperando do corpus das proposições
    selected_codes, selected_ementas, selected_names, scores, scores_normalized = retrieveDocuments(preprocessed_query, k)
    resp_results = list()
    for i  in range(k):
        # Propostas relacionadas pela árvore de proposições
        relations_tree = getRelationsFromTree(selected_codes[i])
        resp_results.append({"id": selected_codes[i], "name": selected_names[i],  
                    "texto": selected_ementas[i].strip(), "score": scores[i], "score_normalized": scores_normalized[i], 
                    "tipo": "PR", "arvore": relations_tree})
    
    response = {"proposicoes": resp_results, "solicitacoes": resp_results_sts}
    return jsonify(response)


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
                cursor.execute(INSERT_DATA_CORPUS.format(*d))
            connection.commit()

        # Reloading model
        print("RELOADING...")
        (codes, names, ementas, tokenized_corpus) = load_corpus(connection)
        model = BM25L(tokenized_corpus)
        print("RELOAD DONE")
    except:
        return Response(status=500)

    return Response(status=201)

if __name__=="__main__":
    app.run(host="0.0.0.0", debug=True, use_reloader=False, port=5000)
