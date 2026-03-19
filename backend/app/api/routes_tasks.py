from fastapi import APIRouter

router = APIRouter(tags=["tasks"])


@router.get("/tasks/")
def tasks():
    return {"tasks": []}
