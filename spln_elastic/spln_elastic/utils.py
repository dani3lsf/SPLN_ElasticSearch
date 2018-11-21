#!/usr/bin/python3
#----------------------------------------------------------------

import json
from elasticsearch import Elasticsearch
from datetime import datetime
 

def load(idx, dtype, file, es):
    # Init ids for documents
    id_a = 1

    # Create an index (ignore if it already exists)
    es.indices.create(index = idx, ignore = 400)

    with open(file) as f:
	    data = f.readlines()

    for line in data:
        es.index(index = idx, doc_type = dtype, id = id_a, body = line)
        id_a += 1


def match(content, field, exact, idx, dtype):

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

def match_as_you_type(content, field, idx, dtype):
    return es.search(index = idx, doc_type = dtype, body = {
        "query": {
            "match_phrase_prefix": {
                field: content
            }
        },
        "highlight" : {
            "pre_tags": ["\033[92m"],
            "post_tags" : ["\033[0m"],
            "fields" : {
                field : {}
            }
        }
    })




credentials_json = open('../data/credentials.json', 'r')
credentials = json.load(credentials_json)
credentials_json.close()

# Setup elasticsearch
es = Elasticsearch(credentials['es_endpoint'], 
    http_auth = (credentials['username'], credentials['password']))

#load('news', 'test-type', '../data/')

res = match_as_you_type("CARBO Ceramics", "title", "news", "test-type")
print("%d documents found" % res['hits']['total'])

print("\n===\n")
print(res)
#for doc in res['hits']['hits']:
 #   print("%s) %s" % (doc['_id'], doc['_source']['content']))