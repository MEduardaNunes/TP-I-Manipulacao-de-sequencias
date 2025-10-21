import traceback
import os
import re

def _ler_conteudo_documento(doc_id, caminho_corpus, mapa_categorias):
    """Lê o conteúdo do arquivo correspondente ao doc_id"""
    caminho_arquivo = None
    
    try:
        # Converte id do documento em caminho de arquivo (Ex: 1, 003 -> business/003.txt)
        categoria_int, numero_int = doc_id
        categoria_nome = mapa_categorias.get(categoria_int)
        if not categoria_nome: return None
        numero_str = f"{numero_int:03d}"
        nome_arquivo = f"{numero_str}.txt"
        caminho_arquivo = os.path.join(caminho_corpus, categoria_nome, nome_arquivo)
        with open(caminho_arquivo, 'r', encoding='latin-1') as f:
            return f.read()
    except (FileNotFoundError, IOError):
        info_erro = caminho_arquivo if caminho_arquivo else str(doc_id)
        print(f"[Erro Snippet] Arquivo não encontrado: {info_erro}")
        return None
    except Exception as e:
        info_erro = caminho_arquivo if caminho_arquivo else str(doc_id)
        print(f"[Erro Snippet] Erro inesperado ao ler {info_erro}: {e}")
        return None
        
def _calcular_limites_snippet(tamanho_conteudo, indice_caractere_inicial, len_termo):
    """Calcula os índices do snippet"""
    # Define o início do snippet 80 caracteres antes do termo (limitado a 0)
    inicio = max(0, indice_caractere_inicial - 80)
        
    # Define o fim do snippet 80 caracteres depois do fim do termo (limitado ao tamanho do conteúdo)
    fim = min(tamanho_conteudo, indice_caractere_inicial + len_termo + 80)
        
    return inicio, fim   
    
def _destacar_termos_no_snippet(snippet_texto, termos_validos_query: list):
    """ Envolve todas as ocorrências de todos os termos válidos com <b> """
    
    texto_modificado = snippet_texto
    
    # Cria um conjunto único de termos em minúsculas 
    termos_para_destaque = {t.lower() for t in termos_validos_query if t and len(t) > 0}
        
    # Itera sobre cada termo válido para destacá-lo
    for termo in termos_para_destaque:
        try:
            # Cria a expressão regular para buscar a palavra inteira
            pattern = r'\b(' + re.escape(termo) + r')\b'
            
            # Adiciona o <b>
            def replace_match(match):
                return f"<b>{match.group(1)}</b>"

            # Aplica a substituição em todo o texto
            texto_modificado = re.sub(pattern, replace_match, texto_modificado, flags=re.IGNORECASE)
            
        except re.error:
            continue

    return texto_modificado
        
def _gerar_snippet_formatado(doc_id, termo_em_foco, indice_caractere_inicial, caminho_corpus, mapa_categorias, termos_validos):
    """ Função principal que gera um snippet formatado. O snippet é centralizado no termo_em_foco, mas destaca todos os termos válidos da query. """
    try:
        conteudo = _ler_conteudo_documento(doc_id, caminho_corpus, mapa_categorias)
        if conteudo is None:
            return "[Erro na leitura do documento]"

        tamanho_termo_em_foco = len(termo_em_foco)
        
        if not (0 <= indice_caractere_inicial < len(conteudo)):
            # Se o índice falhar tenta encontrar o termo em foco na força bruta
            indice_alternativo = conteudo.lower().find(termo_em_foco.lower())
            print(f"[Aviso Snippet] Índice {indice_caractere_inicial} inválido. Usando find() para {indice_alternativo}.")
            indice_caractere_inicial = indice_alternativo
        else:
            # Checa se o termo realmente começa no índice fornecido
            termo_no_conteudo = conteudo[indice_caractere_inicial : indice_caractere_inicial + tamanho_termo_em_foco]
            if termo_no_conteudo.lower() != termo_em_foco.lower():
                indice_alternativo = conteudo.lower().find(termo_em_foco.lower())
                if indice_alternativo != -1:
                    indice_caractere_inicial = indice_alternativo

        if indice_caractere_inicial == -1:
            return "[Termo de foco não encontrado no documento]"

        # Calcula limites, extrai e destaca o termo
        inicio_snippet, fim_snippet = _calcular_limites_snippet(len(conteudo), indice_caractere_inicial, tamanho_termo_em_foco)
        snippet_texto = conteudo[inicio_snippet:fim_snippet]

        snippet_destacado = _destacar_termos_no_snippet(snippet_texto, termos_validos)
        
        # Adiciona elipse se o snippet não começar no início do documento ou se não terminar no fim do documento
        prefixo = "... " if inicio_snippet > 0 else ""
        sufixo = " ..." if fim_snippet < len(conteudo) else ""
        
        return prefixo + snippet_destacado + sufixo

    except Exception as e:
        print(f"Erro inesperado em _gerar_snippet_formatado para {doc_id}, termo foco '{termo_em_foco}':")
        traceback.print_exc()
        return "[Erro interno ao gerar snippet]"