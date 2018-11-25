import json
import re, sys, subprocess

def load_documents(idx, dtype, files, es):
    """Função premite indexar um conjuto de documentos json num elasticsearch
    cluster/node. 
    
    Args:
        idx: indice a utilizar na indexação
        dtype: tipo do documento
        files: conjunto de documentos a inserir
        es: instância do Elasticsearch
    """

    # Create an index (ignore if it already exists)
    es.indices.create(index = idx, ignore = 400)

    for file_o in files:
        with open(file_o) as f:
            data = json.load(f)
            es.index(index = idx, doc_type = dtype, body = data)

def redirect_output(line):
    """Função que permite criar um file descriptor para o possível ficheiro
    definido na linha de input.
    
    Args:
        line: linha onde se encontra definido (ou não) o ficheiro de saída

    Returns:
        string: linha de input sem o redirecionamento para o ficheiro
        fd: file descriptor para o redirecionamento futuro
    """
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

def print_manual():
    """Função que faz uma invocação ao comando "more" da bash e que premite imprimir
    o manual do programa.
    """
    return subprocess.call(['more','manual.txt'])

def pretty_print(hits, times, print_to):
    """Função que imprime com um template específico um determinado número
    de documentos utilizando um file descriptor específico.
    
    Args:
        hits: conjunto de documento que fizeram match com uma determinada query
        times: limite para o número de documentos a imprimir
        print_to: file descriptor de saída
    """

    for doc in hits:
        if times > 0:
            print("=" * 79, file=print_to)
            json_file = json.dumps(doc['_source'])
            json_f = json.loads(json_file)
            for field, content in json_f.items():
                print(field.upper() + ": " + content, file=print_to)
            times -= 1