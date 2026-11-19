import os

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="NeuroX AI API", version="0.2.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str


@app.get("/health")
async def health():
    return {"status": "ok", "service": "neurox-ai-api"}


@app.post("/api/chat")
async def chat(request: ChatRequest):
    message = request.message.strip()
    if not message:
        raise HTTPException(status_code=400, detail="اكتب رسالة أولاً.")

    api_key = os.getenv("AI_API_KEY", "").strip()
    if not api_key:
        return {
            "reply": (
                "وصلت رسالتك إلى خادم NeuroX AI بنجاح. "
                "لتفعيل الردود الذكية، أضف AI_API_KEY وAI_MODEL إلى متغيرات البيئة."
            ),
            "mode": "setup_required",
        }

    base_url = os.getenv("AI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
    model = os.getenv("AI_MODEL", "gpt-4o-mini")
    timeout = httpx.Timeout(45.0, connect=10.0)
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": message}],
        "temperature": 0.7,
    }

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(
                f"{base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
            answer = data["choices"][0]["message"]["content"]
            if not isinstance(answer, str) or not answer.strip():
                raise ValueError("Empty model response")
            return {"reply": answer, "model": model, "mode": "provider"}
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
        raise HTTPException(
            status_code=502,
            detail="تعذر الحصول على رد صالح من مزود الذكاء الاصطناعي.",
        ) from exc


@app.get("/api/mcp/servers")
async def list_mcp_servers():
    return {"servers": [], "status": "not_configured"}
