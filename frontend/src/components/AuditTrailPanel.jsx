import React, { useState, useEffect } from "react";

const API = import.meta.env.VITE_API_URL || "http://localhost:8000";

const RISK_DOT = {
  LOW:      "bg-emerald-400",
  MEDIUM:   "bg-amber-400",
  HIGH:     "bg-red-400",
  CRITICAL: "bg-red-600",
};
const DECISION_COLOR = {
  ALLOW: "text-emerald-700 dark:text-emerald-400 font-bold",
  BLOCK: "text-red-600   dark:text-red-400     font-bold",
};

export default function AuditTrailPanel() {
  const [logs,    setLogs]    = useState([]);
  const [open,    setOpen]    = useState(false);
  const [loading, setLoading] = useState(false);

  const fetchLogs = async () => {
    setLoading(true);
    try {
      const res  = await fetch(`${API}/logs`);
      const data = await res.json();
      setLogs(data);
    } catch {
      setLogs([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { if (open) fetchLogs(); }, [open]);

  return (
    <div className="glass rounded-2xl overflow-hidden transition-all duration-300">
      {/* Toggle header */}
      <button
        onClick={() => setOpen((v) => !v)}
        className="w-full flex items-center justify-between px-5 py-3.5 hover:bg-black/5 dark:hover:bg-white/5 transition-colors duration-200"
      >
        <div className="flex items-center gap-2.5">
          <span className="text-[10px] font-extrabold text-slate-400 dark:text-slate-500 uppercase tracking-widest">📋 Audit Trail</span>
          {logs.length > 0 && (
            <span className="text-[10px] px-2 py-0.5 rounded-full bg-cyan-100 dark:bg-cyan-900/40 text-cyan-700 dark:text-cyan-400 border border-cyan-200 dark:border-cyan-700/50 font-bold">
              {logs.length}
            </span>
          )}
        </div>
        <svg
          className={`w-3.5 h-3.5 text-slate-400 dark:text-slate-500 transition-transform duration-300 ease-out ${open ? "rotate-180" : ""}`}
          fill="none" stroke="currentColor" viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {/* Log list */}
      {open && (
        <div className="border-t border-slate-100 dark:border-white/5 animate-fade-in">
          <div className="flex items-center justify-between px-5 py-2.5 bg-slate-50/50 dark:bg-black/20 border-b border-slate-100 dark:border-white/5">
            <span className="text-[10px] text-slate-400 dark:text-slate-500 font-bold uppercase tracking-wider">Recent Decisions</span>
            <button
              onClick={fetchLogs}
              className="text-[10px] text-cyan-600 dark:text-cyan-400 hover:text-cyan-800 dark:hover:text-cyan-200 font-bold uppercase tracking-wider transition-colors"
            >
              {loading ? "Refreshing…" : "Refresh"}
            </button>
          </div>

          <div className="max-h-80 overflow-y-auto">
            {logs.length === 0 ? (
              <div className="py-8 text-center text-[10px] font-medium text-slate-400 dark:text-slate-600 italic">
                {loading ? "Loading database..." : "No historical audit entries."}
              </div>
            ) : (
              logs.map((log, i) => (
                <div
                  key={i}
                  className="px-5 py-3.5 border-b border-slate-100 dark:border-white/5 hover:bg-black/[0.02] dark:hover:bg-white/[0.02] transition-colors text-[11px]"
                >
                  <div className="flex items-start justify-between gap-3 mb-1.5">
                    <span className="text-slate-800 dark:text-slate-200 font-semibold truncate flex-1 leading-tight">{log.user_input}</span>
                    <span className={`flex-shrink-0 text-[10px] tracking-tight ${DECISION_COLOR[log.decision] || "text-slate-500"}`}>
                      {log.decision}
                    </span>
                  </div>
                  <div className="flex items-center gap-2 text-[10px] text-slate-400 dark:text-slate-500 font-medium overflow-hidden">
                    <span className={`w-1.5 h-1.5 rounded-full ring-2 ring-white dark:ring-black/20 ${RISK_DOT[log.risk_level] || "bg-slate-400"}`} />
                    <span className="font-mono text-cyan-600 dark:text-cyan-800 tracking-tighter opacity-80">{log.intent}</span>
                    <span className="opacity-30">·</span>
                    <span className="truncate">{log.tool_used || "Direct Response"}</span>
                    <span className="opacity-30">·</span>
                    <span className="flex-shrink-0">{new Date(log.timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}</span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
}
