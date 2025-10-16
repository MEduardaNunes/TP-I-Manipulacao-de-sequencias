from flask import Flask, render_template, request, session, redirect, url_for
from modules.indexer import Corpus 
from modules.resultados import Resultados
from modules.models import Categoria
import os

app = Flask(__name__)
app.secret_key = "senha_super_secreta"

resposta = None
corpus_index = None

def inicializar_indice():
    global corpus_index
    caminho_indice_salvo = "data/indice.dat" 
    
    corpus_index = Corpus()
    
    if os.path.exists(caminho_indice_salvo) and corpus_index.carregar_de_disco(caminho_indice_salvo):
        print("SUCESSO: O índice foi carregado do arquivo")
    else:
        caminho_relativo = './bbc'
        caminho_corpus = os.path.abspath(os.path.join(os.path.dirname(__file__), caminho_relativo))

        if not os.path.exists(caminho_corpus):
            print(f"Diretório do corpus não encontrado em '{caminho_corpus}'")
            return

        corpus_index.construir_indice(caminho_corpus)
        
        if corpus_index.estatisticas_corpus:
            print("\nSUCESSO: O índice foi criado e carregado na memória") # DEBUG
            corpus_index.imprimir_estatisticas(limite=10)
            os.makedirs(os.path.dirname(caminho_indice_salvo), exist_ok=True)
            corpus_index.salvar_em_disco(caminho_indice_salvo)
        else:
            print("\nFALHA: O índice não pôde ser criado. Verifique os logs") # DEBUG

@app.route('/', methods=['GET', 'POST'])
def home(): # talvez receber como parametro um objeto da classe consulta e armazenar a query direto nele pra usar no main
    session.permanent = False
    if 'historico' not in session:
        session['historico'] = []

    resposta = None
    termo = None

    if request.method == 'POST':
        termo = request.form['mensagem']

    elif request.args.get('termo'):
        termo = request.args.get('termo')

    if termo:
        caminho = 'bbc/business/001.txt'
        with open(caminho, 'r') as file:
            conteudo = file.read()
        resposta = f"Resultado para: {termo}\n\n{conteudo}"

        if termo not in session['historico']:
            session['historico'].append(termo)
            session['historico'] = session['historico'][-10:]
            session.modified = True

    return render_template('index.html', resposta=resposta)

@app.route('/historico', methods=['GET', 'POST'])
def historico():
    session.permanent = False
    if 'historico' not in session:
        session['historico'] = []

    resposta = None

    if request.method == 'POST':
        termo = request.form['mensagem']
        session['historico'].append(termo)
        session.modified = True

        return redirect(url_for('home', termo = termo))

    return render_template('historico.html', resposta = resposta, historico = session['historico'])

if __name__ == '__main__':
    inicializar_indice()
    
    if corpus_index and corpus_index.estatisticas_corpus:
        mapa_reverso_categoria = {c.value: c.name for c in Categoria}
        
        corpus_index.trie.imprimir_arvore(mapa_categorias=mapa_reverso_categoria, limite=5)
    else:
        print("FALHA: nao foi possível imprimir a árvore")

    app.run(debug=True)