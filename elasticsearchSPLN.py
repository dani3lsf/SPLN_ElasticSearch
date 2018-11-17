#!/usr/bin/python3

import json
from elasticsearch import Elasticsearch
from datetime import datetime

#import credentials
credentialsJson = open('credentials.json','r')
credentials = json.load(credentialsJson)
credentialsJson.close()

#Setup elasticsearch
es = Elasticsearch(credentials['es_endpoint'], 
    http_auth=(credentials['username'],credentials['password']))


""" Exemplo de uso do elasticsearch """

doc = {
    'author': 'kimchy',
    'text': 'Elasticsearch: cool. bonsai cool.',
    'timestamp': datetime.now(),
}         

res = es.index(index="test-index", doc_type='tweet', id=1, body=doc)
print(res['result'])

res = es.get(index="test-index", doc_type='tweet', id=1)
print(res['_source'])

es.indices.refresh(index="test-index")

res = es.search(index="test-index", body={"query": {"match_all": {}}})
print("Got %d Hits:" % res['hits']['total'])
for hit in res['hits']['hits']:
    print("%(timestamp)s %(author)s: %(text)s" % hit["_source"])
 
res = es.delete(index="test-index", doc_type='tweet', id=1)
print(res['result'])

