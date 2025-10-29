"""Módulo de Recuperação de Informação (RI)

    A gramática utilizada para processar uma consulta é a seguinte:
        <exp>         ::= <exp_or>                  
        <exp_or>      ::= <exp_and> (OR <exp_and>)* 
        <exp_and>     ::= <exp_not> (AND <exp_not>)*      
        <exp_not>     ::= NOT <exp_not> | <subexp>   
        <subexp>      ::= "(" <exp> ")" | <palavra> 
        <palavra>     ::= (<simbolo> | <digito>)*  
        <simbolo>       ::= "a" | "b" | "c" | "d" | "e" | "f" | "g" | "h" | "i" | "j" | "k" | "l" | "m" 
                        | "n" | "o" | "p" | "q" | "r" | "s" | "t" | "u" | "v" | "w" | "x" | "y" | "z"
                        | "-" | "'"
        <digito>      ::= "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9" 
"""
import sys
import os
import re
import traceback
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from modules.resultados import ResultadoItem, GerenciadorResultados
from TrieCompacta import TrieCompacta
from modules.models import Categoria
from modules.utils import normaliza_query

class NoParsing:
    """
    Representa um nó da árvore de Parsing
    
    Atributos:
        operador (str): operador do Nó (AND, OR, NOT ou palavra).
        direita (NoParsing): filho à direita do nó.
        esquerda (NoParsing): filho à esquerda do nó.
    """
    def __init__(self, operador, direita = None, esquerda = None):
        self.operador = operador
        self.direita = direita
        self.esquerda = esquerda

    def __repr__(self):
        if self.operador in ("AND", "OR"):
            return f"({self.esquerda} {self.operador} {self.direita})"
        
        elif self.operador == "NOT":
            return f"({self.operador} {self.direita})"
        
        else:
            return self.operador


