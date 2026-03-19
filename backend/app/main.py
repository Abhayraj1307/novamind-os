from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from app.db.database import engine, Base

from app.api.routes_chat import router as chat_router
from app.api.routes_auth import router as auth_router
from app.api.routes_files import router as files_router
from app.api.routes_tasks import router as tasks_router
from app.api.routes_status import router as status_router
from app.api.routes_memory import router as memory_router
from app.api.routes_history import router as history_router


Base.metadata.create_all(bind=engine)

app = FastAPI(title="NovaMind OS")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Routers
app.include_router(chat_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1/auth")
app.include_router(files_router, prefix="/api/v1")
app.include_router(tasks_router, prefix="/api/v1")
app.include_router(status_router, prefix="/api/v1")
app.include_router(memory_router, prefix="/api/v1")
app.include_router(history_router, prefix="/api/v1")

# Frontend
app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.get("/")
async def read_index():
    return FileResponse("app/static/index.html")


@app.get("/health")
def health():
    return {"status": "online", "system": "NovaMind Titan"}
