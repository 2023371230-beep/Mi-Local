"use client";

import { PanelRightClose, Search } from "lucide-react";
import { useEffect, useState } from "react";
import { useChatStore } from "@/lib/stores/chat-store";
import { useUiStore } from "@/lib/stores/ui-store";
import { Button } from "@/components/ui/button";
import { ContextDrawer } from "@/components/ui/context-drawer";
import { EmptyState } from "@/components/ui/empty-state";
import { SourcesPanel } from "@/components/chat/sources-panel";

export function RightContextPanel({
  open,
  onOpenChange,
}: {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}) {
  const sources = useChatStore((state) => state.sources);
  const rightPanelEnabled = useUiStore((state) => state.rightPanel);
  const [wide, setWide] = useState(false);

  useEffect(() => {
    const query = window.matchMedia("(min-width: 1280px)");
    const update = () => setWide(query.matches);
    update();
    query.addEventListener("change", update);
    return () => query.removeEventListener("change", update);
  }, []);

  const shouldShowDesktop = wide && rightPanelEnabled && (open || sources.length > 0);

  return (
    <>
      {shouldShowDesktop ? (
        <aside className="hidden w-80 shrink-0 border-l border-border bg-card/45 xl:block">
          <div className="flex h-full flex-col">
            <div className="flex h-12 items-center justify-between border-b border-border px-3">
              <div>
                <div className="text-sm font-medium">Contexto</div>
                <div className="font-mono text-[11px] text-muted-foreground">{sources.length} fuentes</div>
              </div>
              <Button variant="ghost" size="icon-sm" onClick={() => onOpenChange(false)} aria-label="Cerrar panel derecho">
                <PanelRightClose className="size-4" />
              </Button>
            </div>
            {sources.length > 0 ? (
              <SourcesPanel sources={sources} embedded />
            ) : (
              <div className="p-3">
                <EmptyState icon={Search} title="Sin contexto activo" description="Las fuentes RAG o web apareceran aqui cuando una respuesta las use." compact />
              </div>
            )}
          </div>
        </aside>
      ) : null}
      <ContextDrawer open={open && !wide} onOpenChange={onOpenChange} title="Contexto" description={`${sources.length} fuentes activas`}>
        <SourcesPanel sources={sources} embedded />
      </ContextDrawer>
    </>
  );
}
