from openai import OpenAI
import os
from dotenv import load_dotenv

# Carrega a chave da API do arquivo .env
load_dotenv()

# Carrega a chave da OpenAI
load_dotenv()
client = OpenAI(api_key="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")

# Texto de teste
texto = "A inteligência artificial está transformando o mundo."

try:
    # Gerar embedding
    response = client.embeddings.create(
        model="text-embedding-ada-002",
        input=texto
    )
    embedding = response.data[0].embedding

    print(f"✅ Embedding gerado com sucesso! Vetor com {len(embedding)} dimensões.")
    print("🔹 Primeiros valores:", embedding[:10])

except Exception as e:
    print(f"❌ Erro ao gerar embedding: {e}")
# Função para obter embeddings com OpenAI (API v1+)
def get_openai_embeddings(text, model="text-embedding-ada-002"):
    """
    Gera embeddings para um texto usando o modelo da OpenAI.

    Parameters:
    text (str): Texto para gerar embedding
    model (str): Nome do modelo (default: text-embedding-ada-002)

    Returns:
    list: Vetor de embedding ou None se falhar
    """
    try:
        response = client.embeddings.create(
            model=model,
            input=text
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"Erro ao obter embeddings: {e}")
        return None