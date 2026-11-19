from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
app = FastAPI(title="NeuroX AI API", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:3000"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
class ChatRequest(BaseModel):
    message: str
@app.get("/health")
async def health():
    return {"status": "ok", "service": "neurox-ai-api"}
@app.post("/api/chat")
async def chat(request: ChatRequest):
    if not request.message.strip():
        return {"reply": "اكتب رسالة أولاً."}
    return {"reply": "وصلت رسالتك بنجاح إلى خادم NeuroX AI. هذه استجابة تجريبية؛ يلزم إعداد مزود نموذج لغوي ومفتاح API لتفعيل الذكاء الاصطناعي الحقيقي."}
@app.get("/api/mcp/servers")
async def list_mcp_servers():
    return {"servers": [], "status": "not_configured"}