class ArvoreParsing:
    """
    Representa uma árvore de Parsing.
    
    Atributos:
        query (str): string que representa a consulta a ser realizada.
        tokens (lista de str): lista dos tokens gerados a partir da query.
        raiz (NoParsing): armazena a raiz da árvore de parsing.
    """
    def __init__(self, query = ""):
        self.query = query
        self.tokens = self.gera_tokens()
        self.raiz = None
        self.pos = 0

    def gera_tokens(self):
        """
        Gera lista de tokens a partir da query da árvore.
        
        Retorna:
            A lista de tokens gerada a partir da query.
        """ 
        query_normalizada = normaliza_query(self.query)
        query_normalizada = self.query.replace('(', ' ( ').replace(')', ' ) ')
        return query_normalizada.split()

    def token_atual(self):
        """
        Retorna o token atual que está sendo processado.
        
        Retorna:
            O token atual ou None, caso todos tenham sido processados.
        """
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        
        return None

    def consome_token(self, esperado = ''):
        """
        Consome o token atual, verificando se o token é igual ao esperado (se fornecido).
        Caso o token não corresponda ao esperado, lança ValueError.

        Parâmetros:
            esperado (str): token esperado a ser consumido.
        
        Retorna:
            O token consumido.
        """
        token = self.token_atual()

        if esperado in ("AND", "OR", "NOT", "(", ")"):
            valor_esperado = esperado

        else:
            valor_esperado = "palavra"

        if token is None:
            raise ValueError(f"Fim inesperado de tokens, esperado \" {valor_esperado} \"")
        
        if esperado and token != esperado:
            raise ValueError(f"Token esperado \" {valor_esperado} \" diferente do token atual \" {token} \"")

        self.pos += 1
        return token
    
    def parse_exp(self):
        """
        Representação da regra de <exp>, sendo ela
            <exp> ::= <exp_or>
        
        Retorna:
            O nó gerado pela regra <exp_or>.
        """
        return self.parse_or()
    
    def parse_or(self):
        """
        Representação da regra de <exp_or>. Processa recursivamente uma 
        expressão or, sendo ela
            <exp_or> ::= <exp_and> (OR <exp_and>)* 
     
        Retorna:
            O nó gerado pelo processamento recursivo.
        """
        no_atual = self.parse_and()
        if no_atual is None:
            return None
        
        while self.token_atual() == "OR":
            self.consome_token("OR")

            no_direita = self.parse_and()
            if no_direita is None:
                raise ValueError("Não existe expressão esperada após OR")
            
            if no_atual is None:
                raise ValueError("Não existe expressão esperada antes de OR")
            
            no_atual = NoParsing("OR", no_atual, no_direita)

        return no_atual
    
    def parse_and(self):
        """
        Representação da regra de <exp_and>. Processa recursivamente uma 
        expressão and, sendo ela
            <exp_and> ::= <exp_not> (AND <exp_not>)*      
        
        Retorna:
            O nó gerado pelo processamento recursivo.
        """
        no_atual = self.parse_not()
        if no_atual is None:
            return None

        while self.token_atual() == "AND":
            self.consome_token("AND")

            no_direita = self.parse_not()
            if no_direita is None:
                raise ValueError("Não existe expressão esperada após AND")
            
            if no_atual is None:
                raise ValueError("Não existe expressão esperada antes de AND")

            no_atual = NoParsing("AND", no_atual, no_direita)

        return no_atual
    
    def parse_not(self):
        """
        Representação da regra de <exp_not>. Processa recursivamente uma 
        expressão not, sendo ela
            <exp_not> ::= NOT <exp_not> | <subexp>   
        
        Retorna:
            O nó gerado pelo processamento recursivo.
        """
        if self.token_atual() == "NOT":
            self.consome_token("NOT")

            if self.token_atual() is None:
                raise ValueError("Não existe expressão esperada após NOT")
            
            no_direita = self.parse_not()
            if no_direita is None:
                raise ValueError("Não existe expressão esperada após NOT")
            
            return NoParsing("NOT", no_direita)

        else:
            return self.parse_subexp()
    
    def parse_subexp(self):
        """
        Representação da regra de <sub_exp>. Processa recursivamente uma 
        sub-expressão. 
            <subexp> ::= "(" <exp> ")" | <palavra> 
            <palavra> ::= (<simbolo> | <digito>)*  
            <simbolo> ::= "a" | "b" | "c" | "d" | "e" | "f" | "g" | "h" | "i" | "j" | "k" | "l" | "m" 
                      | "n" | "o" | "p" | "q" | "r" | "s" | "t" | "u" | "v" | "w" | "x" | "y" | "z"
                      | "-" | "'"
            <digito> ::= "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9" 
        
        Retorna:
            O nó gerado pelo processamento recursivo.
        """

        if self.token_atual() == "(":
            self.consome_token("(")

            if self.token_atual() == ")":
                raise ValueError("Parênteses vazio")

            no_atual = self.parse_exp()

            if no_atual is None:
                raise ValueError("Expressão do parênteses não existe")
            
            if self.token_atual() != ")":
                raise ValueError("Falta de parênteses fechando a expressão")

            self.consome_token(")")

            return no_atual
        
        elif re.match(r"[a-zá-úA-ZÁ-Ú0-9\-'\%\&\$\#\,\£]+$", self.token_atual() or "") and self.token_atual() not in ("AND", "OR", "NOT", "(", ")"):
            palavra = self.consome_token()
            print(f"Token gerado: {self.token_atual()}", flush=True)
            return NoParsing(palavra)
        
        else:
            raise ValueError(f"Token inesperado \" {self.token_atual()} \"")
    
    def gera_parsing_tokens(self):
        """
        Gera a árvore de parsing a partir dos tokens da gramática.
        
        Retorna:
            O nó raiz da árvore de parsing.
        """
        if not self.tokens:
            raise ValueError("Consulta vazia")
        
        self.raiz = self.parse_exp()

        if self.raiz is None:
            print("ERRO: parsing falhou, expressão incompleta ou inválida")

        if self.pos < len(self.tokens):
            print("ERRO: tokens não consumidos")
            self.raiz = None

        return self.raiz
    
    def imprimir_debug(self):
        """
        Imprime o estado atual da consulta e os tokens gerados para fins de depuração.
        """
        print("\n--- DEBUG DA ÁRVORE DE PARSING ---")
        print(f"Consulta Original: {self.query}")
        
        # Verifica se os tokens foram gerados corretamente
        if self.tokens:
            print(f"Número de Tokens: {len(self.tokens)}")
            print(f"Tokens Gerados: {self.tokens}")
        else:
            print("AVISO: Nenhum token foi gerado (query vazia após processamento).")

        # Verifica se a raiz da árvore foi construída
        if self.raiz:
            # O __repr__ de NoParsing deve imprimir a estrutura de forma legível
            print(f"Estrutura da Árvore (Raiz): {self.raiz}") 
        else:
            print("ESTADO: A raiz da árvore ainda não foi construída ou o parsing falhou.")
        print("-----------------------------------")


