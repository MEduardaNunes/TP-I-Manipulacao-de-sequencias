from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')

def pagina_inicial():
    return render_template('index.html', titulo="Máquina de busca")
