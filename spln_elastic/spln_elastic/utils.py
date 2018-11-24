#!/usr/bin/python3
#----------------------------------------------------------------

import json
from elasticsearch import Elasticsearch
import os, sys, re

def load_documents(idx, dtype, files, es):

    # Create an index (ignore if it already exists)
    es.indices.create(index = idx, ignore = 400)

    for file_o in files:
        with open(file_o) as f:
            data = json.load(f)
            es.index(index = idx, doc_type = dtype, body = data)


def match(content, field, exact, idx, dtype, es):

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
    return es.search(index = idx, doc_type = dtype, body = {
        "query": {
            "multi_match" : {
                "query" : content,
                "fields" : fields
            }
        }
    })

def common_terms(content, field, idx, dtype, cutoff_frequency, es):
    return es.search(index = idx, doc_type = dtype, body = {
        "query": {
            "common" : {
                field : {
                    "query": content,
                    "cutoff_frequency": cutoff_frequency,
                }
            }
        }
    })

def query_string(content, fields, idx, dtype, es):
    return es.search(index = idx, doc_type = dtype, body = {
        "query": {
            "query_string" : {
                "query" : content,
                "fields" : fields
            }
        }
    })

def simple_query_string(content, fields, idx, dtype, es):
    return es.search(index = idx, doc_type = dtype, body = {
        "query": {
            "simple_query_string" : {
                "query" : content,
                "fields" : fields
            }
        }
    })