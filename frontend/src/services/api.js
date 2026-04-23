import axios from "axios";

const BASE_URL = process.env.API_BASE_URL || "http://localhost:8000";

const api = axios.create({
  baseURL: `${BASE_URL}/api/v1`,
  timeout: 30000,
  headers: { "Content-Type": "application/json" },
});

// Request interceptor — attach any future auth tokens here
api.interceptors.request.use((config) => config);

// Response interceptor — normalize errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const message =
      error.response?.data?.detail ||
      error.response?.data?.errors?.[0]?.msg ||
      error.message ||
      "An unknown error occurred.";
    return Promise.reject(new Error(message));
  }
);

// ---- Workflows ----
export const createWorkflow = (payload) => api.post("/workflows", payload).then((r) => r.data);
export const listWorkflows = (skip = 0, limit = 20) =>
  api.get("/workflows", { params: { skip, limit } }).then((r) => r.data);
export const getWorkflow = (id) => api.get(`/workflows/${id}`).then((r) => r.data);
export const deleteWorkflow = (id) => api.delete(`/workflows/${id}`);

// ---- Tools ----
export const listTools = () => api.get("/tools").then((r) => r.data);

// ---- Documents ----
export const uploadDocument = (file, onProgress) => {
  const form = new FormData();
  form.append("file", file);
  return api.post("/documents/upload", form, {
    headers: { "Content-Type": "multipart/form-data" },
    onUploadProgress: (e) => onProgress && onProgress(Math.round((e.loaded * 100) / e.total)),
  }).then((r) => r.data);
};
export const listDocuments = () => api.get("/documents/list").then((r) => r.data);
export const deleteDocument = (filename) => api.delete(`/documents/${encodeURIComponent(filename)}`);

// ---- Logs ----
export const getLogs = (workflowId, skip = 0, limit = 100) =>
  api.get(`/logs/${workflowId}`, { params: { skip, limit } }).then((r) => r.data);

// ---- WebSocket ----
export const createWebSocket = (workflowId) => {
  const wsBase = BASE_URL.replace(/^http/, "ws");
  return new WebSocket(`${wsBase}/ws/execution/${workflowId}`);
};

export default api;
