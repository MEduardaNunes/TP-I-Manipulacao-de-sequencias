# Módulo de Recuperação de Informação (RI)

# <exp>         := <exp_or>                  
# <exp_or>      := <exp_and> (OR <exp_and>)* 
# <exp_and>     := <term> (AND <exp_not>)*      
# <exp_not>     := NOT <exp_not> | <subexp>   
# <subexp>      := "(" <exp> ")" | <palavra> 
# <palavra>     := <letra> (<letra> | <digito>)*  

# <letra>       := "a" | "b" | "c" | "d" | "e" | "f" | "g" | "h" | "i" | "j" | "k" | "l" | "m" | "n" | "o" | "p" | "q" | "r" | "s" | "t" | "u" | "v" | "w" | "x" | "y" | "z" | "A" | "B" | "C" | "D" | "E" | "F" | "G" | "H" | "I" | "J" | "K" | "L" | "M" | "N" | "O" | "P" | "Q" | "R" | "S" | "T" | "U" | "V" | "W" | "X" | "Y" | "Z"
# <digito>      := "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9"

import re

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
            print(f"ERRO: fim inesperado de tokens, esperado ({esperado})")

        if esperado and token != esperado:
            print(f"ERRO: token esperado ({esperado}) diferente do token atual ({token}))")

        self.pos += 1
        return token
    
    def parse_exp(self):
        return self.parse_or()
    
    def parse_or(self):
        no_atual = self.parse_and()
        
        while self.token_atual() == "OR":
            self.consome_token("OR")
            no_atual = NoParsing("OR", no_atual, self.parse_and())

        return no_atual
    
    def parse_and(self):
        no_atual = self.parse_not()

        while self.token_atual() == "AND":
            self.consome_token("AND")
            no_atual = NoParsing("AND", no_atual, self.parse_not())

        return no_atual
    
    def parse_not(self):
        if self.token_atual() == "NOT":
            self.consome_token("NOT")
            return NoParsing("NOT", self.parse_not())

        else:
            return self.parse_subexp()
        
        return
    
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
            print(f"ERRO: Token inesperado ({self.token_atual()})")
    
    def gera_parsing_tokens(self):
        self.arvore = self.parse_exp()