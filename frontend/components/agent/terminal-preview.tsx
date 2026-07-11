export function TerminalPreview() {
  return (
    <pre className="muted-grid-bg rounded-lg border border-border bg-black/45 p-4 font-mono text-xs leading-6 text-cyan-100">
      $ npm run lint{"\n"}
      $ npm run build{"\n"}
      $ pytest{"\n"}
      <span className="text-muted-foreground">commands require approval in future agent mode</span>
    </pre>
  );
}
