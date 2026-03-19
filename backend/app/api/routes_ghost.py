from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.core.ghost import run_ghost_loop

router = APIRouter(tags=["ghost"])

class GhostRequest(BaseModel):
    objective: str

@router.post("/ghost/run")
async def run_ghost(payload: GhostRequest):
    """
    Triggers the Autonomous GUI Agent.
    WARNING: This will take control of the server's mouse/keyboard.
    """
    try:
        result = run_ghost_loop(payload.objective)
        return {"status": "success", "report": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))