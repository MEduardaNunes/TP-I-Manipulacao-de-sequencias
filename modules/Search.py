# Módulo de Recuperação de Informação (RI)

# <exp>         := <exp_or>                  
# <exp_or>      := <exp_and> (OR <exp_and>)* 
# <exp_and>     := <exp_not> (AND <exp_not>)*      
# <exp_not>     := NOT <exp_not> | <subexp>   
# <subexp>      := "(" <exp> ")" | <palavra> 
# <palavra>     := <letra> (<letra> | <digito>)*  

# <letra>       := "a" | "b" | "c" | "d" | "e" | "f" | "g" | "h" | "i" | "j" | "k" | "l" | "m" | "n" | "o" | "p" | "q" | "r" | "s" | "t" | "u" | "v" | "w" | "x" | "y" | "z"
# <digito>      := "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9"
import sys
import os
import re
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from TrieCompacta import TrieCompacta

class NoParsing:
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
    def __init__(self, query = ""):
        self.query = query
        self.tokens = self.gera_tokens()
        self.arvore = None
        self.pos = 0

    def gera_tokens(self):
        query_normalizada = self.query.replace('(', ' ( ').replace(')', ' ) ')
        return query_normalizada.split()

    def token_atual(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        
        else:
            None

    def consome_token(self, esperado = ''):
        token = self.token_atual()

        if token is None:
            print(f"ERRO: fim inesperado de tokens, esperado \" {esperado} \"")

        if esperado and token != esperado:
            print(f"ERRO: token esperado \" {esperado} \" diferente do token atual \" {token} \"")

        self.pos += 1
        return token
    
    def parse_exp(self):
        return self.parse_or()
    
    def parse_or(self):
        no_atual = self.parse_and()
        if no_atual is None:
            return None
        
        while self.token_atual() == "OR":
            self.consome_token("OR")

            no_direita = self.parse_and()
            if no_direita is None:
                print("ERRO: não existe expressão esperada após OR")
                return None
            
            if no_atual is None:
                print("ERRO: não existe expressão esperada antes de OR")
                return None
            
            no_atual = NoParsing("OR", no_atual, no_direita)

        return no_atual
    
    def parse_and(self):
        no_atual = self.parse_not()
        if no_atual is None:
            return None

        while self.token_atual() == "AND":
            self.consome_token("AND")

            no_direita = self.parse_not()
            if no_direita is None:
                print("ERRO: não existe expressão esperada após AND")
                return None
            
            if no_atual is None:
                print("ERRO: não existe expressão esperada antes de AND")
                return None

            no_atual = NoParsing("AND", no_atual, no_direita)

        return no_atual
    
    def parse_not(self):
        if self.token_atual() == "NOT":
            self.consome_token("NOT")
            if self.token_atual is None:
                print("ERRO: não existe expressão esperada após NOT")
                return None
            
            no_direita = self.parse_not()
            if no_direita is None:
                print("ERRO: não existe expressão esperada após NOT")
                return None
            
            return NoParsing("NOT", no_direita)

        else:
            return self.parse_subexp()
    
    def parse_subexp(self):
        if self.token_atual() == "(":
            self.consome_token("(")

            if self.token_atual() == ")":
                print("ERRO: parênteses vazio")
                return None

            no_atual = self.parse_exp()

            if no_atual is None:
                print("ERRO: expressão do parênteses não existe")
                return None
            
            if self.token_atual() != ")":
                print("ERRO: falta de parênteses fechando a expressão")
                return None

            self.consome_token(")")

            return no_atual
        
        elif re.match(r'[a-z][a-z0-9]*', self.token_atual() or ""):
            palavra = self.consome_token()
            return NoParsing(palavra)
        
        else:
            print(f"ERRO: Token inesperado \" {self.token_atual()} \"")
    
    def gera_parsing_tokens(self):
        if not self.tokens:
            print("ERRO: expressão vazia")
            return None
        
        self.arvore = self.parse_exp()

        if self.arvore is None:
            print("ERRO: parsing falhou, expressão incompleta ou inválida")

        if self.pos < len(self.tokens):
            print("ERRO: tokens não consumidos")
            self.arvore = None

        return self.arvore
    
    def arvore_eh_valida(self):
        if self.arvore is None:
            return False
        
        else:
            return not tem_no_invalido(self.arvore)

def processa_arvore_booleana(no : NoParsing, trie_palavras: TrieCompacta, todos_arquivos : set):
    if no is None:
        return set()
    
    if no.operador == "AND":
        return (processa_arvore_booleana(no.esquerda, trie_palavras, todos_arquivos) 
                & processa_arvore_booleana(no.direita, trie_palavras, todos_arquivos))
    
    elif no.operador == "OR":
        return (processa_arvore_booleana(no.esquerda, trie_palavras, todos_arquivos)
                | processa_arvore_booleana(no.direita, trie_palavras, todos_arquivos))

    elif no.operador == "NOT":
        return todos_arquivos - (processa_arvore_booleana(no.direita, trie_palavras, todos_arquivos))
    
    else:
        palavra = no.operador
        lista_invertida_palavra = trie_palavras.busca_palavra(palavra)
        return set(lista_invertida_palavra.keys()) if lista_invertida_palavra else set()

def tem_no_invalido(no):
    if no is None:
        return True
    
    if no.operador in ("AND", "OR"):
        return tem_no_invalido(no.esquerda) or tem_no_invalido(no.direita)
    
    if no.operador == "NOT":
        return tem_no_invalido(no.direita)
    
    return False

def realiza_consulta(query, trie_palavras : TrieCompacta, todos_documentos : set):
    parser = ArvoreParsing(query)
    arvore = parser.gera_parsing_tokens()

    if parser.arvore_eh_valida():
        return processa_arvore_booleana(arvore, trie_palavras, todos_documentos)
    
    else:
        return set()