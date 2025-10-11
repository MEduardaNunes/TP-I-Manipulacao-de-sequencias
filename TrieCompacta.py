class Ocorrencia:
    """
    Representa uma ocorrência de uma palavra.
    
    Atributos:
        categoria (int): valor da categoria, seguindo o enum definido no main.
        numero (int): número do texto da categoria.
        posicao (int): posicao no arquivo da primeira letra em que ocorre a palavra.
    """

    def __init__(self, categoria, numero, posicao):
        self.categoria = categoria
        self.numero = numero
        self.posicao = posicao

class No:
    """
    Representa um nó.
    
    Atributos:
        valor (str): string contida no Nó
        filhos (lista de No): Nós filhos desse nó.
        ocorrencias (lista de Ocorrencia): 3-tuplas que indicam a seção,
            o número do arquivo e a posição onde a palavra ocorreu.
    """

    def __init__(self, valor):
        self.valor = valor
        self.filhos = []
        self.ocorrencias = []

    def insere_filho(self, filho : 'No'):
        """
        Insere um filho em um Nó em ordem de leitura do valor do Nó
        
        Parâmetros:
            filho (No): nó filho a ser inserido.
        """
            
        self.filhos.append(filho)

    def insere_ocorrencia(self, occorrencia : Ocorrencia):
        """
        Insere uma ocorrência em um Nó, em ordem de entrada da 3-tupla.
        
        Parâmetros:
            ocorrencia (No): a ocorrência a ser inserida.
        """
            
        self.ocorrencias.append(occorrencia)

def prefixo_comum(palavra_um, palavra_dois):
    """
    Retorna o maior prefixo em comum de duas palavras.
        
    Parâmetros:
        palavra_um (string): primeira palavra.
        palavra_dois (string): segunda palavra.

    Retorno:
        O prefixo em comum.
    """

    i = 0
    while (i < len(palavra_um) and i < len(palavra_dois) and palavra_um[i] == palavra_dois[i]):
        i = i + 1

    return palavra_um[:i]

class TrieCompacta:
    """
    Representa uma Trie Compacta.
    
    Atributos:
        raiz (No): nó raiz da árvore.
    """

    def __init__(self):
        self.raiz = No("")

    def insere_palavra(self, palavra, ocorrencia):
        """
        Insere uma palavra na árvore trie.
            
        Atributos:
            palavra (string): palavra a ser inserida na trie.
            ocorrencia (Ocorrencia): 3-tupla (categoria, número, posição) referente ao arquivo.
        """

        self.insere_no_recursivo(self.raiz, palavra, ocorrencia)
    
    def insere_no_recursivo(self, no, palavra, ocorrencia):
        """
        Insere uma palavra recursivamente na árvore trie.
            
        Atributos:
            no (No): nó a ser verificado onde deve inserir a palavra.
            palavra (string): palavra a ser inserida na trie.
            ocorrencia (Ocorrencia): 3-tupla (categoria, número, posição) referente ao arquivo.
        """

        for filho in no.filhos:
            prefixo = prefixo_comum(filho.valor, palavra)

            # Se tem prefixo em comum
            if prefixo:
                # Se o prefixo em comum for exatamente o valor do filho
                if prefixo == filho.valor:
                    resto_palavra = palavra[len(prefixo):]

                    # Se o prefixo é a palavra toda, insere ocorrencia em filho
                    if resto_palavra == "":
                        filho.insere_ocorrencia(ocorrencia)
                        return
                    
                    # Se tiver resto, continua procurando recursivamente nesse nó
                    self.insere_no_recursivo(filho, resto_palavra, ocorrencia)
                    return

                # Se o prefixo em comum não for todo o valor do filho, fazemos split
                resto_filho = filho.valor[len(prefixo):]
                resto_palavra = palavra[len(prefixo):]

                novo_filho = No(resto_filho)
                novo_filho.filhos = filho.filhos.copy()
                novo_filho.ocorrencias = filho.ocorrencias.copy()

                filho.valor = prefixo
                filho.filhos = [novo_filho]
                filho.ocorrencias = []

                if resto_palavra:
                    novo_filho_resto = No(resto_palavra)
                    novo_filho_resto.insere_ocorrencia(ocorrencia)
                    filho.insere_filho(novo_filho_resto)

                else:
                    filho.insere_ocorrencia(ocorrencia)

                return

        novo_no = No(palavra)
        novo_no.insere_ocorrencia(ocorrencia)
        no.insere_filho(novo_no)
    
    def busca_palavra(self, palavra):
        """
        Busca as recorrências de uma palavra na Trie, caso tenha.
            
        Atributos:
            palavra (string): palavra a ser buscada na trie.
        Retorno:
            A lista de ocorrências da palavra ou a lista vazia, se ela não existe na trie.
        """

        return self.busca_no_recursivo(self.raiz, palavra)
    
    def busca_no_recursivo(self, no, palavra):
        """
        Busca as recorrências de uma palavra na Trie, caso tenha, recursivamente.
            
        Atributos:
            palavra (string): palavra a ser buscada na trie.
            no (No): o nó em que é buscada a palavra.
        Retorno:
            A lista de ocorrências da palavra ou a lista vazia, se ela não existe na trie.
        """
        for filho in no.filhos:
            prefixo = prefixo_comum(palavra, filho.valor)

            # Não tem prefixo em comum -> continua
            if prefixo == "":
                continue

            # A palavra e a o valor de filhos são iguais -> palavra achada
            if prefixo == palavra and prefixo == filho.valor:
                return filho.ocorrencias
            
            elif prefixo == filho.valor and len(filho.valor) < len(palavra):
                resto_palavra = palavra[len(prefixo):]
                resultado = self.busca_no_recursivo(filho, resto_palavra)

                if resultado:
                    return resultado
                
            elif len(prefixo) < len(filho.valor):
                return []

        return []

    
    # linhas seguintes -> DEBUG
    def imprimir_arvore(self):
        print("\n--- Conteúdo da Trie ---")
        if not self.raiz.filhos:
            print("(A árvore está vazia)")
            return
        # A recursão começa na raiz, que tem um valor/prefixo vazio.
        self._imprimir_recursivo(self.raiz, "")

    def _imprimir_recursivo(self, no, prefixo_atual):
        palavra_completa = prefixo_atual + no.valor
        
        if no.ocorrencias:
            print(f"- Palavra: '{palavra_completa}'")
            
            for ocorrencia in no.ocorrencias:
                # Acessa os atributos de cada objeto para imprimir os detalhes.
                cat = ocorrencia.categoria
                num = ocorrencia.numero
                pos = ocorrencia.posicao
                print(f"    -> Categoria: {cat}, Número: {num}, Posição: {pos}")

        for filho in no.filhos:
            # Passa a palavra completa atual como o prefixo para a próxima chamada.
            self._imprimir_recursivo(filho, palavra_completa)