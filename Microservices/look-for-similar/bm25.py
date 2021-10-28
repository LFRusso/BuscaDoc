import math
import numpy as np
from multiprocessing import Pool, cpu_count
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class BM25:
    def __init__(self, corpus, tokenizer=None):
        self.corpus_size = len(corpus)
        self.avgdl = 0
        self.doc_freqs = []
        self.idf = {}
        self.doc_len = []
        self.tokenizer = tokenizer

        if tokenizer:
            corpus = self._tokenize_corpus(corpus)

        nd = self._initialize(corpus)
        self._calc_idf(nd)

    def _initialize(self, corpus):
        nd = {}  # word -> number of documents with word
        num_doc = 0
        for document in corpus:
            self.doc_len.append(len(document))
            num_doc += len(document)

            frequencies = {}
            for word in document:
                if word not in frequencies:
                    frequencies[word] = 0
                frequencies[word] += 1
            self.doc_freqs.append(frequencies)

            for word, freq in frequencies.items():
                try:
                    nd[word]+=1
                except KeyError:
                    nd[word] = 1

        self.avgdl = num_doc / self.corpus_size
        return nd

    def _tokenize_corpus(self, corpus):
        pool = Pool(cpu_count())
        tokenized_corpus = pool.map(self.tokenizer, corpus)
        return tokenized_corpus

    def _calc_idf(self, nd):
        raise NotImplementedError()

    def get_scores(self, query):
        raise NotImplementedError()

    def get_batch_scores(self, query, doc_ids):
        raise NotImplementedError()

    def get_top_n(self, query, documents, n=5):

        assert self.corpus_size == len(documents), "The documents given don't match the index corpus"

        scores = self.get_scores(query)
        try:
            scores_normalized = (scores - np.min(scores)) / (np.max(scores) - np.min(scores))
        except:
            scores_normalized = [0 for i in range(scores)]
        top_n = np.argsort(scores)[::-1][:n]
        return [documents[i] for i in top_n], np.sort(scores)[::-1][:n], np.sort(scores_normalized)[::-1][:n]


#Implementacao do BM25L - adapta parametros para corrigir a preferencia do Okapi por documentos mais curtos
class BM25L(BM25):
    def __init__(self, corpus, tokenizer=None, k1=1.5, b=0.75, epsilon=0.25):
        self.k1 = k1
        self.b = b
        self.epsilon = epsilon
        super().__init__(corpus, tokenizer)

    #Calculo do IDF (Inverse Document Frequency)
    def _calc_idf(self, nd):
        # collect idf sum to calculate an average idf for epsilon value
        idf_sum = 0
        # collect words with negative idf to set them a special epsilon value.
        # idf can be negative if word is contained in more than half of documents
        negative_idfs = []
        for word, freq in nd.items():
            idf = math.log(self.corpus_size + 1) - math.log(freq + 0.5)
            self.idf[word] = idf
            idf_sum += idf
            if idf < 0:
                negative_idfs.append(word)
        self.average_idf = idf_sum / len(self.idf)

        eps = self.epsilon * self.average_idf
        for word in negative_idfs:
            self.idf[word] = eps
    
    #Calculo do ctd
    def get_ctd(self, q_freq, b, doc_len, avg_len):
        ctd = q_freq/(1 - b + b*(doc_len)/(avg_len))
        return ctd

    #Avaliar a pontuacao de todos os documentos na base
    def get_scores(self, query):
        score = np.zeros(self.corpus_size)
        doc_len = np.array(self.doc_len)

        for q in query:
            q_freq = np.array([(doc.get(q) or 0) for doc in self.doc_freqs])
            ctd = self.get_ctd(q_freq, self.b, doc_len, self.avgdl)
            score += (self.idf.get(q) or 0) * ( (ctd + 0.5) * (self.k1 + 1) /
                                               ( (ctd + 0.5) + self.k1 ))
        return score


    def _lambda_update(self, scores, lambdas, names):
        """
        Updates bm25 scores using the lambdas values
        """

        for i, name in enumerate(names):
            name = name.strip()
            if (name in lambdas.keys()):
                scores[i] += lambdas[name]

        return scores

    def _lambda_calc(self, all_queries, retrieved_docs, query, cut, delta):
        """
        Searches for similar queries; returns dictionary
        """
        vectorizer = TfidfVectorizer()
        vectorizer.fit(all_queries+[query])
        vsm_2 = vectorizer.transform(all_queries)
        vsm_1 = vectorizer.transform([query])
        similarities = cosine_similarity(vsm_1, vsm_2).tolist()[0]

        doc_sim = [(retrieved_docs[j], similarities[j]) for j in range(len(similarities)) if similarities[j] > cut]
        
        dic = {}
        for tuple in doc_sim:
            sim = tuple[1]
            for doc in tuple[0]:
                (name, score, score_norm) = doc
                if (name in dic):
                    dic[name] += score_norm * sim
                else:
                    dic[name] = score_norm * sim  # calculando a soma do produto sim*score

        for key in dic:
            dic[key] = np.log(dic[key] + 1) * delta
        return dic

    def get_top_n(self, query, documents, n=5, 
                    improve_similarity=False, raw_query=None, past_queries=[], 
                    retrieved_docs=[], names=[], cut=0.6, delta=0.7):

        assert self.corpus_size == len(documents), "The documents given don't match the index corpus"

        scores = self.get_scores(query)
        try:
            scores_normalized = (scores - np.min(scores)) / (np.max(scores) - np.min(scores))
        except:
            scores_normalized = [0 for i in range(scores)]

        if (improve_similarity):
            try:
                lambdas = self._lambda_calc(all_queries=past_queries, retrieved_docs=retrieved_docs, 
                                        query=raw_query, cut=cut, delta=delta)
                scores = self._lambda_update(scores=scores_normalized, lambdas=lambdas, names=names)
            except:
                print("Error calculating lambdas. If there are no past feedbacks yet ignore this message.", flush=True)

        top_n = np.argsort(scores)[::-1][:n]
        return [documents[i] for i in top_n], np.sort(scores)[::-1][:n], np.sort(scores_normalized)[::-1][:n]

    def get_batch_scores(self, query, doc_ids):
        assert all(di < len(self.doc_freqs) for di in doc_ids)
        score = np.zeros(len(doc_ids))
        doc_len = np.array(self.doc_len)[doc_ids]
        for q in query:
            q_freq = np.array([(self.doc_freqs[di].get(q) or 0) for di in doc_ids])
            score += (self.idf.get(q) or 0) * (q_freq * (self.k1 + 1) /
                                               (q_freq + self.k1 * (1 - self.b + self.b * doc_len / self.avgdl)))
        return score.tolist()