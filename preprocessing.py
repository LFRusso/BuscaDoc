from nltk.tokenize import word_tokenize
from string import punctuation
import nltk
from unicodedata import normalize

# Remove os acentos de uma string
def _remove_acentos(txt):
    return normalize('NFKD', txt).encode('ASCII', 'ignore').decode('ASCII')

def preprocess(txt):
    txt = _remove_acentos(txt)
    stopwords = nltk.corpus.stopwords.words("portuguese")
    stopwords.extend(list(punctuation))
    
    terms = word_tokenize(txt.lower())
    terms = [word for word in terms if word not in stopwords]
    
    return terms

def get_name(df, doc, in_field="content", out_field = "name"):
    return str(df[df[in_field]==doc][out_field].to_numpy()[0]).strip()
