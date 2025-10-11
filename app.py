from flask import Flask, render_template
from modules import criar_indice

from enum import Enum

class Categoria(Enum):
    business = 1
    entertainment = 2
    politics = 3
    sport = 4
    tech = 5

app = Flask(__name__)

@app.route('/')

def pagina_inicial():
    return render_template('index.html', titulo="Máquina de busca")

if __name__ == '__main__':
    caminho_corpus = './bbc'
    
    indice = criar_indice(caminho_corpus)
    
    if indice:
        indice.imprimir_arvore()
    else:
        print("FALHA: O índice não foi criado.")