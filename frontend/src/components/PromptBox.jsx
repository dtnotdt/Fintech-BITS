import React, { useState, useRef, useEffect } from "react";

const SAMPLE_PROMPTS = [
  "What is Tesla stock price?",
  "Research Nvidia for me",
  "Show my portfolio",
  "Show my watchlist",
  "Compare Apple and Nvidia",
  "Buy 10 shares of Tesla",
];

export default function PromptBox({ onSend, disabled }) {
  const [value, setValue] = useState("");
  const textareaRef = useRef(null);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = Math.min(textareaRef.current.scrollHeight, 140) + "px";
    }
  }, [value]);

  const handleSend = () => {
    const trimmed = value.trim();
    if (!trimmed || disabled) return;
    onSend(trimmed);
    setValue("");
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="border-t border-slate-200 dark:border-white/5 bg-white/60 dark:bg-slate-900/60 backdrop-blur-xl px-4 py-3 shadow-[0_-4px_30px_rgba(0,0,0,0.03)] dark:shadow-[0_-10px_50px_rgba(0,0,0,0.4)] transition-all">

      {/* Quick-prompt pills */}
      <div className="flex flex-wrap gap-1.5 mb-3 px-1">
        {SAMPLE_PROMPTS.slice(0, 5).map((p) => (
          <button
            key={p}
            onClick={() => !disabled && onSend(p)}
            disabled={disabled}
            className="text-[10px] uppercase tracking-widest font-extrabold px-3 py-1.5 rounded-xl border border-slate-200 dark:border-white/5 text-slate-500 dark:text-slate-500
              hover:border-cyan-400 dark:hover:border-cyan-500 hover:text-cyan-700 dark:hover:text-cyan-400 hover:bg-cyan-50 dark:hover:bg-cyan-500/10
              transition-all duration-300 disabled:opacity-30 disabled:cursor-not-allowed transform active:scale-95"
          >
            {p}
          </button>
        ))}
      </div>

      {/* Input row */}
      <div className="flex items-end gap-3 px-1">
        <div className="flex-1 relative">
          <textarea
            ref={textareaRef}
            rows={1}
            value={value}
            onChange={(e) => setValue(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={disabled}
            placeholder="Ask IntentShield anything..."
            className="w-full resize-none glass dark:bg-white/5 rounded-2xl
              px-5 py-3.5 text-sm font-medium text-slate-800 dark:text-slate-100 placeholder-slate-400 dark:placeholder-slate-600
              focus:outline-none focus:ring-2 focus:ring-cyan-500/20 dark:focus:ring-cyan-500/10 focus:border-cyan-400 dark:focus:border-cyan-500/50
              border border-white/80 dark:border-white/5 transition-all duration-300
              disabled:opacity-50 disabled:cursor-not-allowed"
          />
        </div>

        {/* Send button */}
        <button
          onClick={handleSend}
          disabled={disabled || !value.trim()}
          className="flex-shrink-0 w-12 h-12 rounded-2xl
            bg-gradient-to-br from-cyan-500 to-violet-600
            hover:from-cyan-400 hover:to-violet-500
            disabled:opacity-40 disabled:grayscale disabled:cursor-not-allowed
            flex items-center justify-center text-white shadow-xl shadow-cyan-500/20
            transition-all duration-300 active:scale-90 hover:-translate-y-1"
        >
          {disabled ? (
            <svg className="w-5 h-5 animate-spin" viewBox="0 0 24 24" fill="none">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z" />
            </svg>
          ) : (
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
            </svg>
          )}
        </button>
      </div>

      <p className="mt-3 text-center text-[10px] font-bold text-slate-400 dark:text-slate-600 uppercase tracking-widest leading-relaxed">
        Policies enforced · Press <kbd className="px-1.5 py-0.5 rounded-lg bg-slate-100 dark:bg-white/5 border border-slate-200 dark:border-white/10 text-slate-500 dark:text-slate-500 text-[9px] font-mono mx-1">Enter</kbd> to send
      </p>
    </div>
  );
}
