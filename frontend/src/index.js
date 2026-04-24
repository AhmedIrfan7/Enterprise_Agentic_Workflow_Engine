import React from "react";
import { createRoot } from "react-dom/client";
import "./index.css";

// Catch any global JS errors and show them instead of blank page
window.onerror = function (msg, src, line, col, err) {
  const root = document.getElementById("root");
  if (root) {
    root.innerHTML = `<div style="font-family:monospace;padding:2rem;color:#f87171;background:#0f172a;min-height:100vh">
      <h2 style="color:#fbbf24;margin-bottom:1rem">&#9888; Runtime Error (window.onerror)</h2>
      <pre style="white-space:pre-wrap;font-size:13px;color:#fca5a5">${msg}\n${src}:${line}:${col}\n${err?.stack || ""}</pre>
    </div>`;
  }
  return true;
};

window.addEventListener("unhandledrejection", function (e) {
  const root = document.getElementById("root");
  if (root && !root.querySelector("h2")) {
    root.innerHTML = `<div style="font-family:monospace;padding:2rem;color:#f87171;background:#0f172a;min-height:100vh">
      <h2 style="color:#fbbf24;margin-bottom:1rem">&#9888; Unhandled Promise Rejection</h2>
      <pre style="white-space:pre-wrap;font-size:13px;color:#fca5a5">${e.reason?.stack || String(e.reason)}</pre>
    </div>`;
  }
});

import("./App").then(({ default: App }) => {
  const container = document.getElementById("root");
  const root = createRoot(container);
  root.render(
    <React.StrictMode>
      <App />
    </React.StrictMode>
  );
}).catch((err) => {
  const container = document.getElementById("root");
  if (container) {
    container.innerHTML = `<div style="font-family:monospace;padding:2rem;color:#f87171;background:#0f172a;min-height:100vh">
      <h2 style="color:#fbbf24;margin-bottom:1rem">&#9888; Module Import Error</h2>
      <pre style="white-space:pre-wrap;font-size:13px;color:#fca5a5">${err?.stack || String(err)}</pre>
    </div>`;
  }
});
