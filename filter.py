#!/usr/bin/python3
#------------------------------------------------------------------------------

import os, getopt, sys, re, logging
import spln_elastic, json
from elasticsearch import Elasticsearch

try:
    import gnureadline as readline
except ImportError:
    import readline

LOG_FILENAME = '/tmp/completer.log'
logging.basicConfig(
    format = '%(message)s',
    filename = LOG_FILENAME,
    level = logging.DEBUG,
)

field = 'texto'
idx = 'news'
doc_t = 'test-type'

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
                
                res = match_as_you_type(prefix, field, idx, doc_t)
                self.matches = res

                logging.debug('%s matches: %s',
                              repr(text), self.matches)
            else:
                logging.debug('(empty input) matches: %s',
                              self.matches)
        try:
            response = self.matches[state]
        except IndexError:
            response = None
        
        logging.debug('complete(%s, %s) => %s', repr(text), state,
                                                repr(response))
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
        output = match(line, field, True, idx, doc_t)
        print(output, file=fd)

def execute_query(pattern, highlight, cf, exact, sqs, qs):
    global field, idx, doc_t
    
    if isinstance(field, list):
        if sqs:
            res = spln_elastic.simple_query_string(pattern, field, idx, doc_t, es)
        elif qs:
            res = spln_elastic.query_string(pattern, field, idx, doc_t, es)
        else:
            res = spln_elastic.multi_match(pattern, field, idx, doc_t, es)
    elif cf:
        res = spln_elastic.common_terms(pattern, field, idx, doc_t, ops['-c'], es)
    else:
        res = spln_elastic.match(pattern, field, exact, idx, doc_t, es)

    if '-n' in ops:
        print_to_terminal(res['hits']['hits'], int(ops['-n']))
    else:
        print_to_terminal(res['hits']['hits'], int(res['hits']['total']))


def print_to_terminal(hits, times):
    for doc in hits:
        if times > 0:
            print("=" * 79)
            json_file = json.dumps(doc['_source'])
            json_f = json.loads(json_file)
            for field, content in json_f.items():
                print(field.upper() + ": " + content)
            times -= 1


#------------------------------------------------------------------------------

ops, args = getopt.getopt(sys.argv[1:], 'bp:f:i:hn:ed:c:')
ops = dict(ops)

if os.path.isfile("./credentials.json"):
    credentials_json = open('spln_elastic/data/credentials.json', 'r')
    credentials = json.load(credentials_json)
    credentials_json.close()

    es = Elasticsearch(credentials['es_endpoint'], 
        http_auth = (credentials['username'], credentials['password']))
else:
    es = Elasticsearch()

if '-i' in ops:
    idx = ops['-i']
if '-d' in ops:
    doc_t = ops['-d']

if '-b' in ops:
    print("Loading files...")
    print(args)
    load_documents(idx, doc_t, args, es)
else:
    if '-f' in ops:
        field = ops['-f']

    if '-p' not in ops:
        # In case no pattern is supplied, it is assumed the user wants the command prompt
        readline.set_completer(SimpleCompleter().complete)
        readline.parse_and_bind('tab: complete')
        input_loop()
    else:
        pattern = ops['-p']

        execute_query(pattern, '-h' in ops, '-c' in ops, '-e' in ops, '-s' in ops, '-S' in ops)