from sqlalchemy import create_engine, text
from app.models.database import Base, DATABASE_URL
from app.models.embedding_model import ChunkEmbedding  # Corrigido!
from sqlalchemy.orm import sessionmaker

# Criar engine e sessão
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

print("🔧 Ativando extensão pgvector (se necessário)...")
with engine.connect() as conn:
    conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
    conn.commit()

# Criar as tabelas
Base.metadata.create_all(bind=engine)
print("✅ Tabelas criadas com sucesso!")

# Criar índice vetorial ivfflat se não existir
with engine.connect() as conn:
    print("⚡ Criando índice vetorial ivfflat (se necessário)...")
    conn.execute(text("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM pg_indexes
                WHERE tablename = 'chunk_embeddings' AND indexname = 'ix_chunk_embeddings_vector'
            ) THEN
                CREATE INDEX ix_chunk_embeddings_vector
                ON chunk_embeddings
                USING ivfflat (embedding_vector vector_cosine_ops)
                WITH (lists = 100);
            END IF;
        END
        $$;
    """))
    conn.commit()
    print("✅ Índice vetorial criado com sucesso!")
