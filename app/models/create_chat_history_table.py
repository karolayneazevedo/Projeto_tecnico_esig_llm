import psycopg2
from psycopg2 import sql

# Função para criar a tabela no banco de dados
def create_table():
    # Conectar ao banco de dados PostgreSQL
    try:
        conn = psycopg2.connect(
            host="localhost",  # Seu host do PostgreSQL
            database="mydatabase",  # Nome do banco de dados correto (mydatabase)
            user="postgres",  # Seu usuário (definido como postgres)
            password="123"  # Sua senha (definida como 123)
        )
        cursor = conn.cursor()
        
        # SQL para criar a tabela
        create_table_query = """
        CREATE TABLE IF NOT EXISTS chat_history (
            id SERIAL PRIMARY KEY,
            user_question TEXT NOT NULL,
            assistant_answer TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        # Executa o comando SQL
        cursor.execute(create_table_query)
        conn.commit()
        print("Tabela 'chat_history' criada com sucesso!")
        
        # Fechar a conexão
        cursor.close()
        conn.close()

    except Exception as error:
        print(f"Erro ao conectar ou criar a tabela: {error}")

if __name__ == "__main__":
    create_table()
