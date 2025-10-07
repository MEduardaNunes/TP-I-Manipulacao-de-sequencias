from enum import Enum

class No:
    def __init__(self, valor):
        self.valor = valor
        self.esquerda = None
        self.direita = None

    def insere_esquerda(self, esquerda : 'No'):
        self.esquerda = esquerda

    def insere_direita(self, direita : 'No'):
        self.direita = direita

class TrieCompacta:
    def __init__(self, raiz : No):
        self.raiz = raiz

class Categoria(Enum):
    business = 1
    entertainment = 2
    politics = 3
    sport = 4
    tech = 5