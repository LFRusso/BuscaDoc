import operator
import random
import functools

def process_conll_file(file_path:str)->list:
    """
    input: file_path - Caminho para arquivo .conll
    output: lista de listas, cada elemento da lista interna eh uma tupla do tipo : (palavra, rotulo)
    """
    with open(file_path, "r") as f:
        data = f.read()
    data = data.split("\n\n")
    data = list(map(lambda x:x.split("\n"), data))
    data.pop()
    data = list(map(lambda x:[operator.itemgetter(*[1, -3])(y.split("\t")) for y in x], data))
    return data


def to_list(data:list)->list:
    """
    input: lista de frases rotuladas
    output: lista de palavras rotuladas
    """
    return functools.reduce(operator.iconcat, data, [])


def split_words_n_tags(data:list)->tuple:
    """
    input: frase rotula
    output: duas listas, a primeira de palavras e a segunda de rotulos
    """
    words, tags = map(list, zip(*data))
    return words, tags


def filter_tag(data:list, tag:str)->list:
    """
    input: lista de frases, rótulo
    output: indices das frases que contem pelo menos uma palavra com o rotulo escolhido
    """
    indexes = []
    for i, d in enumerate(data):
        _, tags = split_words_n_tags(d)
        if tag in tags:
            indexes.append(i)
    return indexes


def data_split(data:list, train_size:float, val_size:float)->tuple:
    """
    input: lista de frases, tamanho do conjunto de treino e de validação, o de teste pode ser facilmente inferido.
    output: conjunto de treinamento, validação e teste
    """
    D = data
    random.shuffle(D)
    n = len(D)
    index1 = int(train_size*n)
    index2 = index1 + int(val_size*n)
    train = D[:index1]
    val = D[index1:index2]
    test = D[index2:]
    return (train, val, test)


def retrive_sents(data:list)->list:
    """
    input: frases rotuladas
    output: frases sem o rótulo
    """
    return list(map(lambda x:[w for w,t in x], data))


def error_list(model, unlabeled_test:list, test:list)->list:
    """
    input: model - tagger
           unlabeled_test - frases nao rotuladas do conjunto de teste
           test - frases rotuladas do conjunto de teste
    output: lista de frases em que o modelo cometeu pelo menos um erro
    """
    elist = []
    for x, y in zip(unlabeled_test, test):
        z = model.tag(x)
        if z is None:
            z = 'O'
        if z!=y:
            elist.append((z, y))
    return elist

            
def errors_to_txt(error_list:list, file_name)->None:
    """
    input: lista com as frases em que o modelo cometeu pelo menos um erro
    output: None, salva as frases no arquivo file_name
    """
    to_txt = ""
    for pair in error_list:
        words, real_tags = split_words_n_tags(pair[1])
        _, pred_tags = split_words_n_tags(pair[0])
        for word, real_tag, pred_tag in zip(words, real_tags, pred_tags):
            to_txt += word + "__" + real_tag + "__" + pred_tag + "\n"
        to_txt += "\n"
    with open(file_name, "w") as f:
        f.write(to_txt)

