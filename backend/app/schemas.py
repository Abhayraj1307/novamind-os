from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    user_id: str = "user"
    messages: List[ChatMessage] = []
    mode: str = "operator"
    use_rag: bool = False
    chat_id: Optional[str] = None
    image: Optional[str] = None


class Task(BaseModel):
    id: Optional[str] = None
    title: str = ""
    status: str = "open"
    due_date: Optional[str] = None


class SourceChunk(BaseModel):
    id: Optional[str] = None
    title: Optional[str] = None
    content: Optional[str] = None
    score: Optional[float] = None


class TimelineEvent(BaseModel):
    id: Optional[str] = None
    step: str
    description: str
    created_at: datetime


class ChatResponse(BaseModel):
    reply: str
    tasks: List[Task] = []
    sources: List[SourceChunk] = []
    timeline: List[TimelineEvent] = []
