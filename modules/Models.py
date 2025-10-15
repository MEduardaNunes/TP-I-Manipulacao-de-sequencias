from enum import Enum

class Categoria(Enum):
    business = 1
    entertainment = 2
    politics = 3
    sport = 4
    tech = 5    
         
class Document:
    def __init__(self, categoria, doc_id, conteudo):
        self.categoria = categoria
        self.doc_id = doc_id
        self.conteudo = conteudo
    
    def __repr__(self):
        return f"Documento(id={self.doc_id}, categoria='{self.categoria}')"

