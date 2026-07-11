import { Cpu } from "lucide-react";
import { StatusBadge } from "@/components/ui/status-badge";

function humanSize(value: unknown) {
  const size = Number(value);
  if (!Number.isFinite(size) || size <= 0) return "tamano n/d";
  const gb = size / 1024 / 1024 / 1024;
  if (gb >= 1) return `${gb.toFixed(2)} GB`;
  return `${(size / 1024 / 1024).toFixed(1)} MB`;
}

function modelRole(name: string) {
  const lower = name.toLowerCase();
  if (lower.includes("coder")) return { role: "coder", use: "Programacion, debugging, APIs y bases de datos" };
  if (lower.includes("embedding") || lower.includes("bge")) return { role: "embedding", use: lower.includes("bge") ? "RAG alternativo multilingue" : "RAG ligero y embeddings locales" };
  if (lower.includes("llama3.2")) return { role: "auxiliar/router", use: "Router ligero y tareas auxiliares" };
  if (lower.includes("qwen2.5")) return { role: "general", use: "Redes, ciberseguridad, teoria y respuestas generales" };
  return { role: "modelo", use: "Modelo local disponible en Ollama" };
}

export function ModelCard({ model }: { model: Record<string, unknown> }) {
  const details = (model.details ?? {}) as Record<string, unknown>;
  const name = String(model.name ?? model.model ?? "modelo");
  const role = modelRole(name);
  const recommended = ["qwen2.5:7b", "qwen2.5-coder:7b", "qwen3-embedding:0.6b", "llama3.2"].some((item) => name.includes(item));

  return (
    <div className="surface rounded-lg p-4">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <h3 className="truncate text-base font-semibold">{name}</h3>
          <p className="mt-1 text-sm text-muted-foreground">{role.use}</p>
        </div>
        <div className="rounded-md border border-border bg-background/60 p-2 text-primary">
          <Cpu className="size-4" />
        </div>
      </div>
      <div className="mt-4 flex flex-wrap gap-2">
        <StatusBadge label={role.role} tone={recommended ? "ok" : "idle"} compact />
        <StatusBadge label={String(details.parameter_size ?? "params n/d")} tone="info" compact />
        <StatusBadge label={String(details.quantization_level ?? "quant n/d")} tone="idle" compact />
        <StatusBadge label={String(details.family ?? "family n/d")} tone="idle" compact />
      </div>
      <p className="mt-4 font-mono text-xs text-muted-foreground">{humanSize(model.size)}</p>
    </div>
  );
}
