import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# 1. Carrega as variáveis de ambiente
load_dotenv()

# 2. Lê a variável do .env
DATABASE_URL = os.getenv("DATABASE_URL")

# 3. Cria o engine
engine = create_engine(DATABASE_URL, echo=True)

# 4. Cria sessão e base
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 5. Inicializador do banco
def init_db():
    from app.models.embedding_model import ChunkEmbedding  # importa o modelo
    from sqlalchemy import text

    with engine.connect() as conn:
        print("🔧 Ativando extensão pgvector (se necessário)...")
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        conn.commit()

    Base.metadata.create_all(bind=engine)
    print("✅ Tabelas criadas com sucesso!")
