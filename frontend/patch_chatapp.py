import re

with open("src/pages/ChatApp.jsx", "r") as f:
    content = f.read()

# Add states and useEffects
states_str = """  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [lastSafety, setLastSafety] = useState(null);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  
  const [chats, setChats] = useState([]);
  const [currentChatId, setCurrentChatId] = useState(null);

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
"""
content = re.sub(
    r"  const \[messages, setMessages\] = useState\(\[\]\);\n  const \[loading, setLoading\] = useState\(false\);\n  const \[lastSafety, setLastSafety\] = useState\(null\);\n  const \[sidebarOpen, setSidebarOpen\] = useState\(true\);",
    states_str,
    content,
    flags=re.MULTILINE
)

# Add Left Sidebar
sidebar_str = """
    <div className="flex h-screen overflow-hidden" style={{ background: "transparent" }}>
      {/* ── Left History Sidebar ────────────────────────────── */}
      <aside className="w-64 flex-shrink-0 border-r border-white/60 bg-white/50 backdrop-blur-md flex flex-col pt-4 overflow-y-auto z-10 hidden md:flex">
        <div className="px-4 pb-3">
          <button 
            onClick={handleNewChat}
            className="w-full flex items-center justify-center gap-2 py-2 px-4 bg-white/60 border border-slate-200 shadow-sm text-sm font-semibold text-slate-700 rounded-xl hover:bg-white hover:text-cyan-600 transition"
          >
            <span className="text-lg leading-none">+</span> New Chat
          </button>
        </div>
        <div className="flex-1 px-3 space-y-1.5 overflow-y-auto pb-4">
          <div className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2 ml-1 mt-2">History</div>
          {chats.map(c => (
            <button
              key={c.id}
              onClick={() => loadChat(c.id)}
              className={`w-full text-left px-3 py-2 rounded-lg text-sm truncate transition \${currentChatId === c.id ? 'bg-cyan-50 border border-cyan-100 text-cyan-800 font-semibold shadow-sm' : 'hover:bg-white/40 text-slate-600 border border-transparent hover:border-slate-200'}`}
            >
              {c.title}
            </button>
          ))}
        </div>
      </aside>

      {/* ── Chat Column ──────────────────────────────────────── */}
"""

content = content.replace(
    '    <div className="flex h-screen overflow-hidden" style={{ background: "transparent" }}>\n\n      {/* ── Chat Column ──────────────────────────────────────── */}',
    sidebar_str
)

with open("src/pages/ChatApp.jsx", "w") as f:
    f.write(content)

print("Patched ChatApp.jsx!")
