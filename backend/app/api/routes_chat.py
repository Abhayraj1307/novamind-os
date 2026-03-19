from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional

from app.core.rag import answer_with_rag_stream

router = APIRouter(tags=["chat"])


class ChatRequest(BaseModel):
    user_id: str
    message: str
    mode: str = "operator"
    chat_id: Optional[str] = None
    image: Optional[str] = None


@router.post("/chat_stream/")
def chat_stream_endpoint(payload: ChatRequest):
    generator = answer_with_rag_stream(
        payload.user_id,
        payload.message,
        payload.mode,
        payload.chat_id,
        payload.image
    )
    return StreamingResponse(generator, media_type="text/event-stream")
