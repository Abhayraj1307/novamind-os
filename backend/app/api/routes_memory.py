from fastapi import APIRouter

router = APIRouter(tags=["memory"])


@router.get("/memory/")
def memory():
    return {"facts": []}
