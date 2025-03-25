from flask import request, jsonify

# Função para processar perguntas
def process_question(question):
    # Simulação de resposta (essa lógica pode ser ajustada para usar IA ou busca)
    response = f"Resposta simulada para a pergunta: '{question}'"
    return response

def ask():
    data = request.get_json()
    question = data.get("question")
    
    if not question:
        return jsonify({"error": "No question provided"}), 400

    # Processar a pergunta (essa parte pode ser expandida para integrar IA ou modelos de NLP)
    answer = process_question(question)

    return jsonify({"answer": answer})
