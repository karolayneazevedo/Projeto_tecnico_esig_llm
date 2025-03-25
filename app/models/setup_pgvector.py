import psycopg2

def setup_pgvector():
    conn = psycopg2.connect("postgresql://postgres:123@localhost:5432/mydatabase")
    conn.autocommit = True
    cur = conn.cursor()

    try:
        print("🔧 Ativando extensão pgvector...")
        cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")

        print("📦 Verificando se coluna 'embedding_vector' já existe no tipo correto...")
        cur.execute("""
            SELECT data_type
            FROM information_schema.columns
            WHERE table_name = 'chunk_embeddings' AND column_name = 'embedding_vector';
        """)
        result = cur.fetchone()

        if result and result[0] != 'USER-DEFINED':
            print("🧹 Alterando tipo da coluna 'embedding_vector' para vector(1536)...")
            cur.execute("ALTER TABLE chunk_embeddings DROP COLUMN embedding_vector;")
            cur.execute("ALTER TABLE chunk_embeddings ADD COLUMN embedding_vector vector(1536);")
        else:
            print("✅ Coluna já está no tipo correto ou será recriada.")

        print("⚙️ Criando índice ivfflat...")
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_chunk_embedding_vector
            ON chunk_embeddings
            USING ivfflat (embedding_vector vector_cosine_ops)
            WITH (lists = 100);
        """)

        print("✅ Setup pgvector finalizado com sucesso!")

    except Exception as e:
        print(f"❌ Erro durante configuração: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    setup_pgvector()
