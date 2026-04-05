import React, { useRef, useEffect } from "react";
import MessageBubble from "./MessageBubble";
import PromptBox from "./PromptBox";

export default function ChatWindow({ messages, onSend, loading }) {
  const endRef = useRef(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const suggestions = [
    "What is Tesla's stock price?",
    "Add Tesla to watchlist",
    "Show my watchlist",
    "Compare Apple vs Nvidia",
  ];

  return (
    <div className="flex flex-col h-full">
      {/* Messages area */}
      <div className="flex-1 overflow-y-auto px-5 py-6 space-y-5">
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-center gap-5 animate-fade-in">
            {/* Logo */}
            <div className="w-24 h-24 rounded-[2rem] bg-gradient-to-br from-cyan-400 to-violet-600 flex items-center justify-center text-5xl shadow-2xl shadow-cyan-500/20 transform hover:scale-105 transition-transform duration-500">
              🛡️
            </div>

            <div>
              <h2 className="text-3xl font-black text-slate-900 dark:text-white font-display tracking-tight">IntentShield</h2>
              <p className="text-sm text-slate-500 dark:text-slate-400 mt-2 max-w-[280px] leading-relaxed font-medium">
                Your secure financial co-pilot. <br/>
                Every request is validated by our <span className="text-cyan-600 dark:text-cyan-400 font-bold">Policy Protection Layer</span>.
              </p>
            </div>

            {/* Feature pills */}
            <div className="flex flex-wrap gap-2 justify-center max-w-sm mt-2">
              {[
                { icon: "🧠", label: "Intent Detection" },
                { icon: "⚖️", label: "Policy Engine" },
                { icon: "📊", label: "Market Intel" },
                { icon: "📋", label: "Audit Trail" },
              ].map((f) => (
                <span key={f.label} className="inline-flex items-center gap-2 px-4 py-2 rounded-2xl bg-white/40 dark:bg-white/5 border border-white/60 dark:border-white/10 text-[11px] font-bold text-slate-600 dark:text-slate-300 shadow-sm transition-colors">
                  <span className="text-xs">{f.icon}</span>
                  {f.label}
                </span>
              ))}
            </div>

            {/* Suggestion buttons */}
            <div className="flex flex-col gap-2 max-w-sm w-full mt-4">
              <p className="text-[10px] font-black text-slate-400 dark:text-slate-600 uppercase tracking-[0.2em] mb-1">Try asking</p>
              <div className="grid grid-cols-2 gap-2">
                {suggestions.map((p) => (
                  <button
                    key={p}
                    onClick={() => onSend(p)}
                    className="text-xs p-3.5 rounded-2xl glass dark:bg-white/5 text-slate-600 dark:text-slate-300 hover:text-cyan-600 dark:hover:text-cyan-400
                      hover:border-cyan-300 dark:hover:border-cyan-500/50 border border-white/80 dark:border-white/5 transition-all text-left hover:shadow-xl hover:-translate-y-1 duration-300 group"
                  >
                    <span className="opacity-70 group-hover:opacity-100 transition-opacity font-medium">{p}</span>
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}

        {messages.map((msg, i) => (
          <MessageBubble key={i} msg={msg} />
        ))}

        <div ref={endRef} />
      </div>

      {/* Prompt input */}
      <PromptBox onSend={onSend} disabled={loading} />
    </div>
  );
}
