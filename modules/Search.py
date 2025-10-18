""" Módulo de Recuperação de Informação (RI)

    A gramática utilizada para processar uma consulta é a seguinte:
        <exp>         ::= <exp_or>                  
        <exp_or>      ::= <exp_and> (OR <exp_and>)* 
        <exp_and>     ::= <exp_not> (AND <exp_not>)*      
        <exp_not>     ::= NOT <exp_not> | <subexp>   
        <subexp>      ::= "(" <exp> ")" | <palavra> 
        <palavra>     ::= (<letra> | <digito>)*  
        <letra>       ::= "a" | "b" | "c" | "d" | "e" | "f" | "g" | "h" | "i" | "j" | "k" | "l" | "m" 
                        | "n" | "o" | "p" | "q" | "r" | "s" | "t" | "u" | "v" | "w" | "x" | "y" | "z"
        <digito>      ::= "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9" 
"""
import sys
import os
import re
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from TrieCompacta import TrieCompacta
from Utils import normaliza_query


class NoParsing:
    """
    Representa um nó da árvore de Parsing
    
    Atributos:
        operador (str): operador do Nó (AND, OR, NOT ou palavra).
        direita (NoParsing): filho à direita do nó.
        esquerda (NoParsing): filho à esquerda do nó.
    """
    def __init__(self, op, dir = None, esq = None):
        self.operador = op
        self.direita = dir
        self.esquerda = esq

    def __repr__(self):
        if self.operador in ("AND", "OR"):
            return f"({self.esquerda} {self.operador} {self.direita})"
        
        elif self.operador == "NOT":
            return f"({self.operador} {self.direita})"
        
        else:
            return self.operador


class ArvoreParsing:
    """
    Representa uma árvore de Parsing.
    
    Atributos:
        query (str): string que representa a consulta a ser realizada.
        tokens (lista de str): lista dos tokens gerados a partir da query.
        raiz (NoTrie): armazena a raíz da árvore de parsing.
    """
    def __init__(self, query = ""):
        self.query = query
        self.tokens = self.gera_tokens()
        self.raiz = None
        self.pos = 0

    def gera_tokens(self):
        """
        Gera lista de tokens a partir da query da árvore.
        
        Retorno:
            A lista de tokens gerada a partir da query.
        """ 
        query_normalizada = self.query.replace('(', ' ( ').replace(')', ' ) ')
        return query_normalizada.split()

    def token_atual(self):
        """
        Retorna o token atual que está sendo processado.
        
        Retorno:
            O token atual ou None, caso todos tenham sido processados.
        """
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        
        return None

    def consome_token(self, esperado = ''):
        """
        Verifica se o token é igual ao esperado e se for, o consome partindo
        para o próximo token, e retorna o token consumido.
        
        Retorno:
            O token consumido.
        """
        token = self.token_atual()

        if esperado in ("AND", "OR", "NOT", "(", ")"):
            valor_esperado = esperado

        else:
            valor_esperado = "palavra"

        if token is None:
            raise ValueError(f"Fim inesperado de tokens, esperado \" {valor_esperado} \"")

        if esperado and token != esperado:
            raise ValueError(f"Token esperado \" {valor_esperado} \" diferente do token atual \" {token} \"")

        self.pos += 1
        return token
    
    def parse_exp(self):
        """
        Representação da regra de <exp>.
        
        Retorno:
            O nó gerado pela regra <exp_or>.
        """
        return self.parse_or()
    
    def parse_or(self):
        """
        Representação da regra de <exp_or>. Processa recursivamente uma 
        expressão or.
        
        Retorno:
            O nó gerado pelo processamento recursivo.
        """
        no_atual = self.parse_and()
        if no_atual is None:
            return None
        
        while self.token_atual() == "OR":
            self.consome_token("OR")

            no_direita = self.parse_and()
            if no_direita is None:
                raise ValueError("Não existe expressão esperada após OR")
            
            if no_atual is None:
                raise ValueError("Não existe expressão esperada antes de OR")
            
            no_atual = NoParsing("OR", no_atual, no_direita)

        return no_atual
    
    def parse_and(self):
        """
        Representação da regra de <exp_and>. Processa recursivamente uma 
        expressão and.
        
        Retorno:
            O nó gerado pelo processamento recursivo.
        """
        no_atual = self.parse_not()
        if no_atual is None:
            return None

        while self.token_atual() == "AND":
            self.consome_token("AND")

            no_direita = self.parse_not()
            if no_direita is None:
                raise ValueError("Não existe expressão esperada após AND")
            
            if no_atual is None:
                raise ValueError("Não existe expressão esperada antes de AND")

            no_atual = NoParsing("AND", no_atual, no_direita)

        return no_atual
    
    def parse_not(self):
        """
        Representação da regra de <exp_not>. Processa recursivamente uma 
        expressão not.
        
        Retorno:
            O nó gerado pelo processamento recursivo.
        """
        if self.token_atual() == "NOT":
            self.consome_token("NOT")

            if self.token_atual() is None:
                raise ValueError("Não existe expressão esperada após NOT")
            
            no_direita = self.parse_not()
            if no_direita is None:
                raise ValueError("Não existe expressão esperada após NOT")
            
            return NoParsing("NOT", no_direita)

        else:
            return self.parse_subexp()
    
    def parse_subexp(self):
        """
        Representação da regra de <sub_exp>. Processa recursivamente uma 
        sub-expressão.
        
        Retorno:
            O nó gerado pelo processamento recursivo.
        """

        if self.token_atual() == "(":
            self.consome_token("(")

            if self.token_atual() == ")":
                raise ValueError("Parênteses vazio")

            no_atual = self.parse_exp()

            if no_atual is None:
                raise ValueError("Expressão do parênteses não existe")
            
            if self.token_atual() != ")":
                raise ValueError("Falta de parênteses fechando a expressão")

            self.consome_token(")")

            return no_atual
        
        elif re.match(r'[a-z0-9]+$', self.token_atual() or "") and self.token_atual() not in ("AND", "OR", "NOT", "(", ")"):
            palavra = self.consome_token()
            return NoParsing(palavra)
        
        else:
            raise ValueError(f"Token inesperado \" {self.token_atual()} \"")
    
    def gera_parsing_tokens(self):
        """
        Gera a árvore de parsing a partir dos tokens da gramática.
        
        Retorno:
            O nó raiz da árvore de parsing.
        """
        if not self.tokens:
            print("ERRO: expressão vazia")
            return None
        
        self.raiz = self.parse_exp()

        if self.raiz is None:
            print("ERRO: parsing falhou, expressão incompleta ou inválida")

        if self.pos < len(self.tokens):
            print("ERRO: tokens não consumidos")
            self.raiz = None

        return self.raiz


