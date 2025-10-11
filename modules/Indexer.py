import os
from TrieCompacta import TrieCompacta, No
from .Utils import ListaLigada

class Document:
    def __init__(self, categoria, doc_id, conteudo):
        self.categoria = categoria
        self.doc_id = doc_id
        self.conteudo = conteudo
    
    def __repr__(self):
        return f"Documento(id={self.doc_id}, categoria='{self.categoria}')"
    
def ler_corpus(caminho_corpus):
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
                        doc = Document(categoria, doc_id_num, conteudo)
                        documents.adicionar(doc)
                    except Exception as e:
                        print(f"Erro ao ler o arquivo {caminho_arquivo}: {e}")
    
    print(f"Leitura concluída. Total de {len(documents)} documentos encontrados.") # pra debugar
    return documents

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
                                
                    
def criar_indice(caminho_corpus):
    trie = TrieCompacta()
    
    print("[DEBUG] Função 'criar_indice' iniciada. Chamando 'ler_corpus'...")
    documents = ler_corpus(caminho_corpus)
    
    if not documents:
        print("[DEBUG] A lista de documentos está vazia. A indexação não pode continuar.")
        return trie # Retorna a Trie vazia
    
    for doc in documents:
        doc_id_completo = f"{doc.categoria}/{doc.doc_id}"
        print(f"Indexando documento: {doc_id_completo}", flush=True) # pra debugar
        
        palavras = processar_texto(doc.conteudo)
        for posicao, palavra in enumerate(palavras):
            trie.insere(palavra, doc_id_completo, posicao)
            
    return trie
    
    