import numpy as np
from sqlalchemy.orm import Session
from sentence_transformers import SentenceTransformer
from ..models.database import SessionLocal
from ..models.models import Chunk

# Criando o modelo de embeddings
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# 📌 Função para salvar chunks e seus embeddings no banco
def save_chunk(text: str, article_name: str):
    session = SessionLocal()
    embedding = model.encode(text).tolist()  # Gera embedding
    new_chunk = Chunk(text=text, embedding=embedding, article_name=article_name)
    session.add(new_chunk)
    session.commit()
    session.refresh(new_chunk)
    session.close()
    return new_chunk.id

# 📌 Função para buscar chunks mais relevantes
def search_chunks(query: str, top_k: int = 5):
    session = SessionLocal()
    query_embedding = model.encode(query).tolist()
    
    # Busca por similaridade usando pgvector
    result = session.execute(
        f"SELECT text, article_name FROM chunks ORDER BY embedding <-> ARRAY{query_embedding} LIMIT {top_k};"
    )
    
    session.close()
    return [{"text": row[0], "article_name": row[1]} for row in result.fetchall()]
