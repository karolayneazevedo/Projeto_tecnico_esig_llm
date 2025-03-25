from fastapi import APIRouter
from ..controllers.chat_controller import save_chat, get_chat_history

router = APIRouter()

@router.post("/add_chat/")
def add_chat(user_message: str, assistant_response: str):
    chat_id = save_chat(user_message, assistant_response)
    return {"message": "Histórico salvo!", "id": chat_id}

@router.get("/chat_history/")
def chat_history(limit: int = 20):
    history = get_chat_history(limit)
    return {"history": history}
