import React, { useState } from "react";
import ChatWindow from "../components/ChatWindow";
import SafetyPanel from "../components/SafetyPanel";
import AuditTrailPanel from "../components/AuditTrailPanel";
import PinModal from "../components/PinModal";
import { UserButton } from "@clerk/clerk-react";
import { useTheme } from "../hooks/useTheme";

const API = import.meta.env.VITE_API_URL || "http://localhost:8000";

export default function ChatApp() {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [lastSafety, setLastSafety] = useState(null);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  
  const [chats, setChats] = useState([]);
  const [currentChatId, setCurrentChatId] = useState(null);
  
  // Theme — single source of truth via shared hook
  const [theme, toggleTheme] = useTheme();

  // PIN Modal state
  const [isPinModalOpen, setIsPinModalOpen] = useState(false);
  const [pendingPortfolioMsg, setPendingPortfolioMsg] = useState(null);

  // Pipeline animation state
  const [pipelineStep, setPipelineStep] = useState(0);

  // Simulated pipeline progress during loading
  React.useEffect(() => {
    let interval;
    if (loading) {
      setPipelineStep(1);
      interval = setInterval(() => {
        setPipelineStep(prev => (prev < 4 ? prev + 1 : prev));
      }, 800);
    } else {
      setPipelineStep(0);
      if (interval) clearInterval(interval);
    }
    return () => clearInterval(interval);
  }, [loading]);

  React.useEffect(() => {
    const saved = localStorage.getItem("intentshield_chats");
    if (saved) {
      try {
        const parsed = JSON.parse(saved);
        setChats(parsed);
        if (parsed.length > 0) {
          const first = parsed[0];
          setCurrentChatId(first.id);
          setMessages(first.messages);
        }
      } catch (e) {
        console.error("Failed to parse chats", e);
      }
    }
  }, []);

  React.useEffect(() => {
    if (messages.length === 0 && !currentChatId) return;
    if (messages.length > 0) {
        const id = currentChatId || Date.now().toString();
        if (!currentChatId) setCurrentChatId(id);
        
        setChats(prev => {
            const idx = prev.findIndex(c => c.id === id);
            const userMsg = messages.find(m => m.role === 'user');
            const title = userMsg ? userMsg.content.slice(0, 25) + (userMsg.content.length > 25 ? "..." : "") : "New Chat";
            
            const copy = [...prev];
            if (idx >= 0) {
                copy[idx].messages = messages;
                copy[idx].updatedAt = Date.now();
            } else {
                copy.unshift({ id, title, messages, updatedAt: Date.now() });
            }
            localStorage.setItem("intentshield_chats", JSON.stringify(copy));
            return copy;
        });
    }
  }, [messages, currentChatId]);

  const handleNewChat = () => {
      setMessages([]);
      setCurrentChatId(Date.now().toString());
      setLastSafety(null);
  };

  const loadChat = (chatId) => {
      const c = chats.find(c => c.id === chatId);
      if (c) {
          setMessages(c.messages);
          setCurrentChatId(c.id);
          setLastSafety(null);
      }
  };




  const handleSend = async (userMessage) => {
    if (loading) return;

    const userMsg    = { role: "user",      content: userMessage,  timestamp: new Date().toISOString() };
    const loadingMsg = { role: "assistant", content: "", loading: true, timestamp: new Date().toISOString() };
    setMessages((prev) => [...prev, userMsg, loadingMsg]);
    setLoading(true);

    try {
      const res = await fetch(`${API}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          message: userMessage,
          context: messages.slice(-8).map(m => ({ role: m.role, content: m.content }))
        }),
      });
      if (!res.ok) throw new Error(`Server error ${res.status}`);
      const data = await res.json();

      const assistantMsg = {
        role: "assistant",
        content: data.assistant_reply || "I couldn't process that request.",
        image_urls: data.image_urls || [],
        timestamp: new Date().toISOString(),
      };

      if (data.intent_data?.intent === "VIEW_PORTFOLIO") {
        setPendingPortfolioMsg({ assistantMsg, data });
        setMessages((prev) => [
          ...prev.slice(0, -1),
          {
            role: "assistant",
            content: "Portfolio access requires PIN verification.",
            timestamp: new Date().toISOString(),
          }
        ]);
        setIsPinModalOpen(true);
      } else {
        setMessages((prev) => [...prev.slice(0, -1), assistantMsg]);
        setLastSafety(data);
      }
    } catch (err) {
      setMessages((prev) => [
        ...prev.slice(0, -1),
        {
          role: "assistant",
          content: `⚠️ **Connection error**: Could not reach the backend. Make sure the FastAPI server is running on port 8000.\n\nError: ${err.message}`,
          timestamp: new Date().toISOString(),
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handlePinSuccess = () => {
    setIsPinModalOpen(false);
    if (pendingPortfolioMsg) {
      const { assistantMsg, data } = pendingPortfolioMsg;
      const finalMsg = {
        ...assistantMsg,
        content: `*Secure Access Required: Please verify your 4-digit PIN to view your portfolio.*\n\n${assistantMsg.content}`
      };
      setMessages((prev) => [...prev.slice(0, -1), finalMsg]);
      setLastSafety(data);
      setPendingPortfolioMsg(null);
    }
  };

  const handlePinCancel = () => {
    setIsPinModalOpen(false);
    setPendingPortfolioMsg(null);
    setMessages((prev) => [
      ...prev.slice(0, -1),
      {
        role: "assistant",
        content: "Action cancelled. PIN verification aborted.",
        timestamp: new Date().toISOString(),
      }
    ]);
  };

  const pipelineSteps = [
    { id: 1, label: "Intent Extraction", icon: "🧠" },
    { id: 2, label: "Policy Check",       icon: "⚖️" },
    { id: 3, label: "Decision Engine",    icon: "🔀" },
    { id: 4, label: "Tool Execution",     icon: "🛠️" },
    { id: 5, label: "Audit Log Generated",icon: "📋" },
  ];

  return (

    <div className="flex h-screen overflow-hidden relative">
      <PinModal 
        isOpen={isPinModalOpen} 
        onSuccess={handlePinSuccess} 
        onCancel={handlePinCancel} 
      />

      {/* Background Layers */}
      <div className="mesh-gradient" />
      <div className="mesh-gradient-dark" />

      {/* ── Left History Sidebar ────────────────────────────── */}
      <aside className="w-64 flex-shrink-0 border-r border-slate-200 dark:border-white/10 bg-white/40 dark:bg-slate-900/60 backdrop-blur-xl flex flex-col pt-4 overflow-y-auto z-10 hidden md:flex transition-colors">
        <div className="px-4 pb-3 space-y-2">
          <button 
            onClick={() => handleSend("Show my watchlist")}
            className="w-full flex items-center justify-center gap-2 py-2.5 px-4 bg-cyan-500/10 dark:bg-cyan-500/20 border border-cyan-500/20 dark:border-cyan-500/30 shadow-sm text-sm font-bold text-cyan-700 dark:text-cyan-400 rounded-xl hover:bg-cyan-500/20 dark:hover:bg-cyan-500/30 transition-all"
          >
            👁️ Show Watchlist
          </button>
          <button 
            onClick={handleNewChat}
            className="w-full flex items-center justify-center gap-2 py-2.5 px-4 bg-white/60 dark:bg-white/10 border border-slate-200 dark:border-white/10 shadow-sm text-sm font-semibold text-slate-700 dark:text-slate-200 rounded-xl hover:bg-white dark:hover:bg-white/20 hover:text-cyan-600 transition-all"
          >
            <span className="text-lg leading-none font-light">+</span> New Chat
          </button>
        </div>
        <div className="flex-1 px-3 space-y-1 overflow-y-auto pb-4">
          <div className="text-[10px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest mb-3 ml-2 mt-2">History</div>
          {chats.map(c => (
            <button
              key={c.id}
              onClick={() => loadChat(c.id)}
              className={`w-full text-left px-3 py-2.5 rounded-xl text-sm truncate transition-all ${currentChatId === c.id ? 'bg-cyan-500/10 dark:bg-cyan-500/20 text-cyan-700 dark:text-cyan-400 font-semibold shadow-sm' : 'hover:bg-black/5 dark:hover:bg-white/5 text-slate-600 dark:text-slate-400 border border-transparent'}`}
            >
              {c.title}
            </button>
          ))}
        </div>
      </aside>

      {/* ── Chat Column ──────────────────────────────────────── */}

      <div className="flex-1 flex flex-col min-w-0">

        {/* Top bar */}
        <header className="flex items-center justify-between px-5 py-3 border-b border-white/40 dark:border-white/10 bg-white/60 dark:bg-slate-900/60 backdrop-blur-xl shadow-sm z-10 transition-colors">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-400 to-violet-600 flex items-center justify-center text-xl shadow-md transform -rotate-3">
              🛡️
            </div>
            <div>
              <h1 className="text-base font-bold text-slate-900 dark:text-white leading-none tracking-tight">IntentShield</h1>
              <p className="text-[10px] text-slate-500 dark:text-slate-400 font-medium uppercase tracking-wider mt-1.5 opacity-80">Security Intelligence</p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            {/* Status pill */}
            <div className="hidden sm:flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-emerald-500/10 dark:bg-emerald-500/20 border border-emerald-500/20">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
              <span className="text-[10px] text-emerald-700 dark:text-emerald-400 font-bold uppercase tracking-wider">Engine Active</span>
            </div>

            {/* Theme Toggle */}
            <button
              onClick={toggleTheme}
              className="p-2 rounded-xl bg-slate-100 dark:bg-white/5 text-slate-500 dark:text-slate-400 hover:text-cyan-600 dark:hover:text-cyan-400 transition-all border border-transparent hover:border-slate-200 dark:hover:border-white/10"
              title={`Switch to ${theme === "dark" ? "light" : "dark"} mode`}
            >
              {theme === "dark" ? (
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364-6.364l-.707.707M6.364 17.636l-.707.707M6.364 6.364l.707.707m11.314 11.314l.707.707M12 8a4 4 0 100 8 4 4 0 000-8z" />
                </svg>
              ) : (
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
                </svg>
              )}
            </button>

            <UserButton
              afterSignOutUrl="/"
              appearance={{ elements: { userButtonAvatarBox: "w-9 h-9 rounded-xl border border-white/20 shadow-sm" } }}
            />

            <button
              onClick={() => setSidebarOpen((v) => !v)}
              title="Toggle Safety Panel"
              className="p-2 rounded-xl hover:bg-slate-100 text-slate-400 hover:text-slate-700 transition-colors"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
                  d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </button>
          </div>
        </header>

        {/* Chat area */}
        <div className="flex-1 overflow-hidden">
          <ChatWindow messages={messages} onSend={handleSend} loading={loading} />
        </div>
      </div>

      {/* ── Right Sidebar ─────────────────────────────────────── */}
      {sidebarOpen && (
        <aside className="w-80 flex-shrink-0 border-l border-white/40 dark:border-white/10 bg-white/40 dark:bg-slate-900/60 backdrop-blur-xl shadow-2xl flex flex-col gap-3 p-3 overflow-y-auto z-10 transition-colors">

          {/* Pipeline card */}
          <div className="glass rounded-2xl p-5">
            <h2 className="text-[10px] font-extrabold text-slate-400 dark:text-slate-500 uppercase tracking-[0.2em] mb-4 flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-gradient-to-r from-cyan-400 to-violet-500" />
              Security Pipeline
            </h2>
            <div className="space-y-4">
              {pipelineSteps.map(({ id, label, icon }) => {
                const isActive    = loading && pipelineStep === id;
                const isCompleted = (!loading && !!lastSafety) || (loading && pipelineStep > id);
                
                return (
                  <div key={id} className="flex items-center gap-3 group animate-fade-in">
                    <div className={`w-7 h-7 rounded-full flex items-center justify-center text-[10px] font-black flex-shrink-0 border-2 transition-all duration-300
                      ${isActive    ? "border-cyan-500 text-cyan-600 bg-cyan-500/10 scale-110 shadow-lg shadow-cyan-500/20"
                      : isCompleted ? "border-emerald-500 text-emerald-600 bg-emerald-500/10"
                      :             "border-slate-200 dark:border-white/5 text-slate-300 dark:text-slate-700 bg-transparent"}`}
                    >
                      {isCompleted ? "✓" : id}
                    </div>
                    <div className="flex flex-col">
                      <div className="flex items-center gap-2">
                        <span className="text-sm grayscale-[0.5] group-hover:grayscale-0 transition-all">{icon}</span>
                        <span className={`text-xs font-bold transition-colors
                          ${isActive    ? "text-cyan-600 dark:text-cyan-400"
                          : isCompleted ? "text-slate-900 dark:text-slate-200"
                          :             "text-slate-400 dark:text-slate-700"}`}
                        >
                          {label}
                        </span>
                      </div>
                      {isActive && (
                        <div className="w-full mt-1.5 h-0.5 bg-slate-100 dark:bg-white/5 rounded-full overflow-hidden">
                          <div className="h-full bg-cyan-500 animate-[loadingBar_1.5s_ease-in-out_infinite]" style={{ width: '40%' }} />
                        </div>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Safety Panel */}
          <SafetyPanel data={lastSafety} />

          {/* Audit Trail */}
          <AuditTrailPanel />
        </aside>
      )}
    </div>
  );
}
