def processar_texto(texto): # chamada tanto para as querys quanto para os dados da bbc
    palavra_atual = ""
    lista_de_palavras = []
    texto_minusculo = texto.lower() + " "
    
    for caractere in texto_minusculo:
        # verifica se o caractere é uma letra do alfabeto
        if 'a' <= caractere <= 'z':
            palavra_atual += caractere
        else:
            # se não for, é um separador
            if palavra_atual: # verifica se a palavra atual não está vazia
                lista_de_palavras.append(palavra_atual)
                palavra_atual = "" # reseta para a próxima palavra

    return lista_de_palavras

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

class ListaLigada():
    def __init__(self):
        self.cabeca = None
        self.cauda = None
        self.tamanho = 0
    
    def __len__(self):
        return self.tamanho
    
    def __repr__(self):
        if self.cabeca is None:
            return "Lista([])"
        
        elementos = []
        no_atual = self.cabeca
        while no_atual is not None:
            elementos.append(repr(no_atual.valor)) 
            no_atual = no_atual.proximo
        
        return f"Lista([{', '.join(elementos)}])"
    
    def adicionar(self, item):
        novo_no = No(item)
        if self.cauda is None:
            self.cabeca = novo_no
            self.cauda = novo_no
        else:
            self.cauda.proximo = novo_no
            self.cauda = novo_no
        
        self.tamanho += 1
    
    def obter(self, indice):
        if not (0 <= indice < self.tamanho):
            raise IndexError("Índice fora do intervalo da lista")
        
        no_atual = self.cabeca
        for _ in range(indice):
            no_atual = no_atual.proximo
        
        return no_atual.valor
    
    def __iter__(self):
        return IteradorListaLigada(self.cabeca)

class ListaNaoLigada:
    def __init__(self):
        self.tamanho = 0  
        self.capacidade = 1  
        self._array_interno = self._criar_array(self.capacidade)

    def _criar_array(self, capacidade):
        return [None] * capacidade

    def __len__(self):
        return self.tamanho

    def __repr__(self):
        elementos = [repr(self._array_interno[i]) for i in range(self.tamanho)]
        return f"ListaNaoLigada([{', '.join(elementos)}])"

    def _redimensionar(self, nova_capacidade):
        novo_array = self._criar_array(nova_capacidade)
        for i in range(self.tamanho):
            novo_array[i] = self._array_interno[i]
        
        self._array_interno = novo_array
        self.capacidade = nova_capacidade

    def adicionar(self, item):
        if self.tamanho == self.capacidade:
            self._redimensionar(2 * self.capacidade)
        
        self._array_interno[self.tamanho] = item
        self.tamanho += 1

    def obter(self, indice):
        if not (0 <= indice < self.tamanho):
            raise IndexError("Índice fora do intervalo da lista")
        
        return self._array_interno[indice]

    def __iter__(self):
        for i in range(self.tamanho):
            yield self._array_interno[i]



