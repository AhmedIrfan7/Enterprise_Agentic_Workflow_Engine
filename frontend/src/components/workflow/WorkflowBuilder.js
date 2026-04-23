import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { listTools, createWorkflow } from "../../services/api";
import { useWorkflowStore } from "../../context/useStore";
import Spinner from "../common/Spinner";

const LLM_OPTIONS = [
  { provider: "openai", model: "gpt-4o-mini", label: "GPT-4o Mini (Fast & Cheap)" },
  { provider: "openai", model: "gpt-4o", label: "GPT-4o (Flagship)" },
  { provider: "openai", model: "gpt-4-turbo", label: "GPT-4 Turbo" },
  { provider: "ollama", model: "llama3", label: "Llama 3 (Local — Ollama)" },
];

export default function WorkflowBuilder() {
  const navigate = useNavigate();
  const addWorkflow = useWorkflowStore((s) => s.addWorkflow);

  const [title, setTitle] = useState("");
  const [goal, setGoal] = useState("");
  const [selectedTools, setSelectedTools] = useState([]);
  const [selectedLLM, setSelectedLLM] = useState(LLM_OPTIONS[0]);
  const [availableTools, setAvailableTools] = useState([]);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    listTools().then((data) => setAvailableTools(data.items || [])).catch(() => {});
  }, []);

  const toggleTool = (id) =>
    setSelectedTools((prev) =>
      prev.includes(id) ? prev.filter((t) => t !== id) : [...prev, id]
    );

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!goal.trim()) return;
    setSubmitting(true);
    setError(null);
    try {
      const workflow = await createWorkflow({
        title: title || `Workflow — ${new Date().toLocaleString()}`,
        goal,
        tools_selected: selectedTools,
        llm_provider: selectedLLM.provider,
        llm_model: selectedLLM.model,
      });
      addWorkflow(workflow);
      navigate(`/dashboard/${workflow.id}`);
    } catch (err) {
      setError(err.message);
      setSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="max-w-3xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">New Workflow</h1>
        <p className="text-slate-400 text-sm mt-1">
          Define your agent's goal, select tools, and launch execution.
        </p>
      </div>

      {error && (
        <div className="bg-red-500/10 border border-red-500/30 rounded-lg px-4 py-3 text-red-400 text-sm">
          {error}
        </div>
      )}

      {/* Title */}
      <div className="card space-y-3">
        <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
          Workflow Title (optional)
        </label>
        <input
          type="text"
          className="input-field"
          placeholder="E.g., Competitive Analysis — Q2 2024"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
        />
      </div>

      {/* Goal */}
      <div className="card space-y-3">
        <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
          Agent Goal <span className="text-red-400">*</span>
        </label>
        <textarea
          className="input-field min-h-[120px] resize-y"
          placeholder="Describe exactly what you want the agent to accomplish. Be specific — more context leads to better results.&#10;&#10;Example: Research the top 5 AI startups in healthcare in 2024, compile their funding rounds, key products, and founding team. Output a structured report as a markdown table."
          value={goal}
          onChange={(e) => setGoal(e.target.value)}
          required
          minLength={10}
        />
        <p className="text-xs text-slate-500">{goal.length} characters</p>
      </div>

      {/* LLM */}
      <div className="card space-y-3">
        <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
          LLM Provider & Model
        </label>
        <div className="grid grid-cols-2 gap-2">
          {LLM_OPTIONS.map((opt) => (
            <button
              key={opt.model}
              type="button"
              onClick={() => setSelectedLLM(opt)}
              className={`text-left px-3 py-2.5 rounded-lg border text-sm transition-all ${
                selectedLLM.model === opt.model
                  ? "border-brand-500 bg-brand-600/20 text-white"
                  : "border-white/10 text-slate-400 hover:border-white/20 hover:text-slate-200"
              }`}
            >
              <div className="font-medium">{opt.label}</div>
              <div className="text-xs opacity-60 mt-0.5">{opt.model}</div>
            </button>
          ))}
        </div>
      </div>

      {/* Tools */}
      <div className="card space-y-3">
        <div className="flex items-center justify-between">
          <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
            Agent Tools
          </label>
          <span className="text-xs text-slate-500">
            {selectedTools.length > 0 ? `${selectedTools.length} selected` : "All tools (default)"}
          </span>
        </div>
        <div className="grid grid-cols-2 gap-2">
          {availableTools.map((tool) => (
            <button
              key={tool.id}
              type="button"
              onClick={() => toggleTool(tool.id)}
              className={`text-left px-3 py-2.5 rounded-lg border text-sm transition-all ${
                selectedTools.includes(tool.id)
                  ? "border-brand-500 bg-brand-600/20 text-white"
                  : "border-white/10 text-slate-400 hover:border-white/20"
              }`}
            >
              <div className="font-medium font-mono text-xs text-brand-300">{tool.id}</div>
              <div className="text-xs opacity-60 mt-0.5 line-clamp-2">{tool.description}</div>
            </button>
          ))}
        </div>
        {availableTools.length === 0 && (
          <p className="text-xs text-slate-500 italic">Loading tools… (backend must be running)</p>
        )}
      </div>

      <button type="submit" disabled={submitting || !goal.trim()} className="btn-primary w-full justify-center py-3 text-base">
        {submitting ? <><Spinner size="sm" /> Launching Agent…</> : "⚡ Launch Agentic Workflow"}
      </button>
    </form>
  );
}
