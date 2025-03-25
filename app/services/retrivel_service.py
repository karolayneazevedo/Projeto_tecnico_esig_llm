import logging
from sqlalchemy import text
from app.utils.openai_embeddings import get_openai_embeddings

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def retrieve_relevant_chunks(query, db, k=30):
    try:
        embedding_query = get_openai_embeddings(query)
        if embedding_query is None:
            logger.error("❌ Falha ao gerar embedding da query.")
            return []

        embedding_str = str(embedding_query)

        # Nova consulta SQL melhorada
        sql = text("""
            SELECT 
                article_name,
                chunk_text AS full_text,
                image_path,
                1 - (embedding_vector <-> CAST(:embedding_str AS vector)) AS score
            FROM chunk_embeddings
            WHERE chunk_text IS NOT NULL AND LENGTH(chunk_text) > 50
            ORDER BY embedding_vector <-> CAST(:embedding_str AS vector)
            LIMIT :k;
        """)

        results = db.execute(sql, {
            'embedding_str': embedding_str,
            'k': k
        }).fetchall()

        result_list = []
        for row in results:
            if not row[1] or not row[1].strip():
                logger.warning(f"⚠️ Chunk vazio encontrado em '{row[0]}', ignorando...")
                continue

            result_dict = {
                "article_name": row[0],
                "full_text": row[1],
                "image_path": row[2],
                "score": row[3]
            }
            result_list.append(result_dict)
            logger.debug(f"📦 Chunk válido recuperado: {row[0]} | Texto inicial: {row[1][:100]}...")

        logger.info(f"✅ {len(result_list)} chunks relevantes encontrados.")
        return result_list

    except Exception as e:
        logger.exception(f"❌ Erro crítico ao recuperar chunks: {str(e)}")
        return []
