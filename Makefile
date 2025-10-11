PYTHON = python3

VENV_DIR = env

install: requirements.txt
	@echo "Criando ambiente virtual em '$(VENV_DIR)'..."
	$(PYTHON) -m venv $(VENV_DIR)
	@echo "Instalando dependências de requirements.txt..."
	./$(VENV_DIR)/bin/pip install -r requirements.txt
	@echo "Instalação concluída!"

run:
	@echo "Iniciando o servidor Flask... (Pressione Ctrl+C para parar)"
	./$(VENV_DIR)/bin/python app.py

index:
	@echo "Executando o script de indexação..."
	./$(VENV_DIR)/bin/python indexer.py

clean:
	@echo "--> Removendo ambiente virtual e arquivos de cache..."
	rm -rf $(VENV_DIR)
	rm -rf saved_index
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} +
	@echo "--> Limpeza concluída."