import React, { useState, useEffect, useRef } from "react";
import { listDocuments, uploadDocument, deleteDocument } from "../../services/api";
import Spinner from "../common/Spinner";

function formatBytes(bytes) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / 1024 / 1024).toFixed(2)} MB`;
}

export default function DataVault() {
  const [docs, setDocs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [error, setError] = useState(null);
  const [successMsg, setSuccessMsg] = useState(null);
  const fileInputRef = useRef(null);

  const fetchDocs = async () => {
    try {
      const data = await listDocuments();
      setDocs(data.items || []);
    } catch {
      setError("Failed to load documents.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchDocs(); }, []);

  const handleUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    setError(null);
    setUploadProgress(0);
    try {
      await uploadDocument(file, setUploadProgress);
      setSuccessMsg(`"${file.name}" uploaded and queued for embedding.`);
      setTimeout(() => setSuccessMsg(null), 4000);
      fetchDocs();
    } catch (err) {
      setError(err.message);
    } finally {
      setUploading(false);
      setUploadProgress(0);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  };

  const handleDelete = async (filename) => {
    if (!window.confirm(`Delete "${filename}" from the vault?`)) return;
    try {
      await deleteDocument(filename);
      setDocs((d) => d.filter((f) => f.filename !== filename));
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Data Vault</h1>
        <p className="text-slate-400 text-sm mt-1">
          Upload documents to the vector knowledge base. The agent can query them via the{" "}
          <code className="text-brand-400">query_knowledge_base</code> tool.
        </p>
      </div>

      {error && (
        <div className="bg-red-500/10 border border-red-500/30 rounded-lg px-4 py-3 text-red-400 text-sm">
          {error}
        </div>
      )}
      {successMsg && (
        <div className="bg-green-500/10 border border-green-500/30 rounded-lg px-4 py-3 text-green-400 text-sm">
          ✅ {successMsg}
        </div>
      )}

      {/* Upload zone */}
      <div
        className="card border-dashed border-2 border-white/20 hover:border-brand-500/50 transition-colors cursor-pointer text-center py-8"
        onClick={() => !uploading && fileInputRef.current?.click()}
      >
        <input
          ref={fileInputRef}
          type="file"
          className="hidden"
          accept=".pdf,.txt,.csv,.json,.docx"
          onChange={handleUpload}
          disabled={uploading}
        />
        {uploading ? (
          <div className="space-y-3">
            <Spinner size="lg" className="mx-auto" />
            <p className="text-sm text-slate-400">Uploading… {uploadProgress}%</p>
            <div className="w-full bg-surface-700 rounded-full h-1.5 mx-auto max-w-xs">
              <div
                className="bg-brand-500 h-1.5 rounded-full transition-all duration-300"
                style={{ width: `${uploadProgress}%` }}
              />
            </div>
          </div>
        ) : (
          <div className="space-y-2">
            <div className="text-3xl">📁</div>
            <p className="text-white font-medium">Click to upload a document</p>
            <p className="text-xs text-slate-500">Supported: PDF, TXT, CSV, JSON, DOCX · Max 50MB</p>
          </div>
        )}
      </div>

      {/* Document list */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-sm font-semibold text-white">Indexed Documents</h2>
          <span className="text-xs text-slate-500">{docs.length} files</span>
        </div>
        {loading ? (
          <div className="flex justify-center py-8"><Spinner /></div>
        ) : docs.length === 0 ? (
          <p className="text-sm text-slate-500 text-center py-8 italic">No documents uploaded yet.</p>
        ) : (
          <ul className="space-y-2">
            {docs.map((doc) => (
              <li
                key={doc.filename}
                className="flex items-center justify-between px-3 py-2.5 rounded-lg bg-surface-900 border border-white/5"
              >
                <div className="flex items-center gap-3 min-w-0">
                  <span className="text-lg shrink-0">📄</span>
                  <div className="min-w-0">
                    <div className="text-sm text-white truncate">{doc.filename}</div>
                    <div className="text-xs text-slate-500">{formatBytes(doc.size_bytes)}</div>
                  </div>
                </div>
                <button
                  onClick={() => handleDelete(doc.filename)}
                  className="text-xs text-red-400 hover:text-red-300 px-2 py-1 rounded hover:bg-red-500/10 transition-colors ml-2 shrink-0"
                >
                  Delete
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
