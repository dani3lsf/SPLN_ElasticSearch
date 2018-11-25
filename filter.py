#!/usr/bin/python3
#-------------------------IMPORTS----------------------------------------------------

import os, getopt, sys, re, logging
import spln_elastic, json
from elasticsearch import Elasticsearch
import subprocess

try:
    import gnureadline as readline
except ImportError:
    import readline

#---------------------VARIÁVEIS-E-INICIALIZAÇÃO--------------------------------------

idx = 'default_idx'      # indice a utilizar nas operações 
doc_t = 'default_type'   # tipo de documento a utilizar nas operações
ops, args = getopt.getopt(sys.argv[1:], 'bp:f:i:n:ed:c:sS', ['help'])
ops = dict(ops)

if os.path.isfile("./credentials.json"):
    credentials_json = open('spln_elastic/data/credentials.json', 'r')
    credentials = json.load(credentials_json)
    credentials_json.close()

    es = Elasticsearch(credentials['es_endpoint'], 
        http_auth = (credentials['username'], credentials['password']))
else:
    es = Elasticsearch()

#-----------------------READLINE-Interpretador --------------------------------------

LOG_FILENAME = '/tmp/completer.log'
logging.basicConfig(
    format = '%(message)s',
    filename = LOG_FILENAME,
    level = logging.DEBUG,
)

class Completer:

    def __init__(self):
        pass

    def complete(self, curr_word, state):
        """Função que calcula as formas possíveis de completar uma determinada
        palavra tendo sido dado um prefixo. Armazena os sucessivos pedidos num 
        log.
        
        Args:
            curr_word: A palavra em que nos encotramos e que faz parte do prefixo
            state: O número de vezes que a curr_word já apareceu

        Returns:
            string: a string resultado
        """
        response = None
        
        if state == 0:
            # This is the first time for this text,
            # so build a match list.
            prefix = readline.get_line_buffer()

            if prefix:
                
                res = spln_elastic.match_as_you_type(prefix, curr_word, field, idx, doc_t, es)
                self.matches = res

                logging.debug('%s matches: %s',
                              repr(curr_word), self.matches)
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
                      repr(curr_word), state, repr(response))
        return response

#-------------------------Funções Principais-----------------------------------------

def input_loop(query_type):
    """Função que fica num loop constante a receber queries do cliente até
    ser lida a string "\stop"
    
    Args:
        query_type: string que define o tipo de query a ser executada para 
                    cada input
    """

    line = ''
    while line != '\stop':
        line = input('Prompt ("\stop" to quit): ')
        line, fd = spln_elastic.redirect_output(line)
        if(line != '\stop'):
            execute_query(line, query_type, fd)

def get_query_type():
    """Função que permite identificar com base nos argumentos passados ao
    programa qual o tipo de search query que deverá ser utilizada.

    Returns:
        string: string que define o tipo da query
    """
    if('-s' in ops): return 'simple_query_string'
    elif('-S' in ops): return 'query_string'
    elif('-c' in ops): return 'common_terms'
    elif('-e' in ops): return 'exact_match'
    else:
        if isinstance(field, list):
            return 'multi_match'
        else:
            return 'match'

def execute_query(pattern, query_type, print_to):
    """Função que consoante o tipo de query em questão invoca a função
    final que executará a elasticsearch query. Imprime o resultado para
    o stdout ou para ficheiro
    
    Args:
        pattern: padrão a procurar
        query_type: tipo de query da api do elastisearch
        print_to: file descriptor de saída a utilizar
    """

    global field, idx, doc_t

    if query_type == "simple_query_string":
        res = spln_elastic.simple_query_string(pattern, field, idx, doc_t, es)
    elif query_type == "query_string":
        res = spln_elastic.query_string(pattern, field, idx, doc_t, es)
    elif query_type == "common_terms":
        cutoff = ops['-c']
        res = spln_elastic.common_terms(pattern, field, idx, doc_t, cutoff, es)
    elif query_type == "multi_match":
        res = spln_elastic.multi_match(pattern, field, idx, doc_t, es)
    elif query_type == "exact_match":
        exact = True
        res = spln_elastic.match(pattern, field, exact, idx, doc_t, es)
    else:
        exact = False
        res = spln_elastic.match(pattern, field, exact, idx, doc_t, es)

    if '-n' in ops:
        spln_elastic.pretty_print(res['hits']['hits'], int(ops['-n']), print_to)
    else:
        spln_elastic.pretty_print(res['hits']['hits'], int(res['hits']['total']), print_to)

#-------------------------Lógica-do-Programa-----------------------------------------

if '-i' in ops:
    idx = ops['-i']

if '-d' in ops:
    doc_t = ops['-d']

mutual_exclusive = [i for i in ['-b','-e', '-s', '-S', '-c','--help'] if i in ops]
if len(mutual_exclusive) > 1:
    print("As opções " + str(mutual_exclusive) + " são mutuamente exclusivas.")
    print("Utilize \'--help' para obter mais informação.")
else:
    if '-b' in ops:
        print("Loading files...")
        spln_elastic.load_documents(idx, doc_t, args, es)
    elif '--help' in ops:
        spln_elastic.print_manual()
    else:
        if '-f' in ops:
            field = ops['-f']
            if re.search(r'\s*,\s*', field):
                field = re.split(r'\s*,\s*', field)
            if (('-s' in ops) or ('-S' in ops)) and not isinstance(field,list):
                field = [field]

        else:
            sys.exit("Opção \'-f\' (field) não especificada.")

        query_type = get_query_type()

        if '-p' not in ops:
            # In case no pattern is supplied, it is assumed the user wants the command prompt
            readline.set_completer(Completer().complete)
            readline.parse_and_bind('tab: complete')
            input_loop(query_type)
        else:
            pattern = ops['-p']
            execute_query(pattern, query_type, sys.stdout)

