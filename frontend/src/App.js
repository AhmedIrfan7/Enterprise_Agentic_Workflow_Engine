import React from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Layout from "./components/layout/Layout";
import WorkflowBuilderPage from "./pages/WorkflowBuilderPage";
import DashboardPage from "./pages/DashboardPage";
import DataVaultPage from "./pages/DataVaultPage";
import LogsPage from "./pages/LogsPage";
import ErrorBoundary from "./components/common/ErrorBoundary";

export default function App() {
  return (
    <BrowserRouter>
      <ErrorBoundary>
        <Layout>
          <Routes>
            <Route path="/" element={<Navigate to="/workflows" replace />} />
            <Route path="/workflows" element={<WorkflowBuilderPage />} />
            <Route path="/dashboard/:workflowId" element={<DashboardPage />} />
            <Route path="/vault" element={<DataVaultPage />} />
            <Route path="/logs" element={<LogsPage />} />
          </Routes>
        </Layout>
      </ErrorBoundary>
    </BrowserRouter>
  );
}
