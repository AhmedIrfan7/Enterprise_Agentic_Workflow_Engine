import { create } from "zustand";

export const useWorkflowStore = create((set, get) => ({
  workflows: [],
  activeWorkflowId: null,
  isLoading: false,
  error: null,

  setWorkflows: (workflows) => set({ workflows }),
  addWorkflow: (workflow) => set((s) => ({ workflows: [workflow, ...s.workflows] })),
  updateWorkflow: (id, patch) =>
    set((s) => ({ workflows: s.workflows.map((w) => (w.id === id ? { ...w, ...patch } : w)) })),
  setActiveWorkflow: (id) => set({ activeWorkflowId: id }),
  setLoading: (isLoading) => set({ isLoading }),
  setError: (error) => set({ error }),
}));

export const useExecutionStore = create((set) => ({
  events: {},
  wsStatus: {},

  appendEvent: (workflowId, event) =>
    set((s) => ({
      events: {
        ...s.events,
        [workflowId]: [...(s.events[workflowId] || []), event],
      },
    })),
  clearEvents: (workflowId) =>
    set((s) => ({ events: { ...s.events, [workflowId]: [] } })),
  setWsStatus: (workflowId, status) =>
    set((s) => ({ wsStatus: { ...s.wsStatus, [workflowId]: status } })),
}));
