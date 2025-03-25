# controllers/chat_history_controller.py
from flask import Blueprint, request, jsonify, current_app
from app.services.chat_history_service import insert_chat_history
import psycopg2

chat_history = Blueprint("chat_history", __name__)

# Rota para salvar histórico (POST)
@chat_history.route("/chat_history", methods=["POST"])
def save_chat_history():
    try:
        data = request.get_json()
        current_app.logger.info(f"Dados recebidos: {data}")

        user_question = data["user_question"]
        assistant_answer = data["assistant_answer"]

        insert_chat_history(user_question, assistant_answer)

        return jsonify({"message": "Histórico de chat salvo com sucesso!"}), 200
    except Exception as e:
        current_app.logger.error(f"Erro ao salvar histórico de chat: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Rota para recuperar histórico (GET)
@chat_history.route("/chat_history", methods=["GET"])
def get_chat_history():
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="mydatabase",
            user="postgres",
            password="123"
        )
        cursor = conn.cursor()

        cursor.execute("SELECT user_question, assistant_answer FROM chat_history ORDER BY id ASC;")
        rows = cursor.fetchall()

        history = []
        for row in rows:
            history.append({
                "user_question": row[0],
                "assistant_answer": row[1]
            })

        cursor.close()
        conn.close()

        return jsonify(history), 200
    except Exception as e:
        current_app.logger.error(f"Erro ao buscar histórico: {str(e)}")
        return jsonify({"error": str(e)}), 500
