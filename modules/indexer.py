from TrieCompacta import TrieCompacta, NoTrie
from .utils import ListaLigada, processar_texto
from .models import Documento, Categoria
import os
import math
import re

def parse_linha_trie(linha):
    """
    Parse de uma linha do arquivo de índice da trie

    Parâmetros:
        linha (str): a string da linha a ser analisada. Ex: "('ad',{(1, 23):...})"

    Retorno:
        Uma tupla (valor, lista_invertida_dict) com os dados extraídos.
    """
    linha = linha.strip()

    # Extrai a string do nó (encontra o conteúdo entre as primeiras aspas simples)
    valor_encontrado = re.search(r"^\('([^']*)',", linha)
    if not valor_encontrado:
        # Lida com o caso da raiz, que é '(,{})'
        if linha == "(,{})":
            return "", {}
        raise ValueError(f"Formato de linha inválido, não foi possível encontrar o valor: {linha}")
    
    valor = valor_encontrado.group(1) 
    lista_invertida_dict = {}
    
    # Encontra todas as ocorrências de "(cat, num): {'freq': f, 'pos': p}"
    padrao_ocorrencia = re.compile(r"\((\d+), (\d+)\): \{'frequencia': (\d+), 'primeira_posicao': (\d+)\}")

    # Encontra todas as correspondências na string
    for match in padrao_ocorrencia.finditer(linha):
        cat_str, num_str, freq_str, pos_str = match.groups()
        
        # Converte as strings capturadas para inteiros
        chave = (int(cat_str), int(num_str))
        dados = {
            "frequencia": int(freq_str),
            "primeira_posicao": int(pos_str)
        }
        lista_invertida_dict[chave] = dados

    return valor, lista_invertida_dict

