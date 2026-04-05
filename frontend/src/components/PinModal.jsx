import React, { useState, useEffect, useCallback } from "react";

const DEMO_PIN = "1000";
const PIN_LENGTH = 4;

/**
 * PinModal - Secure PIN verification overlay.
 * Props:
 *   isOpen     {boolean}  - controls visibility
 *   onSuccess  {fn}       - called when correct PIN is entered
 *   onCancel   {fn}       - called when user cancels
 */
export default function PinModal({ isOpen, onSuccess, onCancel }) {
  const [pin, setPin]       = useState("");
  const [error, setError]   = useState("");
  const [shake, setShake]   = useState(false);
  const [success, setSuccess] = useState(false);

  // Reset state every time modal opens
  useEffect(() => {
    if (isOpen) {
      setPin("");
      setError("");
      setShake(false);
      setSuccess(false);
    }
  }, [isOpen]);

  // Auto-submit when 4 digits entered
  useEffect(() => {
    if (pin.length === PIN_LENGTH) {
      handleVerify(pin);
    }
  }, [pin]);

  const handleVerify = useCallback((currentPin) => {
    if (currentPin === DEMO_PIN) {
      setError("");
      setSuccess(true);
      // Short success animation before closing
      setTimeout(() => {
        onSuccess();
      }, 600);
    } else {
      setShake(true);
      setError("Incorrect PIN. Please try again.");
      setTimeout(() => {
        setPin("");
        setShake(false);
      }, 600);
    }
  }, [onSuccess]);

  const pressDigit = (digit) => {
    if (pin.length < PIN_LENGTH && !success) {
      setError("");
      setPin((prev) => prev + digit);
    }
  };

  const pressDelete = () => {
    if (!success) {
      setError("");
      setPin((prev) => prev.slice(0, -1));
    }
  };

  if (!isOpen) return null;

  const keypad = [
    ["1", "2", "3"],
    ["4", "5", "6"],
    ["7", "8", "9"],
    ["del", "0", "cancel"],
  ];

  return (
    /* Backdrop */
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
      style={{ backdropFilter: "blur(12px)", background: "rgba(0,0,0,0.45)" }}
      onClick={(e) => { if (e.target === e.currentTarget) onCancel(); }}
    >
      {/* Modal card */}
      <div
        className={`relative w-full max-w-sm bg-white dark:bg-slate-900 rounded-3xl shadow-2xl border border-white/60 dark:border-white/10 overflow-hidden transition-all duration-300
          ${shake ? "animate-[pinShake_0.5s_ease-in-out]" : ""}
          ${isOpen ? "scale-100 opacity-100" : "scale-95 opacity-0"}`}
      >
        {/* Top gradient accent */}
        <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-cyan-400 via-violet-500 to-cyan-400" />

        {/* Glow halo */}
        <div className="absolute -top-12 left-1/2 -translate-x-1/2 w-40 h-40 rounded-full bg-cyan-400/10 blur-3xl pointer-events-none" />

        <div className="p-8">
          {/* Icon + Title */}
          <div className="flex flex-col items-center mb-7">
            <div className={`w-16 h-16 rounded-2xl flex items-center justify-center text-3xl mb-4 shadow-lg transition-all duration-500
              ${success
                ? "bg-gradient-to-br from-emerald-400 to-teal-500 shadow-emerald-500/30"
                : "bg-gradient-to-br from-cyan-400 to-violet-600 shadow-cyan-500/20"}`}
            >
              {success ? "✓" : "🔐"}
            </div>
            <h2 className="text-xl font-black text-slate-900 dark:text-white tracking-tight text-center">
              {success ? "Access Granted" : "PIN Verification"}
            </h2>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-1.5 text-center font-medium leading-relaxed max-w-[200px]">
              {success
                ? "Identity confirmed. Loading your portfolio…"
                : "Enter your 4-digit security PIN to access your portfolio"}
            </p>
          </div>

          {/* PIN dots */}
          <div className="flex justify-center gap-4 mb-6">
            {Array.from({ length: PIN_LENGTH }).map((_, i) => {
              const filled = i < pin.length;
              return (
                <div
                  key={i}
                  className={`w-4 h-4 rounded-full border-2 transition-all duration-200
                    ${success
                      ? "bg-emerald-500 border-emerald-500 scale-110"
                      : filled
                        ? "bg-gradient-to-br from-cyan-500 to-violet-600 border-transparent scale-110 shadow-md shadow-cyan-500/30"
                        : "bg-transparent border-slate-300 dark:border-slate-600"}`}
                />
              );
            })}
          </div>

          {/* Error message */}
          <div className={`text-center mb-5 transition-all duration-300 ${error ? "opacity-100" : "opacity-0"}`}>
            <span className="text-xs font-bold text-red-500 dark:text-red-400 flex items-center justify-center gap-1.5">
              <span>⚠</span> {error || "‎"}
            </span>
          </div>

          {/* Numeric Keypad */}
          {!success && (
            <div className="grid grid-cols-3 gap-2.5">
              {keypad.flat().map((key) => {
                if (key === "del") {
                  return (
                    <button
                      key="del"
                      onClick={pressDelete}
                      className="h-14 rounded-2xl flex items-center justify-center font-bold text-slate-500 dark:text-slate-400
                        bg-slate-100 dark:bg-white/5 border border-slate-200 dark:border-white/8
                        hover:bg-slate-200 dark:hover:bg-white/10 hover:text-slate-700 dark:hover:text-slate-200
                        active:scale-95 transition-all duration-150 text-lg"
                      aria-label="Delete"
                    >
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                          d="M12 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2M3 12l6.414 6.414a2 2 0 001.414.586H19a2 2 0 002-2V7a2 2 0 00-2-2h-8.172a2 2 0 00-1.414.586L3 12z" />
                      </svg>
                    </button>
                  );
                }
                if (key === "cancel") {
                  return (
                    <button
                      key="cancel"
                      onClick={onCancel}
                      className="h-14 rounded-2xl flex items-center justify-center font-bold text-xs text-slate-500 dark:text-slate-500
                        bg-slate-100 dark:bg-white/5 border border-slate-200 dark:border-white/8
                        hover:bg-red-50 dark:hover:bg-red-500/10 hover:text-red-600 dark:hover:text-red-400 hover:border-red-200 dark:hover:border-red-500/20
                        active:scale-95 transition-all duration-150 uppercase tracking-wider"
                    >
                      Cancel
                    </button>
                  );
                }
                return (
                  <button
                    key={key}
                    onClick={() => pressDigit(key)}
                    className="h-14 rounded-2xl flex items-center justify-center font-black text-xl text-slate-800 dark:text-slate-100
                      bg-white dark:bg-white/8 border border-slate-200 dark:border-white/10
                      hover:bg-gradient-to-br hover:from-cyan-50 hover:to-violet-50 dark:hover:bg-white/15
                      hover:border-cyan-300 dark:hover:border-cyan-500/40 hover:text-cyan-700 dark:hover:text-cyan-300
                      active:scale-95 shadow-sm transition-all duration-150"
                  >
                    {key}
                  </button>
                );
              })}
            </div>
          )}
        </div>

        {/* Bottom tip */}
        {!success && (
          <div className="px-8 pb-6 text-center">
            <p className="text-[10px] text-slate-400 dark:text-slate-600 font-medium uppercase tracking-widest">
              🔒 Demo PIN: 1000 · Secured by IntentShield
            </p>
          </div>
        )}
      </div>

      {/* Inline keyframe for shake */}
      <style>{`
        @keyframes pinShake {
          0%,100% { transform: translateX(0); }
          15%      { transform: translateX(-10px); }
          30%      { transform: translateX(10px); }
          45%      { transform: translateX(-8px); }
          60%      { transform: translateX(8px); }
          75%      { transform: translateX(-4px); }
          90%      { transform: translateX(4px); }
        }
      `}</style>
    </div>
  );
}
