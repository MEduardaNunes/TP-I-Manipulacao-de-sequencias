import traceback
import os

def _ler_conteudo_documento(doc_id, caminho_corpus, mapa_categorias):
    """Lê o conteúdo do arquivo correspondente ao doc_id"""
    try:
        categoria_int, numero_int = doc_id
        categoria_nome = mapa_categorias.get(categoria_int)
        if not categoria_nome: return None
        numero_str = f"{numero_int:03d}"
        nome_arquivo = f"{numero_str}.txt"
        caminho_arquivo = os.path.join(caminho_corpus, categoria_nome, nome_arquivo)
        with open(caminho_arquivo, 'r', encoding='latin-1') as f:
            return f.read()
    except (FileNotFoundError, IOError):
        print(f"[Erro Snippet] Arquivo não encontrado: {caminho_arquivo}")
        return None
    except Exception as e:
        print(f"[Erro Snippet] Erro inesperado ao ler {caminho_arquivo}: {e}")
        return None
        
def _calcular_limites_snippet(tamanho_conteudo, indice_caractere_inicial, len_termo):
    """Calcula os índices [inicio, fim) do snippet"""
    # Define o início do snippet 80 caracteres antes do termo, limitado a 0
    inicio = max(0, indice_caractere_inicial - 80)
        
    # Define o fim do snippet 80 caracteres depois do fim do termo, limitado ao tamanho do conteúdo
    fim = min(tamanho_conteudo, indice_caractere_inicial + len_termo + 80)
        
    return inicio, fim   
    
def _destacar_termo_no_snippet(snippet_texto, termo):
    """Envolve a primeira ocorrência do termo com <b>"""
    # Procura a posição do termo no snippet ignorando maiúsculas/minúsculas
    pos_termo_lower = snippet_texto.lower().find(termo.lower())
        
    # Se o termo for encontrado dentro do snippet
    if pos_termo_lower != -1:
        # Extrai o termo como ele aparece no snippet (preserva maiúsculas/minúsculas)
        termo_encontrado = snippet_texto[pos_termo_lower : pos_termo_lower + len(termo)]
        # Constrói a string do snippet com a tag <b> envolvendo o termo
        snippet_destacado = (
            snippet_texto[:pos_termo_lower] +
            f"<b>{termo_encontrado}</b>" +
            snippet_texto[pos_termo_lower + len(termo):]
        )
        return snippet_destacado
    else:
        return snippet_texto 
        
def _gerar_snippet_formatado(doc_id, termo, indice_caractere_inicial, caminho_corpus, mapa_categorias):
    """
    Função principal que gera um snippet formatado. O termo é destacado com a tag <b>.
    """
    try:
        conteudo = _ler_conteudo_documento(doc_id, caminho_corpus, mapa_categorias)
        if conteudo is None:
            return "[Erro na leitura do documento]"

        # Verifica se o índice fornecido é válido
        if not (0 <= indice_caractere_inicial < len(conteudo)):
            print(f"[Aviso Snippet] Índice {indice_caractere_inicial} inválido para {doc_id}. Usando find().")
            indice_caractere_inicial = conteudo.lower().find(termo.lower())
        else:
            # Checa se o termo realmente começa no índice fornecido
            termo_no_conteudo = conteudo[indice_caractere_inicial : indice_caractere_inicial + len(termo)]
            if termo_no_conteudo.lower() != termo.lower():
                print(f"[Aviso Snippet] Termo '{termo}' não na posição {indice_caractere_inicial} de {doc_id}. Conteúdo: '{termo_no_conteudo}'. Usando find().")
                indice_alternativo = conteudo.lower().find(termo.lower())
                if indice_alternativo != -1:
                    indice_caractere_inicial = indice_alternativo

        if indice_caractere_inicial == -1:
            return "[Termo não encontrado no documento para snippet]"

        # Calcula limites, extrai e destaca o termo
        inicio_snippet, fim_snippet = _calcular_limites_snippet(len(conteudo), indice_caractere_inicial, len(termo))
        snippet_texto = conteudo[inicio_snippet:fim_snippet]
        snippet_destacado = _destacar_termo_no_snippet(snippet_texto, termo)

        # Adiciona elipse se o snippet não começar no início do documento ou se não terminar no fim do documento
        prefixo = "... " if inicio_snippet > 0 else ""
        sufixo = " ..." if fim_snippet < len(conteudo) else ""
        
        return prefixo + snippet_destacado + sufixo

    except Exception as e:
        print(f"Erro inesperado em _gerar_snippet_formatado para {doc_id}, termo '{termo}':")
        traceback.print_exc()
        return "[Erro interno ao gerar snippet]"