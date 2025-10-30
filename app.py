from flask import Flask, render_template, request, session, redirect, url_for, abort
from modules.indexer import Corpus 
from modules.resultados import GerenciadorResultados
from modules.models import Categoria
from modules.search import GerenciadorDeBusca
import os
import traceback

app = Flask(__name__)
app.secret_key = "senha_super_secreta"

corpus_index = None
gerenciador_de_busca = None
caminho_corpus = None

def inicializar_indice():
    """
    Carrega o índice do disco ou o constrói se não existir.
    Inicializa as variáveis globais que a aplicação usará.
    """
    global corpus_index, caminho_corpus, mapa_categorias_reverso, gerenciador_de_busca
    caminho_indice_salvo = "data/indice.dat" 
    caminho_relativo = './bbc'
    
    # Define o caminho absoluto para o corpus
    caminho_corpus = os.path.abspath(os.path.join(os.path.dirname(__file__), caminho_relativo))

    corpus_index = Corpus()
    indice_carregado_ou_construido = False
    
    # Tenta carregar o índice do disco
    if os.path.exists(caminho_indice_salvo) and corpus_index.carregar_de_disco(caminho_indice_salvo):
        print("O índice foi carregado do arquivo")
        indice_carregado_ou_construido = True
    else:
        # Se falhar constrói o índice
        if not os.path.exists(caminho_corpus):
            print(f"ERRO: Diretório do corpus não encontrado em '{caminho_corpus}'")
            return

        corpus_index.construir_indice(caminho_corpus)
        
        if corpus_index.estatisticas_corpus:
            print("\nO índice foi criado e carregado na memória") 
            os.makedirs(os.path.dirname(caminho_indice_salvo), exist_ok=True)
            corpus_index.salvar_em_disco(caminho_indice_salvo)
            indice_carregado_ou_construido = True
        else:
            print("\nERRO: O índice não pôde ser criado. Verifique os logs") 

    # Se o índice estiver pronto inicializa o Gerenciador de Busca
    if indice_carregado_ou_construido:
        try:
            todos_documentos = corpus_index.todos_documentos 
            
            gerenciador_de_busca = GerenciadorDeBusca(
                trie_index=corpus_index.trie,
                todos_documentos=todos_documentos,
                caminho_corpus=caminho_corpus,
                estatisticas_corpus=corpus_index.estatisticas_corpus
            )      
        except Exception as e:
            print(f"[ERRO] Falha ao criar GerenciadorDeBusca: {e}")
            traceback.print_exc()
@app.before_request
def inicializar_sessao():
    """Executa antes de cada rota para garantir que o histórico exista."""
    session.permanent = False
    if 'historico' not in session:
        session['historico'] = []
                    
@app.route('/', methods=['GET'])
def home(): 
    """Página inicial com o formulário de busca."""
    return render_template('index.html')   

@app.route('/search', methods=['GET', 'POST'])
def search_results():
    """Rota para processar a busca e exibir os resultados."""
    global gerenciador_de_busca
    
    resultados_pagina = []
    termo = None
    pagina_atual = 1
    tamanho_pagina_fixo = 10
    tem_proxima_pagina = False
    
    if request.method == 'POST':
        termo = request.form.get('mensagem')
        
        if termo:
            # Adiciona ao histórico (limitado a 10)
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
            pagina_atual = int(request.args.get('page', 1))
            if pagina_atual < 1:
                pagina_atual = 1
        except ValueError:
            pagina_atual = 1
            
    # Se tivermos um termo e o gerenciador estiver pronto, executa a busca
    if termo and gerenciador_de_busca:
        try:
            retorno_busca = gerenciador_de_busca.executar_busca(
                termo, 
                num_pagina=pagina_atual, 
                tamanho_pagina=tamanho_pagina_fixo
            )
            resultados_pagina = retorno_busca
            
            if resultados_pagina is None: 
                resultados_pagina = [{'id': 'ERRO', 'score': 'N/A', 'snippet': 'Consulta inválida (erro de parsing).'} ]
                tem_proxima_pagina = False
            elif not resultados_pagina and pagina_atual > 1:
                print(f"[INFO Busca] Página {pagina_atual} vazia para '{termo}', redirecionando para página 1.")
                return redirect(url_for('search_results', termo=termo, page=1))
            else:
                # Verifica se há mais resultados
                tem_proxima_pagina = len(resultados_pagina) == tamanho_pagina_fixo
        except Exception as e:
            print(f"Erro durante o processamento da busca para '{termo}': {e}")
            traceback.print_exc()
            resultados_pagina = [{'id_completo': 'ERRO Interno', 'categoria':'','id_num':'', 'score': 'N/A', 'snippet': f'Falha na busca: {e}'}]
            tem_proxima_pagina = False
        
    return render_template (
        'search_results.html',
        termo=termo,
        resultados=resultados_pagina,
        pagina_atual=pagina_atual,         
        tem_proxima_pagina=tem_proxima_pagina 
    )

@app.route('/historico', methods=['GET', 'POST'])
def historico():
    """Exibe o histórico de buscas e permite nova busca a partir dele."""
    
    if 'historico' not in session:
        session['historico'] = []

    if request.method == 'POST':
        termo = request.form['mensagem']
        return redirect(url_for('search_results', termo = termo))

    return render_template('historico.html', historico = session['historico'])

@app.route('/documento/<categoria>/<id_documento>', methods=['GET'])
def exibir_documento(categoria, id_documento):
    """Exibe o conteúdo de um documento específico."""
    global caminho_corpus

    # Verifica se a categoria é válida
    categorias_validas = [c.name for c in Categoria]
    if categoria not in categorias_validas:
        print(f"ERRO: Categoria inválida '{categoria}'")
        abort(404, "Documento não encontrado.")

    # Verifica se o id é completamente numérico
    if not id_documento.isdigit():
        print(f"ERRO: id de documento inválido '{id_documento}'")
        abort(404, "Documento não encontrado.")
    
    id_formatado = f"{int(id_documento):03d}" 
    nome_arquivo = f"{id_formatado}.txt"
    
    caminho_arquivo = os.path.join(caminho_corpus, categoria, nome_arquivo)
    
    caminho_absoluto_corpus = os.path.abspath(caminho_corpus)
    caminho_absoluto_arquivo = os.path.abspath(caminho_arquivo)
    
    if not os.path.exists(caminho_arquivo):
        print(f"ERRO: Arquivo não encontrado em {caminho_arquivo}") # DEBUG
        return f"Documento não encontrado: {categoria}/{id_documento}", 404
    
    with open(caminho_arquivo, 'r', encoding='latin-1') as f:
        conteudo = f.read()
            
    documento = {
        'categoria': categoria, 
        'id': id_formatado, 
        'conteudo': conteudo
    }
    return render_template('exibir_documento.html', documento=documento)

@app.route('/ajuda')
def ajuda():
    """Exibe a página de ajuda."""
    return render_template('ajuda.html')

if __name__ == '__main__':
    inicializar_indice()
     
    if gerenciador_de_busca:    
        app.run(debug=False) 
    else:
        print("ERRO: Gerenciador de busca não foi inicializado.")
        print("O servidor Flask não será iniciado.")