def processa_arvore_parsing(no : NoParsing, trie_palavras: TrieCompacta, todos_documentos : set):
    """
    Processa uma árvore de Parsing recursivamente, aplicando operações booleanas sobre os 
    termos dos documentos armazenados em uma Trie Compacta.
    
    Parâmetros:
        no (NoParsing): o nó que será processado.
        trie_palavras (TrieCompacta): a trie que armazena todas palavras de todos os arquivos.
        todos_documentos (set): todas tuplas (seção, número) dos arquivos.
    
    Retorna:
        Um set com todos os arquivos que satisfazem a consulta.
    """
    if no is None:
        return set()
    
    if no.operador == "AND":
        return (processa_arvore_parsing(no.esquerda, trie_palavras, todos_documentos) 
                & processa_arvore_parsing(no.direita, trie_palavras, todos_documentos))
    
    elif no.operador == "OR":
        return (processa_arvore_parsing(no.esquerda, trie_palavras, todos_documentos)
                | processa_arvore_parsing(no.direita, trie_palavras, todos_documentos))

    elif no.operador == "NOT":
        return todos_documentos - (processa_arvore_parsing(no.direita, trie_palavras, todos_documentos))
    
    else:
        palavra = no.operador
        lista_invertida_palavra = trie_palavras.busca_palavra(palavra)
        return set(lista_invertida_palavra.keys()) if lista_invertida_palavra else set()


def tem_no_invalido(no):
    """
    Verifica recursivamente se um no é inválido, ou seja, se algum
    de seus filhos é None.
    
    Parâmetros:
        no (NoParsing): o nó a ser verificado.

    Retorna:
        True se for inválido, False caso contrário.
    """
    if no is None:
        return True
    
    if no.operador in ("AND", "OR"):
        return tem_no_invalido(no.esquerda) or tem_no_invalido(no.direita)
    
    if no.operador == "NOT":
        return tem_no_invalido(no.direita)
    
    return False


def arvore_eh_valida(arvore):
    """
    Verifica se uma árvore é válida, isto é, sem raiz nula e sem
    nós inválidos.
    
    Parâmetros:
        arvore (NoParsing): a árvore a ser verificada.

    Retorna:
        True se for válida, ou False caso contrário.
    """
    if arvore is None:
        return False
    
    else: 
        return not tem_no_invalido(arvore)


def realiza_consulta(query, trie_palavras : TrieCompacta, todos_documentos : set):
    """
    Realiza uma consulta de uma query em um conjunto de documentos, 
    por meio de uma trie compacta que armazena todas palavras dos
    documentos e de uma árvore de parsing que processa a query.
    
    Parâmetros:
        query (str): a consulta a ser realizada.
        trie_palavras (TrieCompacta): a trie compacta que tem todas palavras dos documentos.
        todos_documentos (set): conjunto das tuplas (seção, número) de todos os documentos.

    Retorna:
        Conjunto de tuplas (seção, número) de todos os documentos que satisfaçam 
        a consulta ou None caso a consulta seja inválida.
    """
    try:
        parser = ArvoreParsing(query)
        arvore = parser.gera_parsing_tokens()
        parser.imprimir_debug()

        if arvore_eh_valida(arvore):
            documentos = processa_arvore_parsing(arvore, trie_palavras, todos_documentos)
            return documentos, arvore
        else:
            print("ERRO: Árvore de parsing inválida.")
            return set(), None
        
    except ValueError as e:
        print("ERRO de parsing: ", e)
        return set(), None

def _coletar_termos_query(no: 'NoParsing', termos: set = None):
    """
    Percorre a Árvore de Parsing recursivamente, coletando todos os nós que
    representam palavras (termos) e ignorando os nós que representam operadores (AND, OR, NOT).
    
    Parâmetros:
        no (NoParsing): O nó atual a ser processado (começando pela raiz).
        termos (set): O conjunto acumulador de termos únicos.
        
    Retorna:
        Um set de strings contendo todos os termos únicos da consulta.
    """
    if termos is None:
        termos = set()
        
    if no is None:
        return termos
        
    # Verifica se o nó é uma palavra 
    if no.operador not in ("AND", "OR", "NOT"):
        termos.add(no.operador)
        return termos
    
    # Processa o filho da esquerda (para AND e OR)
    _coletar_termos_query(no.esquerda, termos)
    
    # Processa o filho da direita (para AND, OR e NOT)
    _coletar_termos_query(no.direita, termos)
    
    return termos
    
