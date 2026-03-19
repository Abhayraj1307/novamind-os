from fastapi import APIRouter

router = APIRouter(tags=["history"])


@router.get("/history/")
def history():
    return {"history": []}
