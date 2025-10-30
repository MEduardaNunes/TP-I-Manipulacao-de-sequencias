PYTHON = python3
LOG_FILE = debug_log.txt
VENV_DIR = env

create_log:
	@echo "Criando ou limpando o arquivo de log: $(LOG_FILE)"
	@echo "Logs de execução:" > $(LOG_FILE)


install: requirements.txt
	@echo "Criando ambiente virtual em '$(VENV_DIR)'..."
	$(PYTHON) -m venv $(VENV_DIR)
	@echo "Instalando dependências de requirements.txt..."
	./$(VENV_DIR)/bin/pip install -r requirements.txt
	@echo "Instalação concluída!"

run:
	@echo "Iniciando o servidor Flask... (Pressione Ctrl+C para parar)" | tee -a $(LOG_FILE)
	./$(VENV_DIR)/bin/python app.py | tee -a $(LOG_FILE)

clean:
	rm -rf saved_index
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -f data/indice.dat
	@echo "--> Limpeza concluída." | tee -a $(LOG_FILE)