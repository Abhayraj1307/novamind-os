import json
import math
import uuid
from pathlib import Path
from typing import List, Dict
from app.core.config import settings
from app.core.openai_client import get_openai_client

DATA_DIR = Path("data")
DATA_DIR.mkdir(parents=True, exist_ok=True)
INDEX_PATH = DATA_DIR / "docs_index.json"

def _load_index() -> List[Dict]:
    if not INDEX_PATH.exists(): return []
    try: return json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    except: return []

def _save_index(data): INDEX_PATH.write_text(json.dumps(data), encoding="utf-8")

def _embed(texts):
    client = get_openai_client()
    resp = client.embeddings.create(model=settings.OPENAI_EMBED_MODEL, input=texts)
    return [d.embedding for d in resp.data]

def index_document(user_id, filename, chunks):
    if not chunks: return 0
    embs = _embed(chunks)
    entries = _load_index()
    entries = [e for e in entries if not (e['user_id'] == user_id and e['filename'] == filename)]
    for t, e in zip(chunks, embs):
        entries.append({"id": str(uuid.uuid4()), "user_id": user_id, "filename": filename, "text": t, "embedding": e})
    _save_index(entries)
    return len(chunks)

def search_docs_for_user(user_id, query, top_k=4):
    entries = [e for e in _load_index() if e['user_id'] == user_id]
    if not entries: return []
    q_emb = _embed([query])[0]
    scored = []
    for e in entries:
        dot = sum(a*b for a,b in zip(q_emb, e['embedding']))
        scored.append((dot, e['text']))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [s[1] for s in scored[:top_k]]