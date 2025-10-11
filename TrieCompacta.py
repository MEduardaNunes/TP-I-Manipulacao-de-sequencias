class No:
    def __init__(self, segmento=''):
        self.segmento = segmento
        self.filhos = {}
        self.lista_invertida = {} 
        # {id_documento : {'frequencia': X, 'primeira_posicao': Y}}

class TrieCompacta:
    def __init__(self):
        # raiz da trie = nó vazio
        self.raiz = No()

    def insere(self, palavra, id_documento, posicao):
        # insere uma palavra na trie e atualiza o índice
        no_atual = self.raiz
        palavra_restante = palavra
        
        while palavra_restante:
            primeiro_char = palavra_restante[0]
            
            # não há nenhum filho que comece com o mesmo carcatere
            if primeiro_char not in no_atual.filhos:
                novo_no = No(segmento=palavra_restante)
                no_atual.filhos[primeiro_char] = novo_no
                self.atualiza_lista_invertida(novo_no, id_documento, posicao)
                return
            
            # se existe um filho, compara com ele
            filho = no_atual.filhos[primeiro_char]
            segmento_filho = filho.segmento
            
            prefixo_comum = ""
            for i in range(min(len(palavra_restante), len(segmento_filho))):
                if palavra_restante[i] == segmento_filho[i]:
                    prefixo_comum += palavra_restante[i]
                else:
                    break
            
            # o segmento do filho é prefixo da palavra restante -> continua a busca
            if prefixo_comum == segmento_filho:
                no_atual = filho
                palavra_restante = palavra_restante[len(prefixo_comum):]
            else: # o prefixo comum é menor que o segmento do filho -> precisa dividir
                # um novo nó com o prefixo comum precisa ser criado
                no_interno = No(segmento=prefixo_comum)

                # o filho original vira filho do nó interno
                filho.segmento = segmento_filho[len(prefixo_comum):]
                no_interno.filhos[filho.segmento[0]] = filho
                no_atual.filhos[primeiro_char] = no_interno
                
                resto_palavra_nova = palavra_restante[len(prefixo_comum):]
                
                if resto_palavra_nova:
                    novo_no_folha = No(segmento=resto_palavra_nova)
                    no_interno.filhos[resto_palavra_nova[0]] = novo_no_folha
                    self.atualiza_lista_invertida(novo_no_folha, id_documento, posicao)
                else:
                    self.atualiza_lista_invertida(no_interno, id_documento, posicao)
                return
        self.atualiza_lista_invertida(no_atual, id_documento, posicao)
        
    def atualiza_lista_invertida(self, no, id_documento, posicao):
        if id_documento in no.lista_invertida:
            no.lista_invertida[id_documento]['frequencia'] += 1
        else:
            no.lista_invertida[id_documento] = {
                'frequencia': 1,
                'primeira_posicao': posicao
            }
    
    def busca(self, palavra):
        return
    
    # linhas seguintes -> DEBUG
    def imprimir_arvore(self):
        print("--- Conteúdo da Trie ---")
        if not self.raiz.filhos:
            print("(A árvore está vazia)")
            return
        self._imprimir_recursivo(self.raiz, "")

    def _imprimir_recursivo(self, no, prefixo_atual):
        # A palavra completa até este nó é o prefixo acumulado + o segmento deste nó.
        palavra_completa = prefixo_atual + no.segmento
        
        # Se este nó representa o fim de uma palavra...
        if no.lista_invertida:
            print(f"- Palavra: '{palavra_completa}'", flush=True)
            
            # ...itera sobre o dicionário da lista invertida para imprimir os detalhes.
            for doc_id, info in no.lista_invertida.items():
                freq = info['frequencia']
                pos = info['primeira_posicao']
                # A indentação aqui ajuda na legibilidade
                print(f"    -> Doc: {doc_id} | Frequência: {freq} | Primeira Posição: {pos}", flush=True)

        # Continua a recursão para os filhos
        for char_filho in sorted(no.filhos.keys()):
            self._imprimir_recursivo(no.filhos[char_filho], palavra_completa)