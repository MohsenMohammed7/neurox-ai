# NeuroX AI

**Advanced AI Workspace powered by MCP**

واجهة عمل عربية (RTL) للذكاء الاصطناعي، مع واجهة Next.js وخادم FastAPI ونقاط تجهيز أولية لتكامل MCP.

## الحالة الحالية

هذه نسخة تأسيسية قيد التطوير:
- واجهة عربية متجاوبة ومحادثة أولية.
- مسار Next.js وسيط يرسل الطلبات إلى FastAPI.
- خادم FastAPI مع فحص صحة الخدمة ونقطة محادثة تجريبية.
- نقطة أولية لعرض خوادم MCP؛ لا يوجد خادم MCP متصل بعد.
- لا يوجد مزود نموذج لغوي أو Firebase أو توليد صور مفعّل حتى الآن.

## المتطلبات
- Node.js 20 أو أحدث.
- Python 3.11 أو أحدث.

## تشغيل الواجهة
```bash
npm install
npm run dev
```
افتح `http://localhost:3000`.

## تشغيل الخادم
من مجلد المشروع:
```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r backend/requirements.txt
uvicorn app.main:app --app-dir backend --reload --port 8000
```

انسخ `.env.example` إلى `.env.local` واضبط `BACKEND_URL=http://localhost:8000` عند الحاجة.

## الأمان
لا ترفع مفاتيح API أو كلمات المرور إلى GitHub. استخدم متغيرات البيئة وأسرار GitHub Actions.

## خارطة الطريق
1. التحقق الآلي من البناء والاختبارات.
2. ربط مزود ذكاء اصطناعي حقيقي مع بث الردود وإدارة الأخطاء.
3. إضافة عميل MCP آمن وإدارة الخوادم والأدوات.
4. إضافة Firebase للمصادقة والتخزين عند تجهيز الإعدادات.
5. إضافة توليد الصور وتجهيز تطبيق Android.

راجع `docs/ARCHITECTURE.md` لمزيد من التفاصيل.
