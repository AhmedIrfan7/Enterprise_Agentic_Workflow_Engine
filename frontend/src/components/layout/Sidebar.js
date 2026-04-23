import React, { useState } from "react";
import { NavLink } from "react-router-dom";

const NAV = [
  { to: "/workflows", label: "Workflow Builder", icon: "⚡" },
  { to: "/vault", label: "Data Vault", icon: "🗄️" },
  { to: "/logs", label: "Execution Logs", icon: "📋" },
];

export default function Sidebar() {
  const [collapsed, setCollapsed] = useState(false);

  return (
    <aside
      className={`flex flex-col bg-surface-800 border-r border-white/10 transition-all duration-300 ${
        collapsed ? "w-14" : "w-56"
      } shrink-0`}
    >
      {/* Logo */}
      <div className="flex items-center gap-3 px-4 py-5 border-b border-white/10">
        <span className="text-xl">🤖</span>
        {!collapsed && (
          <span className="text-sm font-semibold text-white leading-tight">
            Agentic<br />
            <span className="text-brand-400">Workflow Engine</span>
          </span>
        )}
      </div>

      {/* Nav */}
      <nav className="flex-1 py-4 space-y-1 px-2">
        {NAV.map(({ to, label, icon }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors duration-150 ${
                isActive
                  ? "bg-brand-600/30 text-brand-400 border border-brand-500/40"
                  : "text-slate-400 hover:text-white hover:bg-white/5"
              }`
            }
          >
            <span className="text-base leading-none">{icon}</span>
            {!collapsed && <span className="truncate">{label}</span>}
          </NavLink>
        ))}
      </nav>

      {/* Collapse toggle */}
      <button
        onClick={() => setCollapsed((c) => !c)}
        className="flex items-center justify-center h-10 border-t border-white/10 text-slate-500 hover:text-white transition-colors"
        aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}
      >
        {collapsed ? "→" : "←"}
      </button>
    </aside>
  );
}
