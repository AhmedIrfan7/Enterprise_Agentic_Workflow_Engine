import { useEffect, useRef, useCallback } from "react";
import { createWebSocket } from "../services/api";
import { useExecutionStore } from "../context/useStore";

export function useWorkflowWebSocket(workflowId) {
  const wsRef = useRef(null);
  const appendEvent = useExecutionStore((s) => s.appendEvent);
  const setWsStatus = useExecutionStore((s) => s.setWsStatus);

  const connect = useCallback(() => {
    if (!workflowId) return;
    if (wsRef.current?.readyState === WebSocket.OPEN) return;

    setWsStatus(workflowId, "connecting");
    const ws = createWebSocket(workflowId);
    wsRef.current = ws;

    ws.onopen = () => setWsStatus(workflowId, "connected");

    ws.onmessage = (evt) => {
      try {
        const event = JSON.parse(evt.data);
        appendEvent(workflowId, event);
      } catch {
        appendEvent(workflowId, { type: "raw", data: { text: evt.data } });
      }
    };

    ws.onerror = () => setWsStatus(workflowId, "error");

    ws.onclose = () => setWsStatus(workflowId, "closed");
  }, [workflowId, appendEvent, setWsStatus]);

  const disconnect = useCallback(() => {
    wsRef.current?.close();
  }, []);

  useEffect(() => {
    connect();
    return () => disconnect();
  }, [connect, disconnect]);

  return { connect, disconnect };
}
