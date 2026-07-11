"use client";

import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import rehypeHighlight from "rehype-highlight";
import "highlight.js/styles/github-dark.css";

export function MarkdownMessage({ content }: { content: string }) {
  return (
    <ReactMarkdown
      remarkPlugins={[remarkGfm]}
      rehypePlugins={[rehypeHighlight]}
      components={{
        pre: ({ children }) => <pre className="overflow-x-auto rounded-md border border-border bg-black/40 p-3 text-xs">{children}</pre>,
        code: ({ children, className }) => <code className={className ?? "rounded bg-muted px-1 py-0.5 font-mono text-xs"}>{children}</code>,
        p: ({ children }) => <p className="mb-2 last:mb-0">{children}</p>,
      }}
    >
      {content}
    </ReactMarkdown>
  );
}
