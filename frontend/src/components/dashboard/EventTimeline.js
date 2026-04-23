import React from "react";

const EVENT_CONFIG = {
  token:        { label: "Thinking",      bg: "bg-purple-500/10", border: "border-purple-500/30", text: "text-purple-300", icon: "🧠" },
  tool_start:   { label: "Using Tool",    bg: "bg-yellow-500/10", border: "border-yellow-500/30", text: "text-yellow-300", icon: "🔧" },
  tool_end:     { label: "Tool Result",   bg: "bg-blue-500/10",   border: "border-blue-500/30",   text: "text-blue-300",   icon: "✅" },
  tool_error:   { label: "Tool Error",    bg: "bg-red-500/10",    border: "border-red-500/30",    text: "text-red-300",    icon: "❌" },
  agent_finish: { label: "Completed",     bg: "bg-green-500/10",  border: "border-green-500/30",  text: "text-green-300",  icon: "🎉" },
  error:        { label: "Error",         bg: "bg-red-500/10",    border: "border-red-500/30",    text: "text-red-400",    icon: "🚨" },
  status:       { label: "Status",        bg: "bg-slate-500/10",  border: "border-slate-500/30",  text: "text-slate-300",  icon: "ℹ️" },
  raw:          { label: "Raw",           bg: "bg-slate-700/20",  border: "border-white/10",      text: "text-slate-400",  icon: "📄" },
};

function getContent(event) {
  const d = event.data || {};
  if (event.type === "token") return d.token || "";
  if (event.type === "tool_start") return `Tool: ${d.tool}\nInput: ${d.input || ""}`;
  if (event.type === "tool_end") return d.output || "";
  if (event.type === "tool_error") return d.error || "";
  if (event.type === "agent_finish") return d.output || "";
  if (event.type === "error") return d.error || "";
  if (event.type === "status") return d.message || JSON.stringify(d);
  return d.text || JSON.stringify(d);
}

function EventCard({ event, index }) {
  const cfg = EVENT_CONFIG[event.type] || EVENT_CONFIG.raw;
  const content = getContent(event);
  if (event.type === "token" && !content.trim()) return null;

  const ts = event.timestamp
    ? new Date(event.timestamp).toLocaleTimeString()
    : "";

  return (
    <div className={`flex gap-3 animate-slide-in`}>
      <div className="flex flex-col items-center">
        <div className={`text-base leading-none mt-0.5`}>{cfg.icon}</div>
        {index !== undefined && (
          <div className="w-px flex-1 bg-white/5 mt-2" />
        )}
      </div>
      <div className={`flex-1 rounded-lg border px-4 py-3 mb-2 ${cfg.bg} ${cfg.border}`}>
        <div className="flex items-center justify-between mb-1">
          <span className={`text-xs font-semibold uppercase tracking-wider ${cfg.text}`}>
            {cfg.label}
          </span>
          <span className="text-xs text-slate-600">{ts}</span>
        </div>
        <pre className={`text-xs whitespace-pre-wrap break-words font-mono ${cfg.text} opacity-90`}>
          {content.length > 600 ? content.slice(0, 600) + "…" : content}
        </pre>
      </div>
    </div>
  );
}

export default function EventTimeline({ events = [] }) {
  if (!events.length) {
    return (
      <div className="flex flex-col items-center justify-center py-16 text-slate-500">
        <div className="text-3xl mb-3">⚡</div>
        <p className="text-sm">Waiting for agent events…</p>
      </div>
    );
  }

  // For token events, collapse consecutive tokens into one block
  const collapsed = [];
  let tokenBuffer = "";
  let lastTs = null;

  for (const evt of events) {
    if (evt.type === "token") {
      tokenBuffer += evt.data?.token || "";
      lastTs = evt.timestamp;
    } else {
      if (tokenBuffer) {
        collapsed.push({ type: "token", timestamp: lastTs, data: { token: tokenBuffer } });
        tokenBuffer = "";
      }
      collapsed.push(evt);
    }
  }
  if (tokenBuffer) collapsed.push({ type: "token", timestamp: lastTs, data: { token: tokenBuffer } });

  return (
    <div className="space-y-0">
      {collapsed.map((evt, i) => (
        <EventCard key={i} event={evt} index={i} />
      ))}
    </div>
  );
}
