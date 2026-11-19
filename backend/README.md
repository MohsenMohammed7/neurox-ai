# NeuroX AI Backend

واجهة FastAPI تأسيسية.

## تشغيل محلي

    python -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    uvicorn app.main:app --reload --port 8000

المسارات: GET /health، POST /api/chat، GET /api/mcp/servers.

رد المحادثة تجريبي ولا يستخدم نموذجاً لغوياً بعد.