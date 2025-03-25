from flask import Flask
from flask_cors import CORS
from app.controllers.pdf_controller import pdf_controller
from app.controllers.ask_controller import ask_controller
from app.models.database import init_db
from app.controllers.chat_history_controller import chat_history  # Importando o blueprint chat_history

import logging

# Configurar logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s [%(levelname)s] %(message)s')

app = Flask(__name__)
CORS(app)

# Inicializa o banco de dados
logging.info("🔧 Inicializando o banco de dados...")
init_db()

# Registra os blueprints
app.register_blueprint(pdf_controller, url_prefix="/api")
app.register_blueprint(ask_controller, url_prefix="/api")
app.register_blueprint(chat_history, url_prefix="/api")  # Registrando o blueprint chat_history

if __name__ == "__main__":
    logging.info("🚀 Iniciando servidor Flask na porta 5000...")
    app.run(debug=True, port=5000)
