from typing import List, Optional
from sqlalchemy.orm import Session

from app import schemas
from app.core import rag, tasks  # <-- your existing files
from app.core.llm_client import chat_with_llm
from app.core.timeline import TimelineBuilder


class Orchestrator:
    """
    Central brain: decides which pipelines to run for a given message.
    """

    def __init__(self, db: Session):
        self.db = db
        self.timeline = TimelineBuilder(db=db)

    def handle_chat(self, payload: schemas.ChatRequest) -> schemas.ChatResponse:
        user_msg = next((m.content for m in payload.messages if m.role == "user"), "").strip()

        intent = self._classify_intent(user_msg, payload)
        self.timeline.add_step("intent_detected", f"Intent classified as '{intent}'.")

        sources: List[schemas.SourceChunk] = []
        new_tasks: List[schemas.Task] = []

        # 1. RAG if requested or obviously doc-related
        answer = None
        if payload.use_rag or intent in ("qa_doc", "study"):
            answer, sources = rag.maybe_answer_with_rag(payload, db=self.db, timeline=self.timeline)

        # 2. Fallback LLM
        if answer is None:
            answer = chat_with_llm(payload, timeline=self.timeline)

        # 3. Planning / tasks (operator mode or planning intent)
        if payload.mode == "operator" or intent in ("plan", "tasks"):
            plan_tasks = tasks.generate_plan_from_goal(payload, db=self.db, timeline=self.timeline)
            extracted = tasks.auto_extract_tasks_from_message(payload, db=self.db, timeline=self.timeline)
            new_tasks = plan_tasks + extracted

        open_tasks = tasks.get_open_tasks_for_user(db=self.db)

        timeline_events = self.timeline.flush()

        return schemas.ChatResponse(
            reply=answer,
            tasks=new_tasks or open_tasks,
            sources=sources,
            timeline=timeline_events,
        )

    def _classify_intent(self, text: str, payload: schemas.ChatRequest) -> str:
        t = text.lower()
        if any(k in t for k in ["summarize my week", "weekly review", "how did i do this week"]):
            return "weekly_review"
        if any(k in t for k in ["plan", "schedule", "deadline", "todo", "tasks"]):
            return "plan"
        if any(k in t for k in ["explain", "help me understand", "what is", "derive"]):
            return "study"
        if any(k in t for k in ["pdf", "doc", "in my notes", "in that file"]):
            return "qa_doc"
        return "generic"
