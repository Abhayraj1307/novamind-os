import psutil
import platform
from fastapi import APIRouter

router = APIRouter(tags=["status"])


@router.get("/status/")
def get_status():
    return {
        "status": "OPERATIONAL",
        "ollama_status": "ONLINE",
        "system_info": f"{platform.system()} ({platform.machine()})",
        "cpu_load": f"{psutil.cpu_percent()}%",
        "memory_usage": f"{psutil.virtual_memory().percent}%"
    }
