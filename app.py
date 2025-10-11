from flask import Flask, render_template, request, session, redirect, url_for
from modules.Indexer import criar_indice
import os

app = Flask(__name__)
app.secret_key = "senha_super_secreta"

resposta = None

@app.route('/', methods=['GET', 'POST'])
def home():
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
    caminho_relativo = './bbc'
    caminho_corpus = os.path.abspath(os.path.join(os.path.dirname(__file__), caminho_relativo))
    
    print(f"Caminho do corpus definido como: {caminho_corpus}")
    
    indice = criar_indice(caminho_corpus)
    
    if indice:
        indice.imprimir_arvore()
        print("\n--- SUCESSO: O índice foi criado e contém dados. ---")
    else:
        print("FALHA: O índice não foi criado.")

    app.run(debug=True)