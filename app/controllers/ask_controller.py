from flask import Blueprint, request, jsonify
from app.services.Generate_service import generate_answer
import logging

ask_controller = Blueprint("ask_controller", __name__)

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@ask_controller.route("/ask", methods=["POST"])
def ask_question():
    try:
        data = request.get_json()
        question = data.get("question", "")
        logger.info(f"📩 Pergunta recebida: {question}")

        if not question:
            logger.warning("❗ Nenhuma pergunta recebida no corpo da requisição.")
            return jsonify({"error": "Pergunta não fornecida."}), 400

        answer = generate_answer(question)
        logger.info("✅ Resposta gerada com sucesso.")
        return jsonify({"answer": answer})

    except Exception as e:
        logger.exception(f"❌ Erro ao processar a pergunta: {str(e)}")
        return jsonify({"error": "Erro interno ao processar a pergunta."}), 500
