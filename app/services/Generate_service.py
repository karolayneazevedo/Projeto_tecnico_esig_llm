import os
import time
import requests
import logging
from dotenv import load_dotenv
from app.services.chat_history_service import insert_chat_history
from app.models.database import SessionLocal
from app.services.retrivel_service import retrieve_relevant_chunks

# Carrega variáveis de ambiente
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_BASE_URL = "https://api.openai.com/v1"

# Configuração de logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


def get_openai_embeddings(query: str):
    try:
        if not OPENAI_API_KEY:
            logger.error("❌ OPENAI_API_KEY não está configurada.")
            return None

        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }

        body = {
            "model": "text-embedding-ada-002",
            "input": query
        }

        response = requests.post(f"{OPENAI_BASE_URL}/embeddings", headers=headers, json=body)

        if response.status_code != 200:
            logger.error(f"❌ Erro ao obter embedding da OpenAI: {response.text}")
            return None

        return response.json()["data"][0]["embedding"]

    except requests.exceptions.RequestException as req_err:
        logger.error(f"❌ Erro na requisição para OpenAI: {req_err}")
        return None
    except Exception as e:
        logger.exception(f"❌ Erro inesperado ao obter embedding: {e}")
        return None


def build_prompt(context_text: str, query: str) -> str:
    return f"""
Você é um assistente da OpenAI especializado em responder perguntas com base em documentos fornecidos.
Responda apenas com base nesse conteúdo.
Se a resposta não estiver claramente no contexto, diga explicitamente:
"Não posso responder com base nos dados fornecidos."

Contexto:
{context_text}

Pergunta: {query}
Resposta:
""".strip()


def generate_answer(query: str, context_chunks: list = []) -> str:
    try:
        start_time = time.time()

        if not OPENAI_API_KEY:
            logger.error("❌ OPENAI_API_KEY não está configurada.")
            return "Erro: API Key da OpenAI não está configurada."

        logger.info(f"🔎 Gerando resposta para a pergunta: '{query}'")

        db = SessionLocal()

        embedding_query = get_openai_embeddings(query)
        if embedding_query is None:
            logger.warning("⚠️ Não foi possível gerar embedding para a consulta.")
            return "Desculpe, não consegui processar a consulta."

        relevant_chunks = retrieve_relevant_chunks(query, db, k=10)
        if not relevant_chunks:
            logger.warning("⚠️ Nenhum documento relevante encontrado.")
            return "Desculpe, não encontrei informações suficientes para responder à sua pergunta."

        MAX_CONTEXT_CHARS = 65000
        context_parts = []
        total_chars = 0

        for doc in relevant_chunks:
            part = doc["full_text"].strip()
            if not part:
                continue
            if total_chars + len(part) > MAX_CONTEXT_CHARS:
                break
            context_parts.append(part)
            total_chars += len(part)

        if not context_parts:
            logger.warning("⚠️ Todos os chunks recuperados estavam vazios.")
            return "Desculpe, os documentos encontrados não contêm informações úteis para responder à sua pergunta."

        context_text = "\n\n".join(context_parts)
        article_titles = [doc["article_name"] for doc in relevant_chunks if doc["full_text"].strip() in context_parts]
        article_titles = list(dict.fromkeys(article_titles))

        logger.info(f"📚 Contexto preparado com {len(context_parts)} documentos.")
        logger.info(f"📦 Tamanho do contexto: {len(context_text)} caracteres")

        prompt = build_prompt(context_text, query)

        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }

        body = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,
            "max_tokens": 500
        }

        response = requests.post(f"{OPENAI_BASE_URL}/chat/completions", headers=headers, json=body)

        if response.status_code != 200:
            logger.error(f"❌ Erro {response.status_code} na chamada OpenAI: {response.text}")
            return "Erro ao gerar resposta com a OpenAI (veja detalhes no log)."

        output = response.json()["choices"][0]["message"]["content"].strip()

        resposta_padrao = "Não posso responder com base nos dados fornecidos."

        if resposta_padrao.lower() not in output.lower():
            if article_titles:
                fontes = "\n\n📚 **Fonte(s):**\n" + "\n".join(f"- {title}" for title in article_titles)
                output += fontes

        insert_chat_history(query, output)
        return output

    except requests.exceptions.RequestException as req_err:
        logger.error(f"❌ Erro na requisição para OpenAI: {req_err}")
        return "Erro: Problema ao se conectar com o servidor OpenAI."
    except Exception as e:
        logger.exception(f"❌ Erro inesperado ao gerar resposta: {e}")
        return "Erro ao gerar resposta com base no contexto."
    finally:
        if 'db' in locals():
            db.close()
