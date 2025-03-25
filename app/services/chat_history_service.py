import psycopg2
from psycopg2 import sql

def insert_chat_history(user_question, assistant_answer):
    try:
        conn = psycopg2.connect(
            host="localhost",  # Seu host do PostgreSQL
            database="mydatabase",  # Nome do banco de dados
            user="postgres",  # Seu usuário do PostgreSQL
            password="123"  # Sua senha do PostgreSQL
        )
        cursor = conn.cursor()

        # SQL para inserir os dados na tabela
        insert_query = """
        INSERT INTO chat_history (user_question, assistant_answer)
        VALUES (%s, %s);
        """
        cursor.execute(insert_query, (user_question, assistant_answer))
        conn.commit()

        # Fechar a conexão
        cursor.close()
        conn.close()
    except Exception as error:
        raise Exception(f"Erro ao inserir no banco de dados: {error}")
