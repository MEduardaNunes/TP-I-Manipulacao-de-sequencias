import re

def obter_caracteres_validos():
    """ Define o conjunto de caracteres aceitos como válidos para formar palavras."""
    return {"'", "-", ".", "&", "%", "$", ",", "!", "?", "#", "@", ";", "(", ")", "[", "]", "{", "}", "_", "+", "=", "*", "/", ":", "~", "^", "<", ">", "|", "\\"}

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
    termo_em_formacao = ""
    inicio_termo_em_formacao = -1 # Guarda o índice do caractere onde o termo atual começou
    
    texto_com_espaco = texto + " " 
    
    caracteres_validos = obter_caracteres_validos()
    
    regex_valido = re.compile(r'[A-Za-zá-úÁ-ÚãõçÇ0-9]') # Permite letras com acento, normais, números e caracteres especiais
    
    for indice_char, caractere in enumerate(texto_com_espaco):
        # Verifica se o caractere é válido (letras, números ou símbolos permitidos)
        if regex_valido.match(caractere) or caractere in caracteres_validos:
            if not termo_em_formacao:
                inicio_termo_em_formacao = indice_char
            termo_em_formacao += caractere.lower()
        else:
            # Se não for um caractere válido, é considerado um separador
            if termo_em_formacao: 
                tokens_com_posicao.append((termo_em_formacao, inicio_termo_em_formacao))  # Adiciona o termo e seu índice
                termo_em_formacao = "" # Reseta para o próximo termo
                inicio_termo_em_formacao = -1

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

class No:
    def __init__(self, valor=None):
        self.valor = valor
        self.proximo = None
        
class IteradorListaLigada:
    def __init__(self, no_inicial):
        self.no_atual = no_inicial

    def __next__(self):
        if self.no_atual is None:
            raise StopIteration
        
        dado_a_retornar = self.no_atual.valor
        self.no_atual = self.no_atual.proximo
        return dado_a_retornar
             
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