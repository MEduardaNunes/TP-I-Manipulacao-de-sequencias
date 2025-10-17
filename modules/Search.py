# Módulo de Recuperação de Informação (RI)

# <exp>         := <exp_or>                  
# <exp_or>      := <exp_and> (OR <exp_and>)* 
# <exp_and>     := <exp_not> (AND <exp_not>)*      
# <exp_not>     := NOT <exp_not> | <subexp>   
# <subexp>      := "(" <exp> ")" | <palavra> 
# <palavra>     := <letra> (<letra> | <digito>)*  

# <letra>       := "a" | "b" | "c" | "d" | "e" | "f" | "g" | "h" | "i" | "j" | "k" | "l" | "m" | "n" | "o" | "p" | "q" | "r" | "s" | "t" | "u" | "v" | "w" | "x" | "y" | "z" | "A" | "B" | "C" | "D" | "E" | "F" | "G" | "H" | "I" | "J" | "K" | "L" | "M" | "N" | "O" | "P" | "Q" | "R" | "S" | "T" | "U" | "V" | "W" | "X" | "Y" | "Z"
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

        if token == None:
            print(f"ERRO: fim inesperado de tokens, esperado \" {esperado} \"")

        if esperado and token != esperado:
            print(f"ERRO: token esperado \" {esperado} \" diferente do token atual \" {token} \"")

        self.pos += 1
        return token
    
    def parse_exp(self):
        return self.parse_or()
    
    def parse_or(self):
        no_atual = self.parse_and()
        if no_atual == None:
            return None
        
        while self.token_atual() == "OR":
            self.consome_token("OR")

            no_direita = self.parse_and()
            if no_direita == None:
                print("ERRO: não existe expressão esperada após OR")
                return None
            
            no_atual = NoParsing("OR", no_atual, no_direita)

        return no_atual
    
    def parse_and(self):
        no_atual = self.parse_not()
        if no_atual == None:
            return None

        while self.token_atual() == "AND":
            self.consome_token("AND")

            no_direita = self.parse_not()
            if no_direita == None:
                print("ERRO: não existe expressão esperada após AND")
                return None

            no_atual = NoParsing("AND", no_atual, no_direita)

        return no_atual
    
    def parse_not(self):
        if self.token_atual() == "NOT":
            self.consome_token("NOT")
            if self.token_atual == None:
                print("ERRO: não existe expressão esperada após NOT")
                return None
            
            no_direita = self.parse_not()
            if no_direita == None:
                print("ERRO: não existe expressão esperada após NOT")
                return None
            
            return NoParsing("NOT", no_direita)

        else:
            return self.parse_subexp()
    
    def parse_subexp(self):
        if self.token_atual() == "(":
            self.consome_token("(")
            no_atual = self.parse_exp()
            self.consome_token(")")

            return no_atual
        
        elif re.match(r'[A-Za-z][A-Za-z0-9]*', self.token_atual() or ""):
            palavra = self.consome_token()
            return NoParsing(palavra)
        
        else:
            print(f"ERRO: Token inesperado \" {self.token_atual()} \"")
    
    def gera_parsing_tokens(self):
        self.arvore = self.parse_exp()

        if self.pos < len(self.tokens):
            print("ERRO: tokens não consumidos")
            self.arvore = None

        return self.arvore

def processa_arvore_booleana(no : NoParsing, trie_palavras: TrieCompacta, todos_arquivos : set):
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
    
def main():
    trie = TrieCompacta()

    trie.insere_palavra("gato", (1, 1), 5)
    trie.insere_palavra("cachorro", (1, 2), 7)
    trie.insere_palavra("peixe", (1, 3), 2)
    trie.insere_palavra("pássaro", (1, 4), 1)

    todos_documentos = {(1, 1), (1, 2), (1, 3), (1, 4)}

    consulta = "gato AND NOT cachorro"
    print(f"\nConsulta: {consulta}")

    parser = ArvoreParsing(consulta)
    arvore = parser.gera_parsing_tokens()
    if arvore == None:
        print("ERRO: erro de sintaxe")

    else :
        print(f"\nÁrvore sintática: {arvore}")
        resultado = processa_arvore_booleana(arvore, trie, todos_documentos)
        if resultado == set():
            print("\nNenhum documento satisfaz a consulta")

        else:
            print("\nDocumentos que satisfazem a consulta:")
            for doc in sorted(resultado):
                print(" ", doc)


if __name__ == "__main__":
    main()