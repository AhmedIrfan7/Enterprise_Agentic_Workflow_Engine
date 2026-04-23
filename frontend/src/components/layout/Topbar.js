import React from "react";

export default function Topbar() {
  return (
    <header className="flex items-center justify-between px-6 py-3 border-b border-white/10 bg-surface-800/50 backdrop-blur-sm">
      <div className="flex items-center gap-2">
        <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-xs font-medium bg-green-500/10 text-green-400 border border-green-500/20">
          <span className="w-1.5 h-1.5 rounded-full bg-green-400 animate-pulse_slow" />
          API Online
        </span>
      </div>
      <div className="flex items-center gap-3">
        <a
          href="/api/docs"
          target="_blank"
          rel="noreferrer"
          className="text-xs text-slate-500 hover:text-brand-400 transition-colors"
        >
          API Docs ↗
        </a>
        <div className="h-4 w-px bg-white/10" />
        <span className="text-xs text-slate-500">v1.0.0</span>
      </div>
    </header>
  );
}
