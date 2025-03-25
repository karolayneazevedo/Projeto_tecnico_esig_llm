from flask import Blueprint, request, jsonify
from app.services.pdf_service import process_document  # Função de serviço principal
from app.models.embedding_model import ChunkEmbedding  # Modelo do banco de dados
from app.models.database import SessionLocal  # Sessão de banco de dados

# Inicializa o blueprint do controller
pdf_controller = Blueprint("pdf_controller", __name__)

@pdf_controller.route("/upload_pdf", methods=["POST"])
def upload_pdf():
    """
    Endpoint para fazer upload de PDF ou DOCX, processar e salvar embeddings no banco.
    """
    if "file" not in request.files:
        return jsonify({"error": "Nenhum arquivo enviado."}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "Arquivo não selecionado."}), 400

    # Extensões permitidas
    allowed_extensions = (".pdf", ".docx", ".doc")
    if not file.filename.lower().endswith(allowed_extensions):
        return jsonify({"error": "Formato de arquivo inválido. Envie um PDF ou DOCX."}), 400

    try:
        file_content = file.read()
        filename = file.filename

        # Chama o serviço responsável por processar e armazenar os dados
        response, status_code = process_document(file_content, filename)
        return jsonify(response), status_code

    except Exception as e:
        return jsonify({"error": f"Erro interno no processamento: {str(e)}"}), 500

@pdf_controller.route("/get_embeddings", methods=["GET"])
def get_embeddings():
    """
    Endpoint para retornar todos os embeddings armazenados no banco.
    """
    db = SessionLocal()
    try:
        embeddings = db.query(ChunkEmbedding).all()
        if not embeddings:
            return jsonify({"message": "Nenhum embedding encontrado."}), 200

        response_data = [
            {
                "id": emb.id,
                "chunk_text": emb.chunk_text,
                "embedding_vector": emb.embedding_vector,
                "article_name": emb.article_name,
                "image_path": emb.image_path
            }
            for emb in embeddings
        ]
        return jsonify({"embeddings": response_data}), 200

    except Exception as e:
        return jsonify({"error": f"Erro ao buscar embeddings: {str(e)}"}), 500

    finally:
        db.close()
