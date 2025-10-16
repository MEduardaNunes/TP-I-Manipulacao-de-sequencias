# ids dos documentos, relevâncias, snippets
# mergesort 

def mergesort():
    pass

class Resultados:
    def __init__(self, id_doc, relevancia, snippet):
        self.lista_resultados = {}
    
    def insere_lista_resultados(self, chave, z):
        if chave not in self.lista_resultados:
            self.lista_resultados[chave] = {
                "relevancia": z,
                "snippet": ""
            }
        else:
            return
    
    def processa_snippet(): # ir no arquivo original através do id do doc -> parse usando re p/ separa em seção e numero do doc -> acessar arquivo -> salvar 80 caracteres antes e 80 depois da primeira posição (verificar os limites do arquivo)
        pass
    
    def processa_arquivo(caminho_arquivo):
        pass
    
    def ordena_resultados():
        pass
    
    def calcular_relevancia():
        pass
    
    # pra cada doc tem que processar o snippet e calcular a relevancia 