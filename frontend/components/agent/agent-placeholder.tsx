import { AlertTriangle, GitPullRequestDraft } from "lucide-react";
import { ApprovalCard } from "@/components/agent/approval-card";
import { DiffPreview } from "@/components/agent/diff-preview";
import { FileExplorerPreview } from "@/components/agent/file-explorer-preview";
import { TerminalPreview } from "@/components/agent/terminal-preview";
import { SectionHeader } from "@/components/ui/section-header";
import { StatusBadge } from "@/components/ui/status-badge";
import { CommandCard } from "@/components/ui/command-card";
import { pageShell } from "@/lib/config/design-tokens";

const timeline = ["Abrir carpeta", "Indexar proyecto", "Planear cambios", "Ver diff", "Aprobar", "Ejecutar pruebas"];

export function AgentPlaceholder() {
  return (
    <div className={pageShell}>
      <SectionHeader
        eyebrow="Agent"
        title="Modo agente planeado"
        description="Vista premium del modulo futuro. No ejecuta acciones reales todavia."
        actions={<StatusBadge label="No ejecuta acciones reales todavia" tone="warning" withIcon />}
      />
      <div className="grid gap-4 lg:grid-cols-[280px_1fr_300px]">
        <FileExplorerPreview />
        <div className="space-y-4">
          <CommandCard icon={GitPullRequestDraft} title="Diff preview" description="Los cambios se revisaran antes de aprobarse.">
            <DiffPreview />
          </CommandCard>
          <CommandCard icon={AlertTriangle} title="Timeline de capacidades" description="Secuencia esperada para el modo agente real.">
            <div className="grid gap-2 sm:grid-cols-2">
              {timeline.map((item, index) => (
                <div key={item} className="surface-muted rounded-md border p-3 text-sm">
                  <span className="mr-2 font-mono text-xs text-primary">{index + 1}</span>{item}
                </div>
              ))}
            </div>
          </CommandCard>
          <TerminalPreview />
        </div>
        <ApprovalCard />
      </div>
    </div>
  );
}
