from flask import Flask, render_template, request, session, redirect, url_for
from modules.indexer import Corpus 
from modules.resultados import GerenciadorResultados
from modules.models import Categoria
from modules.search import realiza_consulta, GerenciadorDeBusca
import os
import traceback

app = Flask(__name__)
app.secret_key = "senha_super_secreta"

corpus_index = None
gerenciador_de_busca = None

def inicializar_indice():
    global corpus_index, gerenciador_de_busca
    caminho_indice_salvo = "data/indice.dat" 
    caminho_relativo = './bbc'
    caminho_corpus = os.path.abspath(os.path.join(os.path.dirname(__file__), caminho_relativo))

    corpus_index = Corpus()
    indice_carregado_ou_construido = False
    
    if os.path.exists(caminho_indice_salvo) and corpus_index.carregar_de_disco(caminho_indice_salvo):
        print("SUCESSO: O índice foi carregado do arquivo")
        indice_carregado_ou_construido = True
    else:
        if not os.path.exists(caminho_corpus):
            print(f"Diretório do corpus não encontrado em '{caminho_corpus}'")
            return

        corpus_index.construir_indice(caminho_corpus)
        
        if corpus_index.estatisticas_corpus:
            print("\nSUCESSO: O índice foi criado e carregado na memória") # DEBUG
            corpus_index.imprimir_estatisticas(limite=10)
            os.makedirs(os.path.dirname(caminho_indice_salvo), exist_ok=True)
            corpus_index.salvar_em_disco(caminho_indice_salvo)
            indice_carregado_ou_construido = True
        else:
            print("\nFALHA: O índice não pôde ser criado. Verifique os logs") # DEBUG

    if indice_carregado_ou_construido:
        try:
            todos_documentos = corpus_index.todos_documentos 
            
            gerenciador_de_busca = GerenciadorDeBusca(
                trie_index=corpus_index.trie,
                todos_documentos=todos_documentos,
                caminho_corpus=caminho_corpus,
                estatisticas_corpus=corpus_index.estatisticas_corpus
            )
            print("SUCESSO: Gerenciador de Busca inicializado e pronto para a busca.")
            
        except Exception as e:
            print(f"[ERRO FATAL] Falha ao criar GerenciadorDeBusca: {e}")
            traceback.print_exc()
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
    global gerenciador_de_busca
    session.permanent = False
    
    if 'historico' not in session:
        session['historico'] = []

    resultados = []
    termo = None
    num_pagina = 1 
    tamanho_pagina_fixo = 10
    tem_proxima_pagina = False
    
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
        
        try:
            num_pagina = int(request.args.get('page', 1))
            if num_pagina < 1:
                num_pagina = 1
        except ValueError:
            num_pagina = 1
    
    if termo and gerenciador_de_busca:
        try:
            resultados = gerenciador_de_busca.executar_busca(termo, num_pagina=num_pagina, tamanho_pagina=tamanho_pagina_fixo)
            
            if resultados is None: 
                resultados = [{'id': 'ERRO', 'score': 'N/A', 'snippet': 'Consulta inválida (erro de parsing).'} ]
            
            tem_proxima_pagina = len(resultados) == tamanho_pagina_fixo
        except Exception as e:
            print(f"Erro durante o processamento da busca para '{termo}': {e}")
            traceback.print_exc()
            tem_proxima_pagina = False
            resultados = [{'id': 'ERRO', 'score': 'N/A', 'snippet': f'Falha na busca: {e}'}]
    else:
        tem_proxima_pagina = False
        tamanho_pagina_fixo = 10
        
    return render_template ('search_results.html', termo=termo, resultados=resultados,num_pagina=num_pagina, tamanho_pagina=tamanho_pagina_fixo, tem_proxima_pagina=tem_proxima_pagina)

@app.route('/historico', methods=['GET', 'POST'])
def historico():
    session.permanent = False
    if 'historico' not in session:
        session['historico'] = []

    if request.method == 'POST':
        termo = request.form['mensagem']
        return redirect(url_for('search_results', termo = termo))

    return render_template('historico.html', historico = session['historico'])

@app.route('/ajuda')
def ajuda():
    return render_template('ajuda.html')

if __name__ == '__main__':
    inicializar_indice()
    
    if corpus_index and corpus_index.estatisticas_corpus:
        from modules.search import ArvoreParsing # debug
        consulta_teste = "apple AND banana OR (car AND NOT ship)" # debug
        
        try:
            parser_teste = ArvoreParsing(consulta_teste)
            parser_teste.gera_parsing_tokens()
            
            print("\n====================================")
            print("TESTE MANUAL: DEBUG ÁRVORE DE PARSING")
            parser_teste.imprimir_debug() # AQUI ESTÁ A CHAMADA
            print("====================================")

            resultado_a = corpus_index.trie.busca_palavra("a")
            print(f"Resultado da busca por 'a': {resultado_a}")
        except Exception as e:
            print(f"Erro ao testar o parsing: {e}")
            
        #mapa_reverso_categoria = {c.value: c.name for c in Categoria}
        #if hasattr(corpus_index, 'trie'): 
            #rint("\nDEBUG: Imprimindo amostra da Trie")
            #corpus_index.trie.imprimir_arvore(mapa_categorias=mapa_reverso_categoria, limite=5)
    app.run(debug=True)