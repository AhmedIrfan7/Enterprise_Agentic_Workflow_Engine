import React, { useState } from "react";
import { getLogs } from "../services/api";
import { useWorkflowStore } from "../context/useStore";
import Spinner from "../components/common/Spinner";

const LEVEL_STYLE = {
  info:    "text-blue-400 bg-blue-500/10",
  debug:   "text-slate-400 bg-slate-500/10",
  warning: "text-yellow-400 bg-yellow-500/10",
  error:   "text-red-400 bg-red-500/10",
};

export default function LogsPage() {
  const workflows = useWorkflowStore((s) => s.workflows);
  const [selectedId, setSelectedId] = useState("");
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchLogs = async (id) => {
    if (!id) return;
    setLoading(true);
    setError(null);
    try {
      const data = await getLogs(id);
      setLogs(data.items || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSelect = (e) => {
    const id = e.target.value;
    setSelectedId(id);
    fetchLogs(id);
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Execution Logs</h1>
        <p className="text-slate-400 text-sm mt-1">Inspect persisted event logs for any past workflow run.</p>
      </div>

      <div className="card">
        <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-2">
          Select Workflow
        </label>
        <select
          className="input-field"
          value={selectedId}
          onChange={handleSelect}
        >
          <option value="">— Choose a workflow —</option>
          {workflows.map((w) => (
            <option key={w.id} value={w.id}>
              {w.title} ({w.status}) — {new Date(w.created_at).toLocaleString()}
            </option>
          ))}
        </select>
      </div>

      {error && (
        <div className="bg-red-500/10 border border-red-500/30 rounded-lg px-4 py-3 text-red-400 text-sm">{error}</div>
      )}

      {loading ? (
        <div className="flex justify-center py-12"><Spinner size="lg" /></div>
      ) : logs.length > 0 ? (
        <div className="card space-y-2">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-sm font-semibold text-white">Log Entries</h2>
            <span className="text-xs text-slate-500">{logs.length} events</span>
          </div>
          {logs.map((log) => (
            <div key={log.id} className="flex gap-3 items-start py-2 border-b border-white/5 last:border-0">
              <span className={`badge shrink-0 mt-0.5 ${LEVEL_STYLE[log.level] || "text-slate-400"}`}>
                {log.level}
              </span>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-0.5">
                  <span className="text-xs font-mono text-brand-400">{log.event_type}</span>
                  <span className="text-xs text-slate-600">{new Date(log.created_at).toLocaleTimeString()}</span>
                </div>
                <p className="text-sm text-slate-300 break-words">{log.message}</p>
                {log.metadata_json && (
                  <pre className="text-xs text-slate-500 mt-1 font-mono break-all whitespace-pre-wrap">
                    {log.metadata_json.length > 300 ? log.metadata_json.slice(0, 300) + "…" : log.metadata_json}
                  </pre>
                )}
              </div>
            </div>
          ))}
        </div>
      ) : selectedId ? (
        <div className="text-center text-slate-500 py-12">No logs found for this workflow.</div>
      ) : null}
    </div>
  );
}
