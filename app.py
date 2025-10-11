from flask import Flask, render_template
from modules.Indexer import criar_indice
import os

app = Flask(__name__)

@app.route('/')

def pagina_inicial():
    return render_template('index.html', titulo="Máquina de busca")

if __name__ == '__main__':
    caminho_relativo = './bbc'
    caminho_corpus = os.path.abspath(os.path.join(os.path.dirname(__file__), caminho_relativo))
    
    print(f"Caminho do corpus definido como: {caminho_corpus}")
    
    indice = criar_indice(caminho_corpus)
    
    if indice:
        indice.imprimir_arvore()
        print("\n--- SUCESSO: O índice foi criado e contém dados. ---")
    else:
        print("FALHA: O índice não foi criado.")