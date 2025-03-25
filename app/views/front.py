import streamlit as st
import requests
from datetime import datetime

st.set_page_config(page_title="Assistente RAG", layout="wide")

menu = st.sidebar.radio("Navegação", ["Chat com Assistente", "Upload de Arquivos"])

API_BASE_URL = "http://localhost:5000/api"

if menu == "Upload de Arquivos":
    st.title("Upload de Arquivos")
    uploaded_files = st.file_uploader(
        "Escolha arquivos (PDF, DOCX, TXT)", 
        type=["pdf", "docx", "txt"], 
        accept_multiple_files=True
    )

    if uploaded_files:
        for file in uploaded_files:
            st.success(f"📁 Arquivo {file.name} enviado com sucesso.")
            file_content = file.read()

            with st.spinner(f"⏳ Processando o arquivo {file.name}..."):
                response = requests.post(
                    f"{API_BASE_URL}/upload_pdf",
                    files={"file": (file.name, file_content)}
                )

            if response.status_code == 200:
                st.success(f"✅ PDF {file.name} processado e salvo no banco com sucesso!")
            else:
                st.error(f"❌ Erro ao processar o PDF {file.name}: {response.text}")

elif menu == "Chat com Assistente":
    st.title("Assistente RAG ESIG")

    if "chat_history" not in st.session_state:
        try:
            response = requests.get(f"{API_BASE_URL}/chat_history")
            if response.status_code == 200:
                history = response.json()
                st.session_state.chat_history = [
                    {
                        "question": h["user_question"],
                        "answer": h["assistant_answer"],
                        "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                    }
                    for h in history
                ]
            else:
                st.session_state.chat_history = []
                st.warning("⚠️ Não foi possível carregar o histórico salvo.")
        except Exception as e:
            st.session_state.chat_history = []
            st.error(f"❌ Erro ao carregar histórico: {e}")

    col1, col2 = st.columns([1, 3])

    with col1:
        st.subheader("Histórico")
        for chat in reversed(st.session_state.chat_history):
            st.markdown(f"**Pergunta:** {chat['question']}")
            st.markdown(f"**Resposta:** {chat['answer']}")
            st.caption(chat["timestamp"])
            st.markdown("---")

    with col2:
        st.subheader("")

        if st.session_state.chat_history:
            last_chat = st.session_state.chat_history[-1]
            st.markdown("### Pergunta")
            st.write(last_chat["question"])
            st.markdown("### Resposta")
            st.write(last_chat["answer"])
        else:
            st.info("💬 Envie sua primeira pergunta para começar!")

        with st.form(key="chat_form", clear_on_submit=True):
            user_input = st.text_input("Digite sua pergunta aqui...", value="", label_visibility="collapsed")
            submit_button = st.form_submit_button("Enviar")  # Botão padrão ajustado aqui

            if submit_button and user_input.strip():
                with st.spinner("🧠 Processando sua pergunta..."):
                    response = requests.post(
                        f"{API_BASE_URL}/ask",
                        json={"question": user_input}
                    )

                if response.status_code == 200:
                    answer = response.json().get("answer", "Resposta vazia")
                else:
                    answer = "Erro ao obter resposta do assistente."

                chat_entry = {
                    "question": user_input,
                    "answer": answer,
                    "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                }

                st.session_state.chat_history.append(chat_entry)

                requests.post(
                    f"{API_BASE_URL}/chat_history",
                    json={
                        "user_question": user_input,
                        "assistant_answer": answer
                    }
                )

                st.rerun()
