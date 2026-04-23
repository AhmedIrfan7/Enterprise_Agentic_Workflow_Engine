import React from "react";
import { Link } from "react-router-dom";
import { useWorkflowStore } from "../../context/useStore";
import { deleteWorkflow } from "../../services/api";

const STATUS_STYLE = {
  pending:   "text-yellow-400 bg-yellow-500/10 border-yellow-500/20",
  running:   "text-blue-400 bg-blue-500/10 border-blue-500/20",
  completed: "text-green-400 bg-green-500/10 border-green-500/20",
  failed:    "text-red-400 bg-red-500/10 border-red-500/20",
  cancelled: "text-slate-400 bg-slate-500/10 border-slate-500/20",
};

export default function WorkflowList() {
  const workflows = useWorkflowStore((s) => s.workflows);
  const removeWorkflow = useWorkflowStore((s) => s.setWorkflows);
  const store = useWorkflowStore();

  const handleDelete = async (e, id) => {
    e.preventDefault();
    if (!window.confirm("Delete this workflow?")) return;
    try {
      await deleteWorkflow(id);
      store.setWorkflows(workflows.filter((w) => w.id !== id));
    } catch {}
  };

  return (
    <div className="card h-full">
      <h2 className="text-sm font-semibold text-white mb-4">Recent Workflows</h2>
      {workflows.length === 0 ? (
        <p className="text-sm text-slate-500 italic text-center py-8">
          No workflows yet. Create one to get started.
        </p>
      ) : (
        <ul className="space-y-2">
          {workflows.slice(0, 15).map((w) => (
            <li key={w.id}>
              <Link
                to={`/dashboard/${w.id}`}
                className="flex items-start gap-3 p-3 rounded-lg border border-white/5 hover:border-brand-500/30 hover:bg-brand-600/5 transition-all group"
              >
                <div className="flex-1 min-w-0">
                  <div className="text-sm font-medium text-white truncate group-hover:text-brand-300 transition-colors">
                    {w.title}
                  </div>
                  <div className="text-xs text-slate-500 mt-0.5">
                    {new Date(w.created_at).toLocaleDateString()}
                  </div>
                </div>
                <div className="flex items-center gap-2 shrink-0">
                  <span className={`badge border ${STATUS_STYLE[w.status] || STATUS_STYLE.pending}`}>
                    {w.status}
                  </span>
                  <button
                    onClick={(e) => handleDelete(e, w.id)}
                    className="text-xs text-slate-600 hover:text-red-400 transition-colors px-1"
                  >
                    ×
                  </button>
                </div>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
