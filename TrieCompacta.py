class No:
    def __init__(self, valor):
        self.valor = valor
        self.filhos = []

    def insereFilho(self, filho : No):
        self.filhos.append(filho)

class TrieCompacta:
    def __init__(self, raiz : No):
        self.raiz = raiz

    def insere(self, palavra):
        return
    
    def busca(self, palavra):
        return