class GerenciadorDeBusca:
    """ Coordena a consulta de forma completa (parsing, busca booleana, cálculo de relevância e formatação)."""
    
    def __init__(self, trie_index: TrieCompacta, todos_documentos: set, caminho_corpus: str, estatisticas_corpus: dict):
        self.trie = trie_index # Referência ao índice invertido
        self.todos_documentos = todos_documentos # Todos os ids de documentos
        self.caminho_corpus = caminho_corpus # Caminho dos dados
        self.estatisticas_corpus = estatisticas_corpus # Dicionário com estatísticas para o cálculo do z-score
        self.mapa_categorias = {c.value: c.name for c in Categoria} # Usado para formatar o doc_id na saída

    def executar_busca(self, query_string: str, num_pagina: int = 1, tamanho_pagina: int = 10):
        """ Executa o ciclo completo da RI e retorna os resultados formatados."""
        
        try:
            # Parsing e busca booleana (retorna ids filtrados e a raiz da árvore)
            documentos_finais_ids, arvore_raiz = realiza_consulta(query_string, self.trie, self.todos_documentos)
            
            if not documentos_finais_ids:
                return []
            
            # Extrai os termos da consulta da árvore
            lista_todos_os_termos = list(_coletar_termos_query(arvore_raiz))

            # Calcula z-scores, relevâncias e termo de foco
            resultados = self._preparar_resultados_para_ordenacao(
                arvore_raiz, documentos_finais_ids, lista_todos_os_termos # Passa a lista
            )
            
            # Inicializa o gerenciador de resultados
            gerenciador = GerenciadorResultados(
                self.caminho_corpus, 
                self.mapa_categorias,
                lista_todos_os_termos 
            )
            
            # Adiciona os resultados calculados para ordenação
            for item in resultados:
                gerenciador.adicionar_resultado(
                    item.doc_id, item.relevancia, item.query_termo, item.caractere_inicial
                )
            
            return gerenciador.obter_pagina_formatada(num_pagina, tamanho_pagina)

        except ValueError as e:
            return [{'id': 'ERRO de Sintaxe', 'score': '0.0000', 'snippet': f'Erro na consulta: {e}'}]
        except Exception as e:
            traceback.print_exc()
            return [{'id': 'ERRO Interno', 'score': 'N/A', 'snippet': f'Falha inesperada na RI: {e}'}]


    def _preparar_resultados_para_ordenacao(self, arvore_raiz: NoParsing, doc_ids: set, lista_todos_os_termos: list):
        """ Calcula a relevância e define o termo/posição de destaque."""
        
        # Busca lista invertida por termo
        lista_tokens_validos = lista_todos_os_termos
        
        if not lista_tokens_validos:
            return [ResultadoItem(doc_id=d, relevancia=0.0, query_termo="", caractere_inicial=0) for d in doc_ids]

        dados_por_doc_id = {}
        
        for termo in lista_tokens_validos:
            lista_invertida_do_termo = self.trie.busca_palavra(termo) 
            stats = self.estatisticas_corpus.get(termo, {"media": 0, "desvio_padrao": 0})
            
            media = stats['media']
            desvio = stats['desvio_padrao']
            
            for doc_id in doc_ids:
                if doc_id in lista_invertida_do_termo:
                    
                    dados = lista_invertida_do_termo[doc_id]
                    freq = dados['frequencia']
                    pos = dados['primeira_posicao']

                    # Cálculo do z-score: (frequência - média) / desvio padrão
                    z_score = (freq - media) / desvio if desvio != 0 else 0 
                    
                    if doc_id not in dados_por_doc_id:
                        dados_por_doc_id[doc_id] = {'termo_scores': []}
                        
                    dados_por_doc_id[doc_id]['termo_scores'].append({
                        'z_score': z_score,
                        'posicao': pos,
                        'termo': termo,
                        'freq': freq
                    })
        
        resultados = []
        
        for doc_id in doc_ids:
            doc_data = dados_por_doc_id.get(doc_id)
            
            if not doc_data or not doc_data['termo_scores']:
                relevancia_final = 0.0
                melhor_termo = lista_tokens_validos[0]
                melhor_posicao = 0
            else:
                # Calcula a média dos z-ccores
                scores = [t['z_score'] for t in doc_data['termo_scores']]
                relevancia_final = sum(scores) / len(scores)
                
                # Encontra o termo com a maior frequência para ser o foco do snippet
                melhor_termo_info = max(doc_data['termo_scores'], key=lambda x: x['freq'])
                melhor_termo = melhor_termo_info['termo']
                melhor_posicao = melhor_termo_info['posicao']

            resultados.append(ResultadoItem(
                doc_id=doc_id, 
                relevancia=relevancia_final, 
                query_termo=melhor_termo, 
                caractere_inicial=melhor_posicao
            ))
            
        return resultados 