from modules.models import Categoria
from collections import namedtuple
from modules.utils import processar_texto
from modules.snippet import _gerar_snippet_formatado

ResultadoItem = namedtuple('ResultadoItem', [
    'doc_id', # tupla (cat_int, num_int)
    'relevancia', # float (média dos z-scores)
    'query_termo', # str (o termo da query a ser destacado)
    'caractere_inicial' # int (índice do caractere inicial do query_termo)
])

def _merge(esquerda, direita):
    """
    Função mergesort: mescla duas listas já ordenadas (por relevância decrescente) em uma única lista ordenada.
    """
    lista_combinada = []
    indice_esq, indice_dir = 0, 0

    # Compara os elementos das duas listas e adiciona o de maior relevância primeiro
    while indice_esq < len(esquerda) and indice_dir < len(direita):
        # Acessa o campo 'relevancia' da namedtuple para comparar
        if esquerda[indice_esq].relevancia >= direita[indice_dir].relevancia:
            lista_combinada.append(esquerda[indice_esq])
            indice_esq += 1
        else:
            lista_combinada.append(direita[indice_dir])
            indice_dir += 1

    # Se houver, adiciona os elementos restantes de uma das listas
    lista_combinada.extend(esquerda[indice_esq:])
    lista_combinada.extend(direita[indice_dir:])
    
    return lista_combinada

def mergesort(lista_resultados):
    """
    Ordena uma lista de objetos ResultadoItem em ordem decrescente de relevância usando o algoritmo mergesort. 
    """
    tamanho = len(lista_resultados)
    if tamanho <= 1: # Caso base: lista já está ordenada (ou vazia).
        return lista_resultados 

    # Divide a lista ao meio
    meio = tamanho // 2
    metade_esquerda = lista_resultados[:meio]
    metade_direita = lista_resultados[meio:]

    esquerda_ordenada = mergesort(metade_esquerda)
    direita_ordenada = mergesort(metade_direita)

    # Combina as metades ordenadas
    return _merge(esquerda_ordenada, direita_ordenada)
            
class GerenciadorResultados:
    """Armazena os resultados de uma busca, ordena-os por relevância e fornece snippets formatados"""
    def __init__(self, caminho_corpus, mapa_categorias, todos_os_termos: list):
        self._resultados= [] # Lista de ResultadoItem
        self._resultados_ordenados = None
        self._caminho_corpus = caminho_corpus
        self._mapa_categorias = mapa_categorias
        self._todos_os_termos = todos_os_termos
        
    def adicionar_resultado(self, doc_id, relevancia, query_termo, caractere_inicial):
        """Adiciona um resultado"""
        if relevancia is None or doc_id is None:
            print(f"[Aviso gerenciador de resultados] Tentativa de adicionar resultado inválido: {doc_id}, {relevancia}")
            return
        
        item = ResultadoItem(doc_id, relevancia, query_termo, caractere_inicial)
        self._resultados.append(item)
        self._resultados_ordenados = None 
    
    def ordenar(self):
        """Ordena os resultados por relevância (decrescente) usando mergesort."""
        if self._resultados_ordenados is None:
            print(f"[DEBUG] Ordenando {len(self._resultados)} resultados...")
            self._resultados_ordenados = mergesort(self._resultados)
            print("[DEBUG] Ordenação concluída.")
      
    def obter_pagina_formatada(self, num_pagina=1, tamanho_pagina=10):
        """
        Retorna uma lista de dicionários formatados para a página especificada,
        incluindo o snippet gerado. Garante que os resultados estejam ordenados.
        """
        if self._resultados_ordenados is None:
            self.ordenar()
        
        # Calcula os índices para a paginação
        inicio = (num_pagina - 1) * tamanho_pagina
        fim = inicio + tamanho_pagina
        
        resultados_pagina = self._resultados_ordenados[inicio:fim]
        resultados_finais = []
        
        for item in resultados_pagina:
            snippet = _gerar_snippet_formatado(
                item.doc_id, 
                item.query_termo, 
                item.caractere_inicial, 
                self._caminho_corpus, 
                self._mapa_categorias,
                self._todos_os_termos
            )

            # Formata o id do doc de (int, int) para string
            categoria_nome = self._mapa_categorias.get(item.doc_id[0], 'desconhecida')
            doc_id_str = f"{categoria_nome}/{item.doc_id[1]:03d}"

            resultados_finais.append({
                'id': doc_id_str,
                'score': f"{item.relevancia:.4f}",
                'snippet': snippet
            })
        
        return resultados_finais