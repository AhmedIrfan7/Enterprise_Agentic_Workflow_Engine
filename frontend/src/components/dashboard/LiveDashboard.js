import React, { useEffect, useRef } from "react";
import { useParams } from "react-router-dom";
import { useExecutionStore, useWorkflowStore } from "../../context/useStore";
import { useWorkflowWebSocket } from "../../hooks/useWebSocket";
import { getWorkflow } from "../../services/api";
import EventTimeline from "./EventTimeline";
import MarkdownResult from "./MarkdownResult";
import Spinner from "../common/Spinner";
import ErrorBoundary from "../common/ErrorBoundary";

const STATUS_BADGE = {
  pending:   "bg-yellow-500/10 text-yellow-400 border-yellow-500/20",
  running:   "bg-blue-500/10  text-blue-400  border-blue-500/20",
  completed: "bg-green-500/10 text-green-400 border-green-500/20",
  failed:    "bg-red-500/10   text-red-400   border-red-500/20",
  cancelled: "bg-slate-500/10 text-slate-400 border-slate-500/20",
};

export default function LiveDashboard() {
  const { workflowId } = useParams();
  const workflows = useWorkflowStore((s) => s.workflows);
  const updateWorkflow = useWorkflowStore((s) => s.updateWorkflow);
  const events = useExecutionStore((s) => s.events[workflowId] || []);
  const wsStatus = useExecutionStore((s) => s.wsStatus[workflowId] || "idle");
  const scrollRef = useRef(null);

  const workflow = workflows.find((w) => w.id === workflowId);

  useWorkflowWebSocket(workflowId);

  // Poll for final result when agent finishes
  useEffect(() => {
    const finished = events.some((e) => e.type === "agent_finish" || e.type === "error");
    if (finished && workflowId) {
      getWorkflow(workflowId).then((w) => updateWorkflow(workflowId, w)).catch(() => {});
    }
  }, [events, workflowId, updateWorkflow]);

  // Auto-scroll timeline
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [events]);

  const finalEvent = events.find((e) => e.type === "agent_finish");
  const finalOutput = finalEvent?.data?.output || workflow?.result;
  const isRunning = wsStatus === "connected" || wsStatus === "connecting";

  return (
    <ErrorBoundary>
      <div className="max-w-5xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-start justify-between gap-4">
          <div>
            <h1 className="text-xl font-bold text-white truncate">
              {workflow?.title || "Workflow Execution"}
            </h1>
            <p className="text-slate-400 text-sm mt-1 line-clamp-2">{workflow?.goal}</p>
          </div>
          <div className="flex flex-col items-end gap-2 shrink-0">
            {workflow?.status && (
              <span className={`badge border ${STATUS_BADGE[workflow.status]}`}>
                {isRunning && <Spinner size="sm" className="mr-1" />}
                {workflow.status}
              </span>
            )}
            <span className={`text-xs font-mono px-2 py-0.5 rounded border ${
              wsStatus === "connected" ? "text-green-400 border-green-500/20 bg-green-500/10" :
              wsStatus === "error" ? "text-red-400 border-red-500/20 bg-red-500/10" :
              "text-slate-400 border-white/10"
            }`}>
              WS: {wsStatus}
            </span>
          </div>
        </div>

        {/* Stats */}
        {workflow && (
          <div className="grid grid-cols-3 gap-3">
            {[
              { label: "Total Events", value: events.length },
              { label: "Tokens Used", value: workflow.token_usage?.toLocaleString() || "—" },
              { label: "Est. Cost", value: workflow.estimated_cost_usd ? `$${workflow.estimated_cost_usd.toFixed(4)}` : "—" },
            ].map(({ label, value }) => (
              <div key={label} className="card text-center">
                <div className="text-lg font-bold text-white">{value}</div>
                <div className="text-xs text-slate-500 mt-0.5">{label}</div>
              </div>
            ))}
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Timeline */}
          <div className="card flex flex-col">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-sm font-semibold text-white">Execution Timeline</h2>
              <span className="text-xs text-slate-500">{events.length} events</span>
            </div>
            <div
              ref={scrollRef}
              className="flex-1 overflow-y-auto max-h-[500px] pr-1"
            >
              <EventTimeline events={events} />
            </div>
          </div>

          {/* Final output */}
          <div className="flex flex-col gap-4">
            <div className="card flex-1">
              <h2 className="text-sm font-semibold text-white mb-4">Final Output</h2>
              {finalOutput ? (
                <MarkdownResult content={finalOutput} />
              ) : (
                <div className="flex flex-col items-center justify-center py-12 text-slate-500">
                  {isRunning ? (
                    <><Spinner size="lg" className="mb-3" /><p className="text-sm">Agent is working…</p></>
                  ) : (
                    <p className="text-sm">Output will appear here when the agent completes.</p>
                  )}
                </div>
              )}
            </div>

            {/* Model info */}
            {workflow && (
              <div className="card text-xs text-slate-500 space-y-1">
                <div>Model: <span className="text-slate-300 font-mono">{workflow.llm_model}</span></div>
                <div>Provider: <span className="text-slate-300">{workflow.llm_provider}</span></div>
                <div>ID: <span className="text-slate-300 font-mono text-xs">{workflow.id}</span></div>
              </div>
            )}
          </div>
        </div>
      </div>
    </ErrorBoundary>
  );
}
