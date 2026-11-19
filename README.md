# NeuroX AI

**Advanced AI Workspace powered by MCP**

منصة عربية RTL للمحادثة الذكية وإدارة سجل المحادثات، مبنية باستخدام Next.js وFastAPI وSQLite.

## ما يعمل حالياً
- واجهة Next.js متجاوبة باللغة العربية.
- إرسال الرسائل من الواجهة إلى FastAPI.
- حفظ المحادثات والرسائل في قاعدة SQLite محلية.
- عرض سجل المحادثات وفتحها وحذفها.
- ربط اختياري بمزود Chat Completions متوافق مع OpenAI.
- فحص صحة الخادم وقاعدة البيانات.
- اختبارات API آلية عبر GitHub Actions.

## ما لم يكتمل بعد
- لا يوجد خادم MCP خارجي متصل حتى الآن.
- Firebase والمصادقة متعددة المستخدمين غير مفعّلين.
- توليد الصور وتطبيق Android لم يجهزا بعد.
- يلزم مفتاح API صالح لتفعيل الردود من نموذج ذكاء اصطناعي فعلي.

## المتطلبات
- Node.js 20 أو أحدث.
- Python 3.11 أو أحدث.

## الإعداد
انسخ `.env.example` إلى `.env.local` في جذر المشروع، ثم أدخل مفتاح مزود الذكاء الاصطناعي في `AI_API_KEY` واضبط `AI_BASE_URL` و`AI_MODEL` حسب المزود. لا ترفع ملف `.env.local` إلى GitHub.

## تشغيل كامل باستخدام Docker
انسخ `.env.example` إلى `.env` في جذر المشروع، ثم أضف مفتاح مزود الذكاء الاصطناعي. شغّل:

```bash
docker compose up --build -d
```
افتح `http://localhost:3000`. لإيقاف الخدمات: `docker compose down`. تبقى قاعدة البيانات محفوظة في Docker volume باسم `neurox-data`.

## تشغيل الواجهة محلياً
```bash
npm install
npm run dev
```
افتح `http://localhost:3000`.

## تشغيل الخادم
من جذر المشروع:
```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r backend/requirements.txt
uvicorn app.main:app --app-dir backend --env-file .env.local --reload --port 8000
```
إذا لم تنشئ ملف `.env.local` بعد، يمكنك تشغيل الخادم من دون الخيار `--env-file`.

## الاختبارات
```bash
npm run lint
npm run build
PYTHONPATH=backend python -m unittest discover -s backend/tests -v
```

## الأمان وملاحظات النشر
- لا تضع مفاتيح API في ملفات المصدر أو المستودع.
- قاعدة SQLite مناسبة للتطوير أو نشر أحادي النسخة؛ استخدم قاعدة بيانات مُدارة عند التوسع لعدة نسخ.
- قبل إتاحة الخدمة للعامة، أضف المصادقة، حدود الطلبات، وسياسة خصوصية ونسخاً احتياطياً.

راجع `docs/ARCHITECTURE.md` لمزيد من التفاصيل.
