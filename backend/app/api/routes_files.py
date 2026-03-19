from fastapi import APIRouter

router = APIRouter(tags=["files"])


@router.post("/files/upload")
def upload():
    return {"status": "uploaded"}
