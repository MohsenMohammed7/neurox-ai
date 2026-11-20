"use client";

import { useCallback, useEffect, useState } from "react";
import { Activity, ArrowUp, Bot, BrainCircuit, ImagePlus, MessageSquare, Plus, Plug, Sparkles, Trash2 } from "lucide-react";

type Message = { role: "assistant" | "user"; content: string };
type Conversation = { id: string; title: string; updated_at: string };

export default function Home() {
  const [prompt, setPrompt] = useState("");
  const [busy, setBusy] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    { role: "assistant", content: "مرحباً بك في NeuroX AI. ابدأ محادثة جديدة أو تابع إحدى محادثاتك السابقة." }
  ]);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [historyError, setHistoryError] = useState("");

  const refreshConversations = useCallback(async () => {
    try {
      const response = await fetch("/api/conversations", { cache: "no-store" });
      if (!response.ok) throw new Error("تعذر تحميل سجل المحادثات");
      const data = await response.json();
      setConversations(data.conversations ?? []);
      setHistoryError("");
    } catch {
      setHistoryError("تعذر تحميل سجل المحادثات حالياً.");
    }
  }, []);

  useEffect(() => { void refreshConversations(); }, [refreshConversations]);

  function newConversation() {
    setConversationId(null);
    setMessages([{ role: "assistant", content: "محادثة جديدة جاهزة. ما الذي تريد أن نعمل عليه؟" }]);
    setPrompt("");
  }

  async function openConversation(id: string) {
    if (busy) return;
    try {
      const response = await fetch(`/api/conversations/${encodeURIComponent(id)}`, { cache: "no-store" });
      if (!response.ok) throw new Error("تعذر فتح المحادثة");
      const data = await response.json();
      setConversationId(id);
      setMessages((data.messages ?? []).map((m: { role: "assistant" | "user"; content: string }) => ({ role: m.role, content: m.content })));
    } catch {
      setHistoryError("لم نتمكن من فتح هذه المحادثة.");
    }
  }

  async function removeConversation(id: string) {
    if (!window.confirm("هل تريد حذف هذه المحادثة نهائياً؟")) return;
    try {
      const response = await fetch(`/api/conversations/${encodeURIComponent(id)}`, { method: "DELETE" });
      if (!response.ok) throw new Error("delete failed");
      if (conversationId === id) newConversation();
      await refreshConversations();
    } catch {
      setHistoryError("تعذر حذف المحادثة.");
    }
  }

  async function sendMessage() {
    const value = prompt.trim();
    if (!value || busy) return;
    setMessages(old => [...old, { role: "user", content: value }]);
    setPrompt("");
    setBusy(true);
    try {
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: value, ...(conversationId ? { conversation_id: conversationId } : {}) })
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || data.reply || "حدث خطأ أثناء إرسال الرسالة.");
      if (data.conversation_id) setConversationId(data.conversation_id);
      setMessages(old => [...old, { role: "assistant", content: data.reply ?? "لم أتمكن من الحصول على رد." }]);
      await refreshConversations();
    } catch (error) {
      setMessages(old => [...old, { role: "assistant", content: error instanceof Error ? error.message : "تعذر الاتصال بالخادم." }]);
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="shell">
      <aside className="sidebar">
        <div className="brand"><div className="brand-icon"><BrainCircuit size={24}/></div><div><b>NeuroX</b><small>AI WORKSPACE</small></div></div>
        <button className="new-chat" onClick={newConversation}><Plus size={17}/> محادثة جديدة</button>
        <div className="nav-label">مساحة العمل</div>
        <a className="nav active"><Bot size={18}/> المحادثة الذكية</a>
        <a className="nav disabled"><ImagePlus size={18}/> توليد الصور <span>قريباً</span></a>
        <a className="nav disabled"><Plug size={18}/> خوادم MCP <span>قريباً</span></a>
        <div className="history-title"><MessageSquare size={15}/> المحادثات السابقة</div>
        {historyError && <p className="history-error">{historyError}</p>}
        <div className="history-list">
          {conversations.length === 0 && <small className="empty-history">ستظهر محادثاتك هنا بعد أول رسالة.</small>}
          {conversations.map(item => (
            <div className={`history-item ${conversationId === item.id ? "selected" : ""}`} key={item.id}>
              <button className="history-open" onClick={() => void openConversation(item.id)} title={item.title}>{item.title}</button>
              <button className="history-delete" onClick={() => void removeConversation(item.id)} aria-label="حذف المحادثة"><Trash2 size={14}/></button>
            </div>
          ))}
        </div>
        <div className="side-bottom"><Activity size={16}/> النظام يعمل <i/></div>
      </aside>

      <section className="workspace">
        <header className="topbar">
          <div><span className="eyebrow">منصة الذكاء الاصطناعي</span><h1>ماذا تريد أن تنجز اليوم؟</h1></div>
          <div className="status"><i/> مساحة عملك الشخصية</div>
        </header>
        <div className="hero">
          <div className="orb"><Sparkles size={34}/></div>
          <h2>أطلق أفكارك مع <em>NeuroX AI</em></h2>
          <p>محادثات محفوظة ومساحة موحدة للأدوات الذكية.</p>
        </div>
        <div className="chat">
          <div className="chat-head">
            <div><b>المساعد الذكي</b><small>{conversationId ? "محادثة محفوظة" : "ابدأ محادثة جديدة"}</small></div>
            <span className="live">● جاهز</span>
          </div>
          <div className="messages">
            {messages.map((m, i) => <div key={i} className={`message ${m.role}`}><div className="avatar">{m.role === "assistant" ? <BrainCircuit size={17}/> : "أنت"}</div><p>{m.content}</p></div>)}
            {busy && <div className="message assistant"><div className="avatar"><BrainCircuit size={17}/></div><p className="typing">NeuroX يفكر الآن...</p></div>}
          </div>
          <div className="composer">
            <textarea value={prompt} onChange={e => setPrompt(e.target.value)} onKeyDown={e => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); void sendMessage(); } }} placeholder="اكتب رسالتك هنا..." rows={2}/>
            <button onClick={() => void sendMessage()} disabled={busy || !prompt.trim()} aria-label="إرسال"><ArrowUp size={20}/></button>
          </div>
          <small className="disclaimer">احفظ محادثاتك تلقائياً. استخدم مفتاح مزود AI لتفعيل الإجابات الذكية الفعلية.</small>
        </div>
      </section>
    </main>
  );
}
