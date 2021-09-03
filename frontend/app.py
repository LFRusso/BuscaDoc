from flask import Flask, render_template, url_for, request, redirect, flash
from werkzeug.utils import secure_filename
import json
import urllib.parse as parse
import requests


UPLOAD_FOLDER = '/tmp'
ALLOWED_EXTENSIONS = {'csv', 'pdf'}

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_filetype(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Upload new file to be included in the dataset
@app.route('/docs', methods=["GET", "POST"])
def showDocs():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)

        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        if file and allowed_filetype(file.filename):
            filename = secure_filename(file.filename)
            content = file.read()
            resp = requests.post("http://localhost:5000/insert", data=content)

    return render_template("docs.html", docs=None, names=None, len=0)

@app.route('/', methods=["GET"])
def index():
    return render_template("index.html", docs=None, names=None, len=0)

@app.route('/search', methods=["GET", "POST"])
def search():
    if (request.method == "POST"):
        query = parse.quote_plus(request.form['query'], safe='')
        return redirect("/search?q="+query+"&p=1")
    
    if (request.method == "GET"):
        query = request.args.get('q')
        page = request.args.get('p')
        data = {'text': query, 'num_proposicoes': 10}
        
        resp = requests.post("http://localhost:5000/", json=data)
        if (resp.status_code == 500):
            return render_template("index.html", docs=None, names=None, len=0)
    
        results = json.loads(resp.content)
        top_docs = [results[i]["ementa"] for i in range(10)]
        labels = [results[i]["id"] for i in range(10)]
        ids = [results[i]["code"] for i in range(10)]
        scores = [results[i]["score"] for i in range(10)]
        
        return render_template("index.html", docs=top_docs, names=labels, query=query, 
                                ids=ids, len=len(labels), scores=scores)

@app.route("/submit/<query>", methods=["POST"])
def submit(query):
    form_results = dict(request.form)
    form_results = [result.split("&") for result in  list(form_results.keys())]

    query = parse.unquote_plus(query)
    
    docs = [r[0] for r in form_results]
    scores = [r[1] for r in form_results]
    classes = list(dict(request.form).values())

    results = [{"id": docs[i], "class": classes[i], "score": scores[i]} for i in range(len(form_results))]
    
    data = {"query": query, "results": results}

    requests.post("http://localhost:5001", json=data)
    return redirect(url_for("index"))

if __name__=="__main__":
    app.run(host="0.0.0.0", debug=True, port=3000)
