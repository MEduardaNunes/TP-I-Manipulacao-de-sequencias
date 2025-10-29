from modules.models import Categoria
from collections import namedtuple
from modules.utils import processar_texto, mergesort
from modules.snippet import _gerar_snippet_formatado

ResultadoItem = namedtuple('ResultadoItem', [
    'doc_id', # tupla (cat_int, num_int)
    'relevancia', # float (média dos z-scores)
    'query_termo', # str (o termo da query a ser destacado)
    'caractere_inicial' # int (índice do caractere inicial do query_termo)
])
     
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
        
    def obter_relevancia(self, item):
        """Função para obter a relevância de um ResultadoItem."""
        return item.relevancia
    
    def ordenar(self):
        """
        Ordena os resultados por relevância (decrescente) usando mergesort.
        
        Retorno: None
        
        """
        if self._resultados_ordenados is None:
            print(f"[DEBUG] Ordenando {len(self._resultados)} resultados...")
            self._resultados_ordenados = mergesort(self._resultados, self.obter_relevancia)
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
            print(f"[DEBUG RESULTADOS] Processando item ID: {item.doc_id}", flush=True)
            snippet = "[Snippet não gerado]"
            try:
                snippet = _gerar_snippet_formatado(
                    item.doc_id, 
                    item.query_termo, 
                    item.caractere_inicial, 
                    self._caminho_corpus, 
                    self._mapa_categorias,
                    self._todos_os_termos
                )
                
            except Exception as e:
                # Captura qualquer falha que ocorra no snippet
                print(f"[Erro GerenciadorResultados] Falha ao gerar snippet para {item.doc_id}: {e}", flush=True)
                snippet = "[Falha na geração do snippet]"

            # Formata o id do doc de (int, int) para string
            categoria_int, numero_int = item.doc_id
            categoria_nome = self._mapa_categorias.get(categoria_int, 'desconhecida')
            doc_num_str = f"{numero_int:03d}"
            doc_id_completo_str = f"{categoria_nome}/{doc_num_str}"

            resultados_finais.append({
                'id_completo': doc_id_completo_str,
                'categoria': categoria_nome,
                'id_num': doc_num_str,
                'score': f"{item.relevancia:.4f}",
                'snippet': snippet
            })
        
        return resultados_finais