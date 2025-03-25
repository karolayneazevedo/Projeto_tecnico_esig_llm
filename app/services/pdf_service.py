import os
import tempfile
import logging
import shutil
import re
from pathlib import Path
import pdfplumber
from langchain.docstore.document import Document
from langchain_community.document_loaders import UnstructuredWordDocumentLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from app.models.embedding_model import ChunkEmbedding
from app.utils.openai_embeddings import get_openai_embeddings
from app.models.database import SessionLocal
from app.utils.pdf_utils import extract_images_from_pdf

logger = logging.getLogger(__name__)


def clean_text(text):
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\w\s.,;:\-()"\']', '', text)
    return text.strip()


def process_document(file_content, filename):
    db = None
    try:
        suffix = Path(filename).suffix.lower()
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
            tmp_file.write(file_content)
            tmp_path = tmp_file.name

        raw_text = ""
        if suffix == ".pdf":
            with pdfplumber.open(tmp_path) as pdf:
                pages_text = [page.extract_text(x_tolerance=1, y_tolerance=1, layout=True) for page in pdf.pages]
                raw_text = " ".join(filter(None, pages_text))
        elif suffix in [".docx", ".doc"]:
            loader = UnstructuredWordDocumentLoader(tmp_path)
            documents = loader.load()
            raw_text = " ".join([doc.page_content for doc in documents])
        else:
            os.remove(tmp_path)
            return {"message": "Formato de arquivo não suportado."}, 400

        cleaned_full_text = clean_text(raw_text)

        if not cleaned_full_text:
            os.remove(tmp_path)
            logger.warning("⚠️ Nenhum conteúdo válido foi extraído do documento.")
            return {"message": "Nenhum conteúdo extraído."}, 400

        title = cleaned_full_text.split(" ")[:10]
        title = " ".join(title)[:255]
        logger.info(f"📄 Título extraído: {title}")

        preview_lines = cleaned_full_text.split(" ")[:100]
        logger.info("📌 Primeiras linhas do texto extraído:")
        logger.info(" ".join(preview_lines))

        image_map = extract_images_from_pdf(tmp_path, "media/images") if suffix == ".pdf" else {}

        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
        chunks = splitter.split_text(cleaned_full_text)
        valid_chunks = [chunk.strip() for chunk in chunks if len(chunk.strip()) > 50]
        logger.info(f"📎 Total: {len(valid_chunks)} chunks válidos gerados")

        db = SessionLocal()
        saved_count = 0

        for i, chunk in enumerate(valid_chunks):
            embedding = get_openai_embeddings(chunk)
            if embedding:
                image_path = image_map.get(0, [None])[0]  # Considerar a primeira imagem disponível, caso exista
                chunk_entry = ChunkEmbedding(
                    chunk_text=chunk,
                    embedding_vector=embedding,
                    article_name=title,
                    image_path=image_path
                )
                db.add(chunk_entry)
                saved_count += 1
            else:
                logger.warning(f"❌ Erro ao gerar embedding para o chunk {i}.")

        db.commit()
        logger.info(f"✅ Documento '{title}' processado com {saved_count} chunks salvos.")

        return {"message": f"Documento '{title}' processado e salvo com sucesso!"}, 200

    except Exception as e:
        logger.exception(f"❌ Erro durante o processamento do documento: {e}")
        if db:
            db.rollback()
        return {"message": f"Erro ao processar: {str(e)}"}, 500

    finally:
        if db:
            db.close()
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        shutil.rmtree("media/images", ignore_errors=True)