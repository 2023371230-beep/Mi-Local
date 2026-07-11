import { Button } from "@/components/ui/button";
import { StatusBadge } from "@/components/ui/status-badge";

export function ApprovalCard() {
  return (
    <div className="surface rounded-lg p-4">
      <div className="text-sm font-medium">Permisos planeados</div>
      <p className="mt-1 text-sm leading-6 text-muted-foreground">El agente futuro trabajara con aprobaciones explicitas.</p>
      <div className="mt-4 space-y-2">
        <StatusBadge label="Read-only" tone="ok" withIcon />
        <StatusBadge label="Suggest" tone="info" withIcon />
        <StatusBadge label="Apply with approval" tone="warning" withIcon />
        <StatusBadge label="Commands with approval" tone="degraded" withIcon />
      </div>
      <Button className="mt-4 w-full" disabled>Activar modo agente proximamente</Button>
    </div>
  );
}
