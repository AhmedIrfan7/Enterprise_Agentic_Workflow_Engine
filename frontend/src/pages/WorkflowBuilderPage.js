import React, { useEffect } from "react";
import WorkflowBuilder from "../components/workflow/WorkflowBuilder";
import WorkflowList from "../components/workflow/WorkflowList";
import { listWorkflows } from "../services/api";
import { useWorkflowStore } from "../context/useStore";

export default function WorkflowBuilderPage() {
  const setWorkflows = useWorkflowStore((s) => s.setWorkflows);

  useEffect(() => {
    listWorkflows().then((data) => setWorkflows(data.items || [])).catch(() => {});
  }, [setWorkflows]);

  return (
    <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
      <div className="xl:col-span-2">
        <WorkflowBuilder />
      </div>
      <div>
        <WorkflowList />
      </div>
    </div>
  );
}