class Corpus:
    def __init__(self):
            """Inicializa um objeto com uma trie vazia e um dicionário de estatísticas vazio"""
            self.trie = TrieCompacta()
            self.estatisticas_corpus = {}  # Formato: {"termo": {"media": x, "desvio_padrao": y}}  
    
    def construir_indice(self, caminho_corpus):
        """
        Método responsável por fazer o processo de indexação (lê documentos, calcula estatísticas e preenche a trie)
        
        Parâmetros:
            caminho_corpus (str): O caminho para o diretório raiz do corpus de documentos
        """
    
        documentos = self._ler_documentos(caminho_corpus)
        total_docs = len(documentos)
        
        if total_docs == 0:
            print("[DEBUG] A lista de documentos está vazia. A indexação não pode continuar.")
            return
        
        # Dicionário temporário para armazenar as frequências de cada termo por documento
        frequencias_por_doc = {} # Formato: {'business/001': {'trade': 5, 'market': 3}, ...}
        lista_de_frequencias_por_termo = {} # Formato: {'trade': [5, 0, 2, ...], 'market': [3, 1, 0, ...]}
        
        for doc in documentos:
            doc_id_completo = f"{doc.categoria}/{doc.doc_id}" # Cria um id único para cada doc (ex: 'business/001')
            frequencias_por_doc[doc_id_completo] = {}

            # Normalização do texto
            termos_com_posicao = processar_texto(doc.conteudo)
            for termo, indice_char in termos_com_posicao:
                # Preenche o dicionário de frequências do doc atual
                frequencias_por_doc[doc_id_completo][termo] = frequencias_por_doc[doc_id_completo].get(termo, 0) + 1
                
                # Converte os identificadores do doc para inteiros
                categoria_int = Categoria[doc.categoria].value
                numero_int = int(doc.doc_id)
                
                # Insere o termo, o id do documento e a primeira posição de ocorrência do termo na trie Compacta
                self.trie.insere_palavra(termo, (categoria_int, numero_int), indice_char)
        
        todos_os_termos = set(termo for freqs in frequencias_por_doc.values() for termo in freqs)        
        
        # Calcula a média e o desvio padrão de cada termo
        for termo in todos_os_termos:
            lista_de_frequencias_por_termo[termo] = []
            for doc_id in frequencias_por_doc:
                freq = frequencias_por_doc[doc_id].get(termo, 0)
                lista_de_frequencias_por_termo[termo].append(freq)
                
        for termo, freqs in lista_de_frequencias_por_termo.items():
            soma_freq = 0
            
            for freq in freqs:
                soma_freq += freq
                
            media = soma_freq / total_docs
            
            if total_docs > 1:
                variancia = 0
                soma_das_diferencas_quadradas = 0 
                
                for freq in freqs:
                    soma_das_diferencas_quadradas += (freq - media) ** 2
                
                variancia = soma_das_diferencas_quadradas / (total_docs - 1)
                desvio_padrao = math.sqrt(variancia)
            else:
                desvio_padrao = 0
                
            self.estatisticas_corpus[termo] = {
                "media": media,
                "desvio_padrao": desvio_padrao
            }
    
    def _ler_documentos(self, caminho_corpus):
        documents = ListaLigada()
        
        for categoria in os.listdir(caminho_corpus):
            caminho_categoria = os.path.join(caminho_corpus, categoria)
            if os.path.isdir(caminho_categoria):
                for nome_arquivo in os.listdir(caminho_categoria):
                    if nome_arquivo.endswith('.txt'):
                        doc_id_num = nome_arquivo[:-4]
                        caminho_arquivo = os.path.join(caminho_categoria, nome_arquivo)
                        try:
                            with open(caminho_arquivo, 'r', encoding='latin-1') as f:
                                conteudo = f.read()
                            doc = Documento(categoria, doc_id_num, conteudo)
                            documents.adicionar(doc)
                        except Exception as e:
                            print(f"Erro ao ler o arquivo {caminho_arquivo}: {e}")
        
        return documents
    
    def carregar_de_disco(self, caminho_arquivo):
        """
        Carrega o índice (trie e estatísticas) de um arquivo de texto
        """
        print(f"[DEBUG] Carregando o índice de '{caminho_arquivo}'...")
        try:
            with open(caminho_arquivo, 'r', encoding='utf-8') as f:
                linhas = f.readlines()
                
                try:
                    indice_estatisticas = linhas.index("--ESTATISTICAS--\n")
                    indice_trie = linhas.index("--TRIE--\n")
                except ValueError:
                    raise ValueError("Arquivo de índice corrompido: marcadores de seção não encontrados.")

                # Processa as estatísticas
                for i in range(indice_estatisticas + 1, indice_trie):
                    linha = linhas[i].strip()
                    if not linha: continue
                    termo, estatisticas_str = linha.split(':', 1)
                    media_str, desvio_str = estatisticas_str.split(',')
                    self.estatisticas_corpus[termo] = {
                        "media": float(media_str),
                        "desvio_padrao": float(desvio_str)
                    }

                self.trie = TrieCompacta()
                pilha_de_pais = [self.trie.raiz] # pilha com os nós
                
                for i in range(indice_trie + 2, len(linhas)):
                    linha = linhas[i]
                    if not linha.strip(): continue

                    profundidade_atual = (len(linha) - len(linha.lstrip(' '))) // 2
                    valor, lista_invertida_dict = parse_linha_trie(linha)

                    novo_no = NoTrie(valor)
                    novo_no.lista_invertida = lista_invertida_dict

                    while len(pilha_de_pais) > profundidade_atual:
                        pilha_de_pais.pop()
                    
                    # O pai é o último nó que sobrou na pilha
                    pai_no = pilha_de_pais[-1]
                    pai_no.insere_filho(novo_no)
                    
                    # Adiciona o novo nó à pilha
                    pilha_de_pais.append(novo_no)
                
            print("[DEBUG] Índice carregado com sucesso.")
            return True
        except FileNotFoundError:
            print("[DEBUG] Arquivo de índice não encontrado. Um novo será criado.")
            return False
        except Exception as e:
            print(f"Erro ao carregar o índice: {e}")
            return False
        
    def salvar_em_disco(self, caminho_arquivo):
        """
        Salva o índice (trie e estatísticas) em um arquivo de texto
        """
        print(f"[DEBUG] Salvando o índice em '{caminho_arquivo}'...")
        try:
            with open(caminho_arquivo, 'w', encoding='utf-8') as f:
                f.write("---ESTATISTICAS---\n")
                for termo, stats in self.estatisticas_corpus.items():
                    media = stats['media']
                    desvio = stats['desvio_padrao']
                    f.write(f"{termo}:{media},{desvio}\n")

                f.write("---TRIE---\n")
                self._salvar_no_recursivo(f, self.trie.raiz, 0)
            
            print("[DEBUG] Índice salvo com sucesso.")
        except IOError as e:
            print(f"Erro ao salvar o índice: {e}")
    
    def _formatar_lista_invertida(self, lista_invertida):
        """
        Converte o dicionário da lista invertida para uma string
        """
        if not lista_invertida:
            return "{}"

        partes = []
        for chave, dados in lista_invertida.items():
            cat, num = chave
            freq = dados["frequencia"]
            pos = dados["primeira_posicao"]
            
            # Constrói a string para um item do dicionário em um formato definido
            parte_str = f"({cat}, {num}):{{'frequencia':{freq}, 'primeira_posicao':{pos}}}"
            partes.append(parte_str)
        
        conteudo_interno = ", ".join(partes)
        return f"{{{conteudo_interno}}}"
    
    def _salvar_no_recursivo(self, arquivo, NoTrie, profundidade):
        """
        Método auxiliar recursivo para salvar os nós da trie
        """
        # Indentação para representar a estrutura da árvore
        indentacao = "  " * profundidade
        
        lista_invertida_str = self._formatar_lista_invertida(NoTrie.lista_invertida)
        
        # faz com que o valor do nó seja escrito com aspas (ex: 'ad')
        valor_str = repr(NoTrie.valor)

        # Escreve o nó NoTrie arquivo: indentação, valor e sua lista invertida
        arquivo.write(f"{indentacao}({valor_str},{lista_invertida_str})\n")
        
        for filho in NoTrie.filhos:
            self._salvar_no_recursivo(arquivo, filho, profundidade + 1)         
    
    # PARA DEBUG
    def imprimir_estatisticas(self, limite=10):
        """
        Imprime as estatísticas do corpus de forma legível para debugging.

        Parâmetros:
            limite (int): O número máximo de termos a serem impressos.
                          Útil para não poluir a tela com milhares de linhas.
        """
        print("\n--- Estatísticas do Corpus ---")
        if not self.estatisticas_corpus:
            print("(Nenhuma estatística calculada)")
            return
        
        count = 0
        for termo, stats in self.estatisticas_corpus.items():
            if count >= limite:
                print(f"\n... e mais {len(self.estatisticas_corpus) - limite} termos.")
                break
            
            media = stats['media']
            desvio = stats['desvio_padrao']
            
            print(f"- Termo: '{termo}'")
            print(f"    Média de Frequência: {media:.4f}")
            print(f"    Desvio Padrão: {desvio:.4f}")
            
            count += 1
                                
                    

    
   
