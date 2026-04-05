import React from "react";

const RISK_LABELS = { LOW: "🟢 LOW", MEDIUM: "🟡 MEDIUM", HIGH: "🔴 HIGH", CRITICAL: "🚨 CRITICAL" };
const DECISION_ICONS = { ALLOW: "✅", BLOCK: "🚫" };

function Badge({ label, className }) {
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold border ${className}`}>
      {label}
    </span>
  );
}

function Row({ label, children }) {
  return (
    <div className="flex items-start justify-between gap-2 py-2 border-b border-slate-100 dark:border-white/5 last:border-0 transition-colors">
      <span className="text-[10px] uppercase tracking-wider font-bold text-slate-400 dark:text-slate-500 flex-shrink-0 mt-0.5 w-24">{label}</span>
      <div className="text-right text-xs text-slate-700 dark:text-slate-300 font-medium">{children}</div>
    </div>
  );
}

export default function SafetyPanel({ data }) {
  if (!data) {
    return (
      <div className="glass rounded-2xl p-4 flex flex-col h-36 transition-colors">
        <h2 className="text-[10px] font-extrabold text-slate-400 dark:text-slate-500 uppercase tracking-widest mb-3 flex items-center gap-1.5 opacity-80">
          <span className="w-1.5 h-1.5 rounded-full bg-gradient-to-r from-cyan-400 to-violet-500" />
          Safety Panel
        </h2>
        <div className="flex-1 flex items-center justify-center text-slate-400 dark:text-slate-600 text-[10px] font-medium text-center italic">
          Send a message to see live safety metadata here.
        </div>
      </div>
    );
  }

  const { intent_data, policy_result, decision_result, audit_log_entry } = data;
  const decision  = policy_result?.decision   || "BLOCK";
  const risk      = policy_result?.risk_level || "UNKNOWN";
  const intent    = policy_result?.intent     || "UNKNOWN";
  const isAllowed = decision === "ALLOW";

  return (
    <div className="glass rounded-2xl p-5 flex flex-col gap-1 animate-fade-in transition-colors">

      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <h2 className="text-[10px] font-extrabold text-slate-400 dark:text-slate-500 uppercase tracking-widest flex items-center gap-1.5">
          <span className={`w-2 h-2 rounded-full ${isAllowed ? "bg-emerald-500" : "bg-red-500"} animate-pulse shadow-glow`} />
          Safety Panel
        </h2>
        <Badge
          label={`${DECISION_ICONS[decision] || "?"} ${decision}`}
          className={`decision-${decision} text-[10px] px-2 py-0.5`}
        />
      </div>

      {/* Fields */}
      <Row label="Intent">
        <span className="font-mono text-cyan-700 dark:text-cyan-400 font-bold">{intent}</span>
      </Row>

      <Row label="Risk Level">
        <Badge label={RISK_LABELS[risk] || risk} className={`risk-${risk} text-[10px]`} />
      </Row>

      <Row label="Confidence">
        <div className="flex items-center gap-2 justify-end">
          <div className="w-16 h-1.5 bg-slate-100 dark:bg-white/5 rounded-full overflow-hidden border border-slate-200 dark:border-white/5">
            <div
              className="h-full bg-gradient-to-r from-cyan-400 to-violet-500 rounded-full transition-all duration-500"
              style={{ width: `${((intent_data?.confidence || 0) * 100).toFixed(0)}%` }}
            />
          </div>
          <span className="text-slate-700 dark:text-slate-200 font-bold tabular-nums tracking-tighter">
            {((intent_data?.confidence || 0) * 100).toFixed(0)}%
          </span>
        </div>
      </Row>

      <Row label="Tool Used">
        {decision_result?.tool_used ? (
          <span className="font-bold text-emerald-600 dark:text-emerald-400">{decision_result.tool_used}</span>
        ) : (
          <span className="text-slate-300 dark:text-slate-700 italic">None</span>
        )}
      </Row>

      <Row label="Executed">
        {decision_result?.executed
          ? <span className="text-emerald-600 dark:text-emerald-400 font-bold">Yes</span>
          : <span className="text-red-500 dark:text-red-400 font-bold">No</span>}
      </Row>

      {/* Reason */}
      <div className={`mt-4 p-3.5 rounded-xl text-[11px] leading-relaxed border transition-colors
        ${isAllowed
          ? "bg-emerald-50/50 dark:bg-emerald-500/5 border-emerald-200 dark:border-emerald-500/20 text-emerald-800 dark:text-emerald-300"
          : "bg-red-50/50   dark:bg-red-500/5     border-red-200     dark:border-red-500/20     text-red-800     dark:text-red-300"}`}
      >
        <p className="font-bold mb-1 uppercase tracking-wider text-[9px] opacity-70">
          {isAllowed ? "✅ Authorization Reason" : "🚫 Rejection Reason"}
        </p>
        <p className="font-medium leading-normal">{policy_result?.reason || "—"}</p>
      </div>

      {/* Symbol / companies */}
      {(intent_data?.symbol || intent_data?.companies?.length > 0) && (
        <div className="mt-3 p-3 rounded-xl bg-slate-100/50 dark:bg-white/5 border border-slate-200 dark:border-white/5 text-[11px] transition-colors">
          {intent_data?.symbol && (
            <p className="text-slate-500 dark:text-slate-400 font-medium">
              Symbol: <span className="text-slate-900 dark:text-white font-mono font-bold ml-1">{intent_data.symbol}</span>
            </p>
          )}
          {intent_data?.companies?.length > 0 && (
            <p className="text-slate-500 dark:text-slate-400 font-medium mt-1">
              Entities: <span className="text-slate-900 dark:text-white font-bold ml-1">{intent_data.companies.join(", ")}</span>
            </p>
          )}
        </div>
      )}

      {/* Timestamp */}
      {audit_log_entry?.timestamp && (
        <p className="mt-2 text-[10px] text-slate-400 dark:text-slate-600 text-right font-medium">
          {new Date(audit_log_entry.timestamp).toLocaleTimeString()}
        </p>
      )}
    </div>
  );
}
