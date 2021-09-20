import pycrfsuite
import string
import time
import random
from sklearn import metrics
from utils import *

class CRF:
    def __init__(self, feature_func:callable=None, training_opt:dict={})->None:
        self._feature_func = feature_func if feature_func is not None else self._get_features
        self._training_opt = training_opt
        self._tagger = pycrfsuite.Tagger()

    def set_model_file(self, model_file:str)->None:
        self._tagger.open(model_file)
        
    def _get_features(self, tokens:list, idx:int)->list:
        PUNC = string.punctuation+"º°"
        token = tokens[idx]

        feature_list = []

        # Verifica se existe um algarismo na palavra atual
        if not token.isalpha():
            feature_list.append("HAS_NUMBER")

        # Verifica se a palavra atual começa com letra maiúscula
        if token[0].isupper():
            feature_list.append("IS_CAPITALIZED")

        # Vefica se existe pontuação na palavra atual
        if any(list(map(lambda x:x in PUNC, token))):
            feature_list.append("HAS_PUNCTUATION")

        n = len(token)
        # Extrai prefixos e sufixos da palavra atual
        if n>1:
            feature_list.append("PREF_"+token[:2])
            feature_list.append("SUF_"+token[-1:])
        if n>2:
            feature_list.append("PREF_"+token[:3])
            feature_list.append("SUF_"+token[-2:]) 
        if n>3:
            feature_list.append("PREF_"+token[:4])
            feature_list.append("SUF_"+token[-3:])

        if idx==0:
            return feature_list

        # Mesmo processo para a palavra anterior
        previous_token = tokens[idx-1]

        if not previous_token.isalpha():
            feature_list.append("PHAS_NUMBER")

        if previous_token[0].isupper():
            feature_list.append("PIS_CAPITALIZED")

        if any(list(map(lambda x:x in PUNC, previous_token))):
            feature_list.append("PHAS_PUNCTUATION")

        n = len(previous_token)
        if n>1:
            feature_list.append("PPREF_"+previous_token[:2])
            feature_list.append("PSUF_"+previous_token[-1:])
        if n>2:
            feature_list.append("PPREF_"+previous_token[:3])
            feature_list.append("PSUF_"+previous_token[-2:])   
        if n>3:
            feature_list.append("PPREF_"+previous_token[:4])
            feature_list.append("PSUF_"+previous_token[-3:])

        if idx==len(tokens)-1:
            return feature_list

        # Mesmo processo para a palavra seguinte
        next_token = tokens[idx+1]

        if not next_token.isalpha():
            feature_list.append("NHAS_NUMBER")

        if next_token[0].isupper():
            feature_list.append("NIS_CAPITALIZED")

        if any(list(map(lambda x:x in PUNC, next_token))):
            feature_list.append("NHAS_PUNCTUATION")

        n = len(next_token)
        if n>1:
            feature_list.append("NPREF_"+next_token[:2])
            feature_list.append("NSUF_"+next_token[-1:])
        if n>2:
            feature_list.append("NPREF_"+next_token[:3])
            feature_list.append("NSUF_"+next_token[-2:])
        if n>3:
            feature_list.append("NPREF_"+next_token[:4])
            feature_list.append("NSUF_"+next_token[-3:])

        return feature_list

    def train(self, train_data:list, model_file:str, verbose:bool=True)->None:
        trainer = trainer = pycrfsuite.Trainer(verbose=verbose)
        trainer.set_params(self._training_opt)

        for sent in train_data:
            tokens, labels = zip(*sent)
            features = [self._feature_func(tokens, i) for i in range(len(tokens))]
            trainer.append(features, labels)

        trainer.train(model_file)
        self.set_model_file(model_file)

    def tag_sents(self, sents:list)->list:
        result = []
        for tokens in sents:
            features = [self._feature_func(tokens, i) for i in range(len(tokens))]
            labels = self._tagger.tag(features)

            if len(labels) != len(tokens):
                raise Exception(" Predicted Length Not Matched, Expect Errors !")

            tagged_sent = list(zip(tokens, labels))
            result.append(tagged_sent)

        return result

    def tag(self, tokens):
        return self.tag_sents([tokens])[0]
    
    def return_docs(self, tokens:list)->list:
        res = self.tag(tokens)
        x, y = zip(*res)
        n = len(y)
        marginal = [self._tagger.marginal(y[i], i) for i in range(n)]
        
        labels = list(set(y))
        if len(labels)==1:
            if y[0]=="O":
                return []
            else:
                return [(" ".join(x), sum(marginal)/len(marginal))]

        docs = []
        confidence = []
        sent = " "
        prob = 0
        counter = 0
        for i in range(n):
            if y[i]=="DOCUMENTO":
                sent += x[i] + " "
                prob += marginal[i]
                counter += 1
            else:
                if sent !=" ":
                    docs.append(sent)
                    confidence.append(round(prob/counter, 2))
                    counter = 0
                sent = " "
                prob = 0
        if sent!=" ":
            docs.append(sent)
            confidence.append(prob/ counter)
        return list(zip(docs, confidence))
