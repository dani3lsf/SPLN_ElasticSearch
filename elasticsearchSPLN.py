#!/usr/bin/python3
#------------------------------------------------------------------------------

import json
from elasticsearch import Elasticsearch
from datetime import datetime

# Init ids for articles
id_a = 153082

# Import credentials
credentials_json = open('spln_elastic/data/credentials.json', 'r')
credentials = json.load(credentials_json)
credentials_json.close()

# Setup elasticsearch
es = Elasticsearch(credentials['es_endpoint'], 
    http_auth = (credentials['username'], credentials['password']))

"""     Povoamento do Cluster
# Create an index (ignore if it already exists)
es.indices.create(index = 'news', ignore = 400)

 
with open('data/data.jsonl') as f:
	data = f.readlines()

for line in data:
    es.index(index = 'news', doc_type = 'test-type', id = id_a, body = line)
    id_a += 1
""" 

#es.indices.refresh(index="test-index")

res = es.search(index="news", body={"query": {"match_all": {}}})
print("Got %d Hits:" % res['hits']['total'])
for hit in res['hits']['hits']:
    print("-> id: %(id)s\n-> title: %(title)s\n-> media-type: %(media-type)s\n-> source: %(source)s\n-> published: %(published)s\n-> content: %(content)s\n" % hit["_source"])
 
#res = es.delete(index="test-index", doc_type='tweet', id=1)
#print(res['result'])
 
