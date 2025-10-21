import re

def processar_texto(texto):
    """
    Normaliza um texto: converte para minúsculas e extrai palavras/números,
    junto com o índice do caractere inicial de cada um no texto original.

    Parâmetros:
        texto (str): A string de entrada a ser processada.

    Retorno:
        list[tuple[str, int]]: Uma lista de tuplas, onde cada tupla contém
                               o termo normalizado (str) e seu índice de
                               caractere inicial (int) no texto original.
                               Ex: [('palavra1', 0), ('123', 9), ...]
    """
    
    tokens_com_posicao = [] # Lista para armazenar as tuplas (termo, indice_char)
    termo_atual = ""
    inicio_termo_atual = -1 # Guarda o índice do caractere onde o termo atual começou
    
    texto_com_espaco = texto + " "
    
    for indice_char, caractere in enumerate(texto_com_espaco):
        # Verifica se o caractere é uma letra ou um número.
        if caractere.isalnum():
            if not termo_atual:
                inicio_termo_atual = indice_char
            termo_atual += caractere.lower()
        else:
            # Se não for, é um separador
            if termo_atual: # Verifica se o termo atual não está vazio
                tokens_com_posicao.append((termo_atual, inicio_termo_atual))
                termo_atual = "" # Reseta para o próximo termo
                inicio_termo_atual = -1

    return tokens_com_posicao

def normaliza_query(query):
    """
    Normaliza a query, convertando palavras para minúsculo (com exceção os operadores)
    e tira apóstofres possesivos (como Carl's -> Carl).

    Parâmetros:
        query (str): A string a ser processada.

    Retorno:
        A string normalizada.
    """
    query_normalizada = ""
    palavras_query = query.replace('(', ' ( ').replace(')', ' ) ').split()

    for palavra in palavras_query:
        if palavra in ("AND", "OR", "NOT", "(", ")"):
            query_normalizada += palavra + " "

        else:
            palavra = re.sub(r"['’]s$", "", palavra)
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



