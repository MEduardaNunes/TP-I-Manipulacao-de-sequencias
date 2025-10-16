# ids dos documentos, relevâncias, snippets
class Resultados:
    def __init__(self, id_doc, relevancia, snippet):
        self.id_doc = id_doc
        self.relevancia = relevancia
        self.snippet = snippet
    
    def processa_snippet(): # ir no arquivo original através do id do doc -> parse usando re p/ separa em seção e numero do doc -> acessar arquivo -> salvar 80 caracteres antes e 80 depois da primeira posição (verificar os limites do arquivo)
        pass
    
    def processa_arquivo(caminho_arquivo):
        pass
    
    def ordena_resultados():
        pass
    
    def calcular_relevancia():
        pass
    
    # pra cada doc tem que processar o snippet e calcular a relevancia 