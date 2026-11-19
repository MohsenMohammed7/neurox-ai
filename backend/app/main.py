import os
import sqlite3
import uuid
from contextlib import contextmanager
from pathlib import Path
from typing import Optional

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(title="NeuroX AI API", version="0.3.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = os.getenv("NEUROX_DB_PATH", str(Path(__file__).resolve().parent.parent / "data" / "neurox.db"))


@contextmanager
def connect_db():
    path = Path(DB_PATH)
    path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path, timeout=15)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys = ON")
    try:
        yield db
    finally:
        db.close()


def init_db():
    with connect_db() as db:
        db.executescript("""
            CREATE TABLE IF NOT EXISTS conversations (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id TEXT NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
                role TEXT NOT NULL CHECK(role IN ('user', 'assistant')),
                content TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE INDEX IF NOT EXISTS idx_messages_conversation
                ON messages(conversation_id, id);
        """)


@app.on_event("startup")
async def startup():
    init_db()


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=20000)
    conversation_id: Optional[str] = None


def get_ai_reply(message: str):
    api_key = os.getenv("AI_API_KEY", "").strip()
    if not api_key:
        return (
            "وصلت رسالتك إلى خادم NeuroX AI وتم حفظها. لتفعيل الردود الذكية، "
            "أضف AI_API_KEY وAI_MODEL إلى متغيرات البيئة.",
            "setup_required",
            None,
        )

    base_url = os.getenv("AI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
    model = os.getenv("AI_MODEL", "gpt-4o-mini")
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": message}],
        "temperature": 0.7,
    }
    return api_key, base_url, model, payload


async def request_ai_reply(message: str):
    config = get_ai_reply(message)
    if len(config) == 3:
        return config
    api_key, base_url, model, payload = config
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(45.0, connect=10.0)) as client:
            response = await client.post(
                f"{base_url}/chat/completions",
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
            answer = data["choices"][0]["message"]["content"]
            if not isinstance(answer, str) or not answer.strip():
                raise ValueError("Empty model response")
            return answer, "provider", model
    except httpx.HTTPStatusError as exc:
        status = exc.response.status_code
        if status in (401, 403):
            detail = "مفتاح مزود الذكاء الاصطناعي غير صالح أو لا يملك صلاحية الاستخدام."
        elif status == 429:
            detail = "تم تجاوز حد الطلبات لدى مزود الذكاء الاصطناعي. حاول لاحقاً."
        else:
            detail = f"رفض مزود الذكاء الاصطناعي الطلب (HTTP {status})."
        raise HTTPException(status_code=502, detail=detail) from exc
    except (httpx.RequestError, KeyError, IndexError, ValueError) as exc:
        raise HTTPException(status_code=502, detail="تعذر الحصول على رد صالح من مزود الذكاء الاصطناعي.") from exc


@app.get("/health")
async def health():
    try:
        init_db()
        return {"status": "ok", "service": "neurox-ai-api", "database": "ok"}
    except sqlite3.Error as exc:
        raise HTTPException(status_code=503, detail="قاعدة البيانات غير متاحة.") from exc


@app.post("/api/chat")
async def chat(request: ChatRequest):
    message = request.message.strip()
    if not message:
        raise HTTPException(status_code=400, detail="اكتب رسالة أولاً.")

    reply, mode, model = await request_ai_reply(message)
    conversation_id = request.conversation_id or str(uuid.uuid4())
    try:
        with connect_db() as db:
            exists = db.execute("SELECT id FROM conversations WHERE id = ?", (conversation_id,)).fetchone()
            if exists is None:
                db.execute(
                    "INSERT INTO conversations (id, title) VALUES (?, ?)",
                    (conversation_id, message[:72]),
                )
            db.execute(
                "INSERT INTO messages (conversation_id, role, content) VALUES (?, 'user', ?)",
                (conversation_id, message),
            )
            db.execute(
                "INSERT INTO messages (conversation_id, role, content) VALUES (?, 'assistant', ?)",
                (conversation_id, reply),
            )
            db.execute("UPDATE conversations SET updated_at = CURRENT_TIMESTAMP WHERE id = ?", (conversation_id,))
    except sqlite3.Error as exc:
        raise HTTPException(status_code=503, detail="تعذر حفظ المحادثة في قاعدة البيانات.") from exc

    return {"reply": reply, "conversation_id": conversation_id, "mode": mode, "model": model}


@app.get("/api/conversations")
async def list_conversations():
    with connect_db() as db:
        rows = db.execute(
            "SELECT id, title, created_at, updated_at FROM conversations ORDER BY updated_at DESC LIMIT 100"
        ).fetchall()
    return {"conversations": [dict(row) for row in rows]}


@app.get("/api/conversations/{conversation_id}")
async def get_conversation(conversation_id: str):
    with connect_db() as db:
        conversation = db.execute(
            "SELECT id, title, created_at, updated_at FROM conversations WHERE id = ?",
            (conversation_id,),
        ).fetchone()
        if conversation is None:
            raise HTTPException(status_code=404, detail="المحادثة غير موجودة.")
        messages = db.execute(
            "SELECT id, role, content, created_at FROM messages WHERE conversation_id = ? ORDER BY id",
            (conversation_id,),
        ).fetchall()
    return {"conversation": dict(conversation), "messages": [dict(row) for row in messages]}


@app.delete("/api/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):
    with connect_db() as db:
        cursor = db.execute("DELETE FROM conversations WHERE id = ?", (conversation_id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="المحادثة غير موجودة.")
    return {"deleted": True, "conversation_id": conversation_id}


@app.get("/api/mcp/servers")
async def list_mcp_servers():
    return {"servers": [], "status": "not_configured"}
