from langchain.text_splitter import RecursiveCharacterTextSplitter

def chunk_text(text, chunk_size=512, overlap=30):
    if not text.strip():
        return []
    print(f"🔹 Processando chunking do texto... (tamanho: {len(text)} caracteres)")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap,
        separators=["\n\n", "\n", ". ", " "]  # Priorizando quebras naturais
    )
    return splitter.split_text(text)