def processa_arvore_parsing(no : NoParsing, trie_palavras: TrieCompacta, todos_arquivos : set):
    """
    Processa uma árvore de Parsing recursivamente,
    buscando os arquivos em uma trie.
    
    Atributos:
        no (NoParsing): o nó que será processado.
        trie_palavras (TrieCompacta): a trie que armazena todas palavras de todos os arquivos.
        todos_arquivos (set): todas tuplas (seção, número) dos arquivos.
    
    Retorno:
        Um set com todos os arquivos que satisfazem a consulta.
    """
    if no is None:
        return set()
    
    if no.operador == "AND":
        return (processa_arvore_parsing(no.esquerda, trie_palavras, todos_arquivos) 
                & processa_arvore_parsing(no.direita, trie_palavras, todos_arquivos))
    
    elif no.operador == "OR":
        return (processa_arvore_parsing(no.esquerda, trie_palavras, todos_arquivos)
                | processa_arvore_parsing(no.direita, trie_palavras, todos_arquivos))

    elif no.operador == "NOT":
        return todos_arquivos - (processa_arvore_parsing(no.direita, trie_palavras, todos_arquivos))
    
    else:
        palavra = no.operador
        lista_invertida_palavra = trie_palavras.busca_palavra(palavra)
        return set(lista_invertida_palavra.keys()) if lista_invertida_palavra else set()


def tem_no_invalido(no):
    """
    Verifica recursivamente se um no é inválido, ou seja, se algum
    de seus filhos tem um filho "None".
    
    Atributos:
        no (NoParsing): o nó a ser verificado.

    Retorno:
        True se for inválido, ou False caso contrário.
    """
    if no is None:
        return True
    
    if no.operador in ("AND", "OR"):
        return tem_no_invalido(no.esquerda) or tem_no_invalido(no.direita)
    
    if no.operador == "NOT":
        return tem_no_invalido(no.direita)
    
    return False


def arvore_eh_valida(arvore):
    """
    Verifica se uma árvore é inválida, verificando se sua raíz é
    None ou se não tem nenhum nó filho inválido.
    
    Atributos:
        arvore (NoParsing): a árvore a ser verificada.

    Retorno:
        True se for válida, ou False caso contrário.
    """
    if arvore is None:
        return False
    
    else: 
        return not tem_no_invalido(arvore)


def realiza_consulta(query, trie_palavras : TrieCompacta, todos_documentos : set):
    """
    Realiza uma consulta de uma query em um conjunto de documentos, 
    por meio de uma trie compacta que armazena todas palavras dos
    documentos e de uma árvore de parsing que processa a query.
    
    Atributos:
        query (str): a consulta a ser realizada.
        trie_palavras (TrieCompacta): a trie compacta que tem todas palavras dos arquivos.
        todos_documento (set): conjunto das tuplas (seção, número) de todos os arquivos.

    Retorno:
        Um set com todos os arquivos que satisfazem a consulta
        ou None caso ocorra um erro.
    """
    query_normalizada = normaliza_query(query)
    parser = ArvoreParsing(query_normalizada)
    arvore = parser.gera_parsing_tokens()

    if arvore_eh_valida(arvore):
        return processa_arvore_parsing(arvore, trie_palavras, todos_documentos)
    
    else:
        return None