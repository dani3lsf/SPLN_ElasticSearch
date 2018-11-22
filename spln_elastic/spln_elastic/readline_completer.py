#!/usr/bin/env python3

import json
from elasticsearch import Elasticsearch
from datetime import datetime
import os
import sys
import re

try:
    import gnureadline as readline
except ImportError:
    import readline
import logging

LOG_FILENAME = '/tmp/completer.log'
logging.basicConfig(
    format='%(message)s',
    filename=LOG_FILENAME,
    level=logging.DEBUG,
)

def match_as_you_type(content, field, idx, dtype):
    lst = []

    res = es.search(index = idx, doc_type = dtype, body = {
        "query": {
            "match_phrase_prefix": {
                field: content
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
        match = re.sub(r'.*(<em>.*</em>)*<em>(.*)</em>(.*)', r'\2\3', match[0])
        lst.append(match)

    return lst

class SimpleCompleter:

    def __init__(self):
        pass

    def complete(self, text, state):
        response = None
        
        if state == 0:
            # This is the first time for this text,
            # so build a match list.
            prefix = readline.get_line_buffer()
            if prefix:
                
                res = match_as_you_type(prefix, "Titulo", "articles", "test-type")
                self.matches = res

                logging.debug('%s matches: %s',
                              repr(text), self.matches)
            else:
                logging.debug('(empty input) matches: %s',
                              self.matches)

        # Return the state'th item from the match list,
        # if we have that many.
        try:
            response = self.matches[state]
        except IndexError:
            response = None
        logging.debug('complete(%s, %s) => %s',
                      repr(text), state, repr(response))
        return response

def redirect_output(line):
    output = re.search(r'(.*)\s+>\s+(.*)',line)
    if output:
        output_path = output.group(2)
        try:
            f = open(output_path, 'w')
            return output.group(1) ,f
        except FileNotFoundError:
            print("Ficheiro de saída inválido!! Redirecionando para o stdout ...")
            return output.group(1), sys.stdout
    else:
        return line, sys.stdout

def input_loop():
    line = ''
    while line != 'stop':
        line = input('Prompt ("stop" to quit): ')
        line, fd = redirect_output(line)
        output = match(line, 'Titulo', True, "articles", "test-type")
        print(output, file=fd)

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

es = Elasticsearch()

#es.indices.create(index = "articles", ignore = 400)
#es.indices.delete(index='articles', ignore=[400, 404])

# Register the completer function
readline.set_completer(SimpleCompleter().complete)

# Use the tab key for completion
readline.parse_and_bind('tab: complete')

print("OLALALALALA", file=sys.stdout)

# Prompt the user for text
input_loop()
