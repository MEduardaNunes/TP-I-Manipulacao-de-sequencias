from flask import Flask, render_template, request, session, redirect, url_for
from modules.indexer import Corpus 
from modules.resultados import GerenciadorResultados
from modules.models import Categoria
from modules.search import ArvoreParsing, arvore_eh_valida, realiza_consulta
from modules.utils import normaliza_query
import os
import traceback

app = Flask(__name__)
app.secret_key = "senha_super_secreta"

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

@app.route('/', methods=['GET'])
def home(): 
    """Página inicial com o formulário de busca."""
    session.permanent = False
    if 'historico' not in session:
        session['historico'] = []

    return render_template('index.html')   

@app.route('/search', methods=['GET', 'POST'])
def search_results():
    """Rota para processar a busca e exibir os resultados."""
    global corpus_index
    session.permanent = False
    
    if 'historico' not in session:
        session['historico'] = []

    resultados = []
    termo = None
    
    if request.method == 'POST':
        termo = request.form.get('mensagem')
        
        if termo:
            if termo not in session['historico']:
                session['historico'].append(termo)
                session['historico'] = session['historico'][-10:]
                session.modified = True
            
            return redirect(url_for('search_results', termo=termo))
        else:
            return redirect(url_for('home'))
    
    elif request.method == 'GET':
        termo = request.args.get('termo')
    
    if termo and corpus_index and corpus_index.estatisticas_corpus:
        
        mapa_reverso_categoria = {c.value: c.name for c in Categoria}
        caminho_corpus = os.path.abspath(os.path.join(os.path.dirname(__file__), './bbc'))
        
        try:
            todos_documentos = corpus_index.trie.get_todos_doc_ids()
            resultados_ids = realiza_consulta(termo, corpus_index.trie, corpus_index.todos_documentos)
            
            if(resultados_ids != None):
                gerenciador = GerenciadorResultados(caminho_corpus, mapa_reverso_categoria)
                
                relevancia_final = 0
                
                # Adiciona os resultados encontrados à lista formatada
                for doc_id in resultados_ids:
                    gerenciador.adicionar_resultado(
                        doc_id,
                        relevancia_final,
                        termo,  # Termo que foi pesquisado
                        0  # Caractere inicial 
                    )
                    
                resultados = gerenciador.obter_pagina_formatada(num_pagina=1, tamanho_pagina=10)
            else:
                print("Consulta inválida")
                
        except Exception as e:
            print(f"Erro durante o processamento da busca para '{termo}': {e}")
            traceback.print_exc()
            resultados = [{'id': 'ERRO', 'score': 'N/A', 'snippet': f'Falha na busca: {e}'}]
            
    return render_template('search_results.html', termo=termo, resultados=resultados)

@app.route('/historico', methods=['GET', 'POST'])
def historico():
    session.permanent = False
    if 'historico' not in session:
        session['historico'] = []

    if request.method == 'POST':
        termo = request.form['mensagem']
        return redirect(url_for('search_results', termo = termo))

    return render_template('historico.html', historico = session['historico'])

if __name__ == '__main__':
    inicializar_indice()
    
    if corpus_index and corpus_index.estatisticas_corpus:
        mapa_reverso_categoria = {c.value: c.name for c in Categoria}
        if hasattr(corpus_index, 'trie'): 
            print("\nDEBUG: Imprimindo amostra da Trie")
            corpus_index.trie.imprimir_arvore(mapa_categorias=mapa_reverso_categoria, limite=5)
    app.run(debug=True)