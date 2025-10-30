import re

def obter_caracteres_validos():
    """ Define o conjunto de caracteres aceitos como válidos para formar palavras."""
    return {"'", "-", ".", "&", "%", "$", ",", "!", "?", "#", "@", ";", "[", "]", "{", "}", "_", "+", "=", "*", "/", ":", "~", "^", "<", ">", "|", "\\"}

def _obter_caracteres_internos_palavra():
    """ Define o set de caracteres internos permitidos."""
    # '.' pode ser interno (e.g.) mas também externo. '-' e "'" são normalmente internos.
    return frozenset(["'", "-"]) 

def _obter_simbolos_indexaveis():
    """ Define símbolos que devem ser indexados como tokens separados."""
    return frozenset([".", "&", "%", "$"]) # Adicione outros se necessário (ex: ',', ';')
    
def processar_texto(texto):
    """
    Normaliza um texto: converte para minúsculas, e extrai o índice do caractere inicial de cada um no texto original.

    Parâmetros:
        texto (str): A string de entrada a ser processada.

    Retorno:
        list[tuple[str, int]]: Uma lista de tuplas, onde cada tupla contém o termo 
        normalizado (str) e seu índice de caractere inicial (int) no texto original.
        Ex: [('palavra1', 0), ('123', 9), ...]
    """
    
    tokens_com_posicao = [] # Lista para armazenar as tuplas (termo, indice_char)
    
    # - Palavras: Sequências de letras/números que podem conter '-' ou "'" internamente
    # - Números: Sequências de dígitos, possivelmente com '.' ou ','
    # - Símbolos standalone: Captura os símbolos definidos em _obter_simbolos_indexaveis

    # Constrói o padrão de símbolos
    simbolos_padrao = '[' + re.escape("".join(_obter_simbolos_indexaveis()())) + ']'
    
    padrao = re.compile(r"([a-z0-9'" + re.escape("-") + r"]+)|(" + simbolos_padrao + r")", re.IGNORECASE)
    
    for match in padrao.finditer(texto):
        token = match.group(0) # Pega o texto completo do match
        indice_char = match.start() # Pega o índice inicial

        # Normaliza para minúsculas
        token_normalizado = token.lower()
        
        # Adiciona à lista
        tokens_com_posicao.append((token_normalizado, indice_char))

    return tokens_com_posicao

def normaliza_query(query):
    """
    Normaliza a query, convertando palavras para minúsculo (com exceção os operadores)

    Parâmetros:
        query (str): A string a ser processada.

    Retorno:
        A string normalizada.
    """
    query_normalizada = ""
    termos_query = query.replace('(', ' ( ').replace(')', ' ) ').split()
    
    for palavra in termos_query:
        if palavra in ("AND", "OR", "NOT", "(", ")"):
            query_normalizada += palavra + " "
        else:
            query_normalizada += palavra.lower() + " "

    return query_normalizada.strip()
             
def _merge(esquerda, direita, chave):
    """
    Função de mesclagem do algoritmo Merge Sort. Mescla duas listas ordenadas de forma decrescente em uma única lista ordenada.

    Parâmetros:
        - esquerda (list): Lista ordenada à esquerda.
        - direita (list): Lista ordenada à direita.
        - chave (function): Função que extrai a chave de comparação de cada item.

    Retorno:
        list: Lista mesclada de forma ordenada.
    """
    lista_combinada = []
    indice_esq, indice_dir = 0, 0

    # Compara os elementos das duas listas e adiciona o de maior chave primeiro
    while indice_esq < len(esquerda) and indice_dir < len(direita):
        if  chave(esquerda[indice_esq]) >= chave(direita[indice_dir]):
            lista_combinada.append(esquerda[indice_esq])
            indice_esq += 1
        else:
            lista_combinada.append(direita[indice_dir])
            indice_dir += 1

    # Se houver, adiciona os elementos restantes de uma das listas
    lista_combinada.extend(esquerda[indice_esq:])
    lista_combinada.extend(direita[indice_dir:])
    
    return lista_combinada

def mergesort(lista, chave):
    """
    Ordena uma lista de forma decrescente usando o algoritmo mergesort.

    O algoritmo divide a lista em duas metades recursivamente, até que cada parte contenha um único elemento,
    e depois mescla as metades ordenadas.

    Parâmetros:
        - lista (list): Lista a ser ordenada.
        - chave (function): Função que extrai a chave de comparação de cada item.

    Retorno:
        list: Lista ordenada em ordem decrescente.
    """
    tamanho = len(lista)
    if tamanho <= 1: # Lista já está ordenada (ou vazia)
        return lista 

    # Divide a lista ao meio
    meio = tamanho // 2
    metade_esquerda = lista[:meio]
    metade_direita = lista[meio:]

    esquerda = mergesort(lista[:meio], chave)
    direita = mergesort(lista[meio:], chave)

    # Combina as metades ordenadas
    return _merge(esquerda, direita, chave)

