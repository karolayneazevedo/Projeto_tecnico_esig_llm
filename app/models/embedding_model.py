from sqlalchemy import Column, Integer, String, Text
from app.models.database import Base
from app.models.vector_type import Vector  # importa o novo tipo customizado

class ChunkEmbedding(Base):
    __tablename__ = "chunk_embeddings"

    id = Column(Integer, primary_key=True, index=True)
    chunk_text = Column(Text, nullable=False)
    embedding_vector = Column(Vector, nullable=True)  # agora é vector(1536)
    article_name = Column(String(255), nullable=False)
    image_path = Column(String(255), nullable=True)
