#!/usr/bin/python3
#----------------------------------------------------------------

from elasticsearch import Elasticsearch
import re

def match(content, field, exact, idx, dtype, es):
    """Função que implementa a query match default ou a query match_phrase
    da api full text queries do elasticsearch, com base num boleano que 
    identifica se pretendemos exatidão ou não da procura.
    
    Args:
        content: padrão a aplicar no field
        field: campo do documento a aplicar o padrão
        exact: boleano que identifica a exatidão ou não exatidão da procura
        idx: índice que mapeia os documentos onde a procura deverá ser realizada
        dtype: tipo dos documentos a aplicar a procura
        es: instância do Elasticsearch

    Returns:
        objeto com o resultado da query.
    """

    if exact:
        query = "match_phrase"
    else:
        query = "match"

    return es.search(index = idx, doc_type = dtype, body = {
        "query": {
            query: {
                field: content
            }
        }
    })

def match_as_you_type(prefix, curr_word, field, idx, dtype, es):
    """Função que utiliza a query match_phrase_prefix da api full text search
    do ElasticSearch e que identifica a lista das possíveis strings onde o 
    prefixo se aplica.
    
    Args:
        prefix: prefixo completo a utilizar na procura
        curr_word: palavra corrente a completar
        field: campo do documento a aplicar o padrão
        idx: índice que mapeia os documentos onde a procura deverá ser realizada
        dtype: tipo dos documentos a aplicar a procura
        es: instância do Elasticsearch

    Returns:
        lista das possíveis strings onde o prefixo se aplica.
    """

    lst = []

    res = es.search(index = idx, doc_type = dtype, body = {
        "query": {
            "match_phrase_prefix": {
                field : {
                    "query" : prefix,
                    "max_expansions" : 1000
                }
            }
        },
        "highlight" : {
            "fields" : {
               field : {}
            }
        }
    })  
    
    for doc in res['hits']['hits']:
        match = doc['highlight'][field]
        #Condição para o caso em que já se escreveu a palavra que fez match completa
        if( curr_word == "" ):
            #print(match[0])
            match = re.sub(r'.*<em>(.*)</em>\s*(.*)', r'\2', match[0])
        else:
            match = re.sub(r'.*<em>(.*)</em>(.*)', r'\1\2', match[0])
        lst.append(match)

    return lst

def multi_match(content, fields, idx, dtype, es):
    """Função que implementa a query multi_match da api full text queries do 
    elasticsearch. Semelhante à match query mas aplica o padrão a vários fields.
    
    Args:
        content: padrão a aplicar no field
        field: campo do documento a aplicar o padrão
        idx: índice que mapeia os documentos onde a procura deverá ser realizada
        dtype: tipo dos documentos a aplicar a procura
        es: instância do Elasticsearch

    Returns:
        objeto com o resultado da query.
    """
    
    return es.search(index = idx, doc_type = dtype, body = {
        "query": {
            "multi_match" : {
                "query" : content,
                "fields" : fields
            }
        }
    })

def common_terms(content, field, idx, dtype, cutoff_frequency, es):
    """Função que implementa a query common_terms da api full text queries do 
    elasticsearch. Faz match dando maior relevância a palavras mais comuns.
    
    Args:
        content: padrão a aplicar no field
        field: campo do documento a aplicar o padrão
        idx: índice que mapeia os documentos onde a procura deverá ser realizada
        dtype: tipo dos documentos a aplicar a procura
        cutoff_frequency: frequência de cutoff
        es: instância do Elasticsearch

    Returns:
        objeto com o resultado da query.
    """
    return es.search(index = idx, doc_type = dtype, body = {
        "query": {
            "common" : {
                field : {
                    "query": content,
                    "cutoff_frequency": cutoff_frequency
                }
            }
        }
    })

def query_string(content, fields, idx, dtype, es):
    """Função que implementa a query query_string da api full text queries do 
    elasticsearch. Mais poderosa que um match default, deixando utilizar no padrão
    operadores condicionais bem como wildcards.
    
    Args:
        content: padrão a aplicar no field
        fields: campos do documento a aplicar o padrão
        idx: índice que mapeia os documentos onde a procura deverá ser realizada
        dtype: tipo dos documentos a aplicar a procura
        es: instância do Elasticsearch

    Returns:
        objeto com o resultado da query.
    """

    return es.search(index = idx, doc_type = dtype, body = {
        "query": {
            "query_string" : {
                "query" : content,
                "fields" : fields
            }
        }
    })

def simple_query_string(content, fields, idx, dtype, es):
    """Função que implementa a query simple_multi_match da api full text queries do 
    elasticsearch. Semelhante ao query_match mas possui uma syntax mais robusta,
    permitindo utilizar simbolos no padrão tais como ['|','+','-'].
    
    Args:
        content: padrão a aplicar no field
        field: campo do documento a aplicar o padrão
        idx: índice que mapeia os documentos onde a procura deverá ser realizada
        dtype: tipo dos documentos a aplicar a procura
        es: instância do Elasticsearch

    Returns:
        objeto com o resultado da query.
    """
    
    return es.search(index = idx, doc_type = dtype, body = {
        "query": {
            "simple_query_string" : {
                "query" : content,
                "fields" : fields
            }
        }
    })