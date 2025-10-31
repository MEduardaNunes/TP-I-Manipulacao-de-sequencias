# TP-I-Manipulacao-de-sequencias
# TP-I-Manipulacao-de-sequencias

Este é um protótipo funcional de uma máquina de busca que utiliza conceitos de indexação de documentos com árvores de prefixo (Trie Compacta) e consulta booleana. O sistema é capaz de processar consultas utilizando os operadores AND, OR e NOT, e exibe os resultados em uma interface web desenvolvida com Flask. A relevância dos documentos é calculada com base nos z-scores dos termos das consultas.

## Requisitos

- Python 3.9+
- Dependências listadas em `requirements.txt`

## Estrutura do Projeto

O projeto é composto pelos seguintes módulos:

- **Trie Compacta**: Implementação da estrutura Trie Compacta para indexação de palavras nos documentos.
- **Indexer**: Responsável pela construção e manutenção do índice invertido.
- **Consulta (Search)**: Processamento das consultas booleanas e interação com a Trie para recuperação dos documentos relevantes.
- **Interface (Flask)**: Uma interface web para realizar as consultas e exibir os resultados com snippets dos documentos.
- **Gerenciador de Resultados**: Organiza, classifica e exibe os resultados de forma paginada.

## Como Rodar

### Passo 1: Configurar o Ambiente Virtual

Crie um ambiente virtual e instale as dependências do projeto:

```bash
make install
```
Isso irá criar um ambiente virtual na pasta env e instalar as dependências listadas no arquivo requirements.txt.

### Passo 2: Configurar o ambiente virtual
Inicie o servidor Flask para rodar a aplicação:
```bash
make run
```
O servidor estará disponível localmente para que você possa testar o sistema de busca.

### Passo 3: Limpar o projeto
Para limpar arquivos temporários e caches, execute:
```bash
make clean
```
Isso removerá o índice salvo e os arquivos temporários.