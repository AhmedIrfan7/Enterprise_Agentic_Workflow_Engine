import React from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

export default function MarkdownResult({ content }) {
  if (!content) return null;
  return (
    <div className="card prose prose-invert prose-sm max-w-none
                    prose-headings:text-white prose-headings:font-semibold
                    prose-p:text-slate-300 prose-p:leading-relaxed
                    prose-a:text-brand-400 prose-a:no-underline hover:prose-a:underline
                    prose-code:text-brand-300 prose-code:bg-white/5 prose-code:px-1 prose-code:rounded
                    prose-pre:bg-surface-900 prose-pre:border prose-pre:border-white/10
                    prose-blockquote:border-brand-500 prose-blockquote:text-slate-400
                    prose-table:text-slate-300 prose-th:text-white prose-th:bg-surface-700
                    prose-strong:text-white">
      <ReactMarkdown remarkPlugins={[remarkGfm]}>{content}</ReactMarkdown>
    </div>
  );
}
