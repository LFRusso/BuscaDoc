# BuscaDoc

Uma plataforma simples para a obtenção dados para o treinamento de modelos de recuperação de informação


| Arquivo          | Link                                                                                           | Descrição                                    |
|------------------|------------------------------------------------------------------------------------------------|----------------------------------------------|
| corpus_small.csv | [download](https://drive.google.com/file/d/1TwrKqLzcUe_mZX18zQvxtDyiysIryDDQ/view?usp=sharing) | Contém 5000 documentos do corpus original.   |
| corpus_full.csv  | [download](https://drive.google.com/file/d/1CcnIwmM_ydDxURkrGqVM2onEKOCNcTtq/view?usp=sharing) | Corpus original, contendo 114646 documentos. |
| new_docs.csv     | [download](https://drive.google.com/file/d/1AiIjlbTahhidRPlp7nB4dhebpgHFM2SD/view?usp=sharing)   | Arquivos para testar inserção na página.     |


## 1. Execução sem Docker

Na raíz do projeto, execute

```bash
pip3 install -r requirements.txt
```

para realizar a instalação dos requisitos.

### 1.1 Inicializando Banco

No diretório `./db` execute o comando 

```bash
docker-compose up -d
```

Para criar um container com o banco postgres.

Dentro do mesmo diretório, execute

```bash
bash load_schema.sh
```

ou, alternativamente, conecte-se ao banco com

```bash
bash connect.sh
```

e execute os *create tables* para as tabelas `corpus` e `feedback`.

Tendo uma arquivo *.csv* no seguinte formato:

![](assets/csv_db_insert.png)

como os arquivos `corpus_full.csv` e `corpus_small.csv`, estes podem ser inseridos diretamente no banco executando

```bash
bash connect.csv 
```

e, no postgres,

```postgres
\COPY corpus FROM 'nomedoarquivo' CSV HEADER DELIMITER ',';
```

Para parar a execução do banco, execute na mesma pasta

```bash
docker-compose down
```

### 1.2 lookForSimilar

Com o banco sendo executado e os requisitos instalados, podemos executar o `lookForSimilar`. No diretório de mesmo nome, executamos:

```bash
python3 app.py
```

para executarmos diretamente com o `Python 3` ou então

```bash
python3 wsgi.py
```

para executar usando o `WSGI`.

### 1.3 scoringApi

No diretório `scoringApi`, execute

```bash
python3 app.py
```

para executar diretamente ou então

```bash
bash autorun
```


### 1.4 frontend

No diretório `frontend`, execute

```bash
python3 app.py
```

para executar diretamente ou então

```bash
bash autorun
```

# 2. Modo Uso

Ao acessar o endereço `http://localhost:3000`, o usuário será apresentado à seguinte página:

![](assets/buscadoc1.png)

Ao fazer uma busca, os resultados mais relevantes para ela de acordo com o modelo serão mostradas e sua relevância poderá ser classificada pelo usuário.

![](assets/buscadoc2.png)

Ao terminar de classificar os resultados, o usuário deve clicar em "enviar" no fim da página.

Na aba **DOCUMENTOS**, o usuário pode inserir arquivos do tipo *csv* no seguinte formato:

![](assets/insertion.png)

de acordo com o arquivo de exemplo `new_docs.csv`. Os campos são:

- **code**: O código do arquivo de acordo como site da Câmara.
- **name**: O nome do arquivo
- **txt_ementa**: A ementa
- **text**: O texto completo (equivalente à *imgArquivoTeorPDF* nas bases da Câmara)