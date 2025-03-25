from fastapi import APIRouter
from ..controllers.chunk_controller import save_chunk, search_chunks

router = APIRouter()

@router.post("/add_chunk/")
def add_chunk(text: str, article_name: str):
    chunk_id = save_chunk(text, article_name)
    return {"message": "Chunk salvo!", "id": chunk_id}

@router.get("/search_chunks/")
def search_chunks_route(query: str, top_k: int = 5):
    results = search_chunks(query, top_k)
    return {"results": results}
