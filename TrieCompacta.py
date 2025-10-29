class NoTrie:
    """
    Representa um nó da Trie.
    
    Atributos:
        valor (str): string contida no nó
        filhos (list[NoTrie]): Nós filhos desse nó.
        lista_invertida (dict[tuple[int, int], dict[str, int]]): dicionário 
            que mapeia uma chave (seção, número) que indica o documento e 
            associa à frequência de ocorrência de uma palavra no documento
            e à primeira ocorrência dessa palavra.
    """

    def __init__(self, valor):
        self.valor = valor
        self.filhos = []
        self.lista_invertida = {}

    def insere_filho(self, filho : 'NoTrie'):
        """
        Insere um nó filho em ordem de leitura.
        
        Parâmetros:
            filho (NoTrie): nó filho a ser inserido.
        """
            
        self.filhos.append(filho)

    def insere_na_lista_invertida(self, chave, posicao):
        """
        Atualiza a lista_invertida de um nó com uma nova ocorrência.
        
        Parâmetros:
            chave (tuple[int, int]): tupla (seção, número) de um documento.
            posicao (int): posição dentro do documento da palavra.
        """
        if chave in self.lista_invertida:
            self.lista_invertida[chave]["frequencia"] += 1

        else:
            self.lista_invertida[chave] = {
                "frequencia": 1,
                "primeira_posicao": posicao
            }

def prefixo_comum(palavra_um, palavra_dois):
    """
    Retorna o maior prefixo em comum de duas palavras.
        
    Parâmetros:
        palavra_um (string): primeira palavra.
        palavra_dois (string): segunda palavra.

    Retorna:
        O prefixo em comum.
    """

    if palavra_um is None or palavra_dois is None:
        return ""

    i = 0
    while (i < len(palavra_um) and i < len(palavra_dois) and palavra_um[i] == palavra_dois[i]):
        i = i + 1

    return palavra_um[:i]

class TrieCompacta:
    """
    Representa uma Trie Compacta.
    
    Atributos:
        raiz (NoTrie): nó raiz da árvore.
    """

    def __init__(self):
        self.raiz = NoTrie("")

    def insere_palavra(self, palavra, chave, posicao):
        """
        Insere uma palavra na árvore trie.
            
        Parâmetros:
            palavra (string): palavra a ser inserida na trie.
            ocorrencia (Ocorrencia): 3-tupla (categoria, número, posição) referente ao arquivo.
        """

        self.insere_no_recursivo(self.raiz, palavra, chave, posicao)
    
    def insere_no_recursivo(self, no, palavra, chave, posicao):
        """
        Insere recursivamente uma palavra a partir de um nó.
            
        Parâmetros:
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
                        filho.insere_na_lista_invertida(chave, posicao)
                        return
                    
                    # Continua inserindo o restante da paavra em nó filho
                    self.insere_no_recursivo(filho, resto_palavra, chave, posicao)
                    return

                # Se o prefixo em comum não for todo o valor do filho, fazemos split
                resto_filho = filho.valor[len(prefixo):]
                resto_palavra = palavra[len(prefixo):]

                novo_filho = NoTrie(resto_filho)
                novo_filho.filhos = filho.filhos.copy()
                novo_filho.lista_invertida = filho.lista_invertida.copy()

                filho.valor = prefixo
                filho.filhos = [novo_filho]
                filho.lista_invertida = {}

                if resto_palavra:
                    novo_filho_resto = NoTrie(resto_palavra)
                    novo_filho_resto.insere_na_lista_invertida(chave, posicao)
                    filho.insere_filho(novo_filho_resto)

                else:
                    filho.insere_na_lista_invertida(chave, posicao)

                return

        # Caso não tenha prefixo comum com nenhum filho, cria novo nó
        novo_no = NoTrie(palavra)
        novo_no.insere_na_lista_invertida(chave, posicao)
        no.insere_filho(novo_no)
    
    def busca_palavra(self, palavra):
        """
        Busca as ocorrências de uma palavra na Trie, caso tenha.
            
        Parâmetros:
            palavra (string): palavra a ser buscada na trie.

        Retorna:
            A lista de ocorrências da palavra ou a lista vazia, se ela não existe na trie.
        """

        return self.busca_no_recursivo(self.raiz, palavra)
    
    def busca_no_recursivo(self, no, palavra):
        """
        Busca as ocorrências de uma palavra na Trie, caso tenha, recursivamente.
            
        Parâmetros:
            palavra (string): palavra a ser buscada na trie.
            no (NoTrie): o nó em que é buscada a palavra.

        Retorna:
            A lista de ocorrências da palavra ou a lista vazia, se ela não existe na trie.
        """
        for filho in no.filhos:
            prefixo = prefixo_comum(palavra, filho.valor)

            # Não tem prefixo em comum, então continua
            if prefixo == "":
                continue

            # A palavra e a o valor de filhos são iguais, então palavra foi achada
            if prefixo == palavra and prefixo == filho.valor:
                return filho.lista_invertida
            
            # A palavra ainda não foi totalmente encontrada, então busca recursivamente
            # No filho o restante da palavra
            elif prefixo == filho.valor and len(filho.valor) < len(palavra):
                resto_palavra = palavra[len(prefixo):]
                resultado = self.busca_no_recursivo(filho, resto_palavra)

                if resultado:
                    return resultado
            
            # O prefixo não cobre toda a palavra; palavra não encontrada na Trie
            elif len(prefixo) < len(filho.valor):
                return {}

        return {}
    
    def imprimir_arvore(self, mapa_categorias = None, limite = 20):
        """
        Imprime a Trie Compacta a partir da raiz.
            
        Parâmetros:
            mapa_categorias (map): enumeração que traduz um número para uma categoria.
            limite (int): limite de nós a serem impressos.
        """
         
        print("\n--- Conteúdo da Trie ---")
        
        if not self.raiz.filhos:
            print("(A árvore está vazia)")
            return
        
        # A recursão começa na raiz, que tem um valor/prefixo vazio.
        self._imprimir_recursivo(self.raiz, "", mapa_categorias, limite, {'count': 0})

    def _imprimir_recursivo(self, no, prefixo_atual, mapa_categorias, limite, contador):
        """
        Imprime a Trie Compacta recursivamente a partir de um nó.
            
        Parâmetros:
            no (NoTrie): o nó que será impresso.
            prefixo_atual (str): prefixo acumulado até o nó atual.
            mapa_categorias (map): enumeração que traduz um número para uma categoria.
            limite (int): limite de nós a serem impressos.
            contador (dict): dicionário que armazena contador das impressões. 
        """

        # Para a impressão se o limite for atingido
        if contador['count'] >= limite:
            return

        palavra_completa = prefixo_atual + no.valor
        
        if no.lista_invertida:
            print(f"- Palavra: '{palavra_completa}'")
            
            for chave, dados in no.lista_invertida.items():
                if contador['count'] >= limite:
                    print("    -> (limite de impressão atingido)")
                    return

                cat_int, num_int = chave
                freq = dados.get('frequencia', 'N/A') # Usar .get() para segurança
                
                categoria_str = str(cat_int)
                if mapa_categorias and cat_int in mapa_categorias:
                    categoria_str = mapa_categorias[cat_int]
                
                num_str = f"{num_int:03d}"
                
                print(f"    -> Documento: {categoria_str}/{num_str}, Frequência: {freq}")
                contador['count'] += 1

        for filho in no.filhos:
            if contador['count'] < limite:
                self._imprimir_recursivo(filho, palavra_completa, mapa_categorias, limite, contador)