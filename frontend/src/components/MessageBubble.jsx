import React from "react";

/**
 * Renders a single chat message bubble.
 * Supports basic markdown: **bold**, *italic*, bullet lists, line breaks.
 */
function formatText(text) {
  return text.split("\n").map((line, i) => {
    const parts = [];
    const regex = /\*\*(.+?)\*\*|\*(.+?)\*|\[(.+?)\]\((.+?)\)/g;
    let last = 0;
    let match;
    while ((match = regex.exec(line)) !== null) {
      if (match.index > last) parts.push(line.slice(last, match.index));
      if (match[1]) parts.push(<strong key={`b${i}-${match.index}`} className="font-exrabold text-slate-900 dark:text-white">{match[1]}</strong>);
      else if (match[2]) parts.push(<em key={`e${i}-${match.index}`} className="text-cyan-700 dark:text-cyan-400 font-medium italic">{match[2]}</em>);
      else if (match[3] && match[4]) parts.push(<a key={`l${i}-${match.index}`} href={match[4]} target="_blank" rel="noopener noreferrer" className="text-cyan-600 dark:text-cyan-400 font-semibold hover:underline">{match[3]}</a>);
      last = regex.lastIndex;
    }
    if (last < line.length) parts.push(line.slice(last));

    if (line.trimStart().startsWith("- ")) {
      return (
        <li key={i} className="ml-4 list-disc text-slate-700 dark:text-slate-300">
          {parts.length ? parts : line.replace(/^-\s/, "")}
        </li>
      );
    }
    return (
      <p key={i} className="leading-relaxed text-slate-700 dark:text-slate-300">
        {parts.length ? parts : (line || <>&nbsp;</>)}
      </p>
    );
  });
}

export default function MessageBubble({ msg }) {
  const isUser    = msg.role === "user";
  const isLoading = msg.loading;

  return (
    <div className={`flex items-end gap-3 animate-slide-up ${isUser ? "flex-row-reverse" : "flex-row"}`}>

      {/* Avatar */}
      <div className={`flex-shrink-0 w-8 h-8 rounded-xl flex items-center justify-center text-sm font-bold shadow-md transition-all duration-300
        ${isUser
          ? "bg-gradient-to-br from-cyan-500 to-violet-600 text-white"
          : "bg-white dark:bg-slate-800 border border-cyan-200 dark:border-white/10 text-lg"}`}
      >
        {isUser ? "U" : "🛡"}
      </div>

      {/* Bubble */}
      <div className={`max-w-[85%] px-4 py-3 rounded-2xl text-sm leading-relaxed shadow-sm transition-colors duration-300
        ${isUser
          ? "bg-gradient-to-br from-cyan-500/90 to-violet-600/90 text-white rounded-br-sm shadow-cyan-500/10"
          : "glass dark:bg-slate-900/40 text-slate-800 dark:text-slate-200 rounded-bl-sm"}`}
      >
        {isLoading ? (
          <div className="flex items-center gap-1.5 py-1 px-2">
            <span className="typing-dot" />
            <span className="typing-dot" />
            <span className="typing-dot" />
          </div>
        ) : (
          <div className="prose-chat space-y-1">
            {formatText(msg.content)}
          </div>
        )}

        {/* Image gallery */}
        {msg.image_urls && msg.image_urls.length > 0 && (
          <div className="mt-3 grid grid-cols-2 sm:grid-cols-3 gap-2">
            {msg.image_urls.slice(0, 6).map((url, idx) => (
              <img
                key={idx}
                src={url}
                alt="Research visual"
                onError={(e) => (e.target.style.display = "none")}
                className="w-full h-24 object-cover rounded-xl border border-white/60 dark:border-white/10 shadow-sm"
              />
            ))}
          </div>
        )}

        {/* Timestamp */}
        {!isLoading && (
          <div className={`mt-2 text-[10px] font-medium opacity-60 ${isUser ? "text-cyan-50 text-right" : "text-slate-500 dark:text-slate-400"}`}>
            {new Date(msg.timestamp || Date.now()).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
          </div>
        )}
      </div>
    </div>
  );
}
