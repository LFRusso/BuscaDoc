import nltk
from nltk.tokenize import RegexpTokenizer
from nltk.util import ngrams
from string import punctuation
from unicodedata import normalize

from savoy import Savoy

def _remove_accents(txt):
    return normalize('NFKD', txt).encode('ASCII', 'ignore').decode('ASCII')

def preprocess(txt, n=2):
    txt = _remove_accents(txt)
    stopwords = nltk.corpus.stopwords.words("portuguese")
    stopwords.extend(list(punctuation))

    stemmer = Savoy()
    tokenizer = RegexpTokenizer('\w+')
    terms = tokenizer.tokenize(txt.lower())
    terms = [stemmer.stem(word) for word in terms if word not in stopwords]

    ngram = [" ".join(i) for i in list(ngrams(terms, n))]

    composition = terms + ngram
    return composition