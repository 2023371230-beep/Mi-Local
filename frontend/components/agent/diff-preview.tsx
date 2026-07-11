export function DiffPreview() {
  return (
    <pre className="rounded-lg border border-border bg-black/45 p-4 font-mono text-xs leading-6 text-emerald-100">
      <span className="text-muted-foreground">diff --git a/app/example.tsx b/app/example.tsx</span>{"\n"}
      <span className="text-emerald-200">+ propuesta visual antes de aplicar cambios</span>{"\n"}
      <span className="text-rose-200">- ninguna edicion real se ejecuta todavia</span>{"\n"}
      <span className="text-cyan-100">+ aprobacion requerida antes de tocar archivos</span>
    </pre>
  );
}
