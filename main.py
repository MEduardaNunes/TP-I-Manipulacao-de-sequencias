from enum import Enum

class No:
    def __init__(self, valor):
        self.valor = valor
        self.filhos = []

class TrieCompacta:
    def __init__(self, raiz : No):
        self.raiz = raiz

class Categoria(Enum):
    business = 1
    entertainment = 2
    politics = 3
    sport = 4
    tech = 5