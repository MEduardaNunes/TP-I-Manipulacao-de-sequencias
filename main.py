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