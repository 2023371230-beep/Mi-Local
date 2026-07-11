import { PanelRightOpen } from "lucide-react";
import { Button } from "@/components/ui/button";
import { StatusBadge } from "@/components/ui/status-badge";

export function ContextPanelToggle({ count, onClick }: { count: number; onClick: () => void }) {
  return (
    <Button variant="secondary" size="sm" onClick={onClick} aria-label="Abrir contexto">
      <PanelRightOpen className="size-4" />
      Contexto
      {count > 0 ? <StatusBadge label={String(count)} tone="info" compact className="ml-1 h-5 px-1" /> : null}
    </Button>
  );
}
