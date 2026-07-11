"use client";

import { useQuery } from "@tanstack/react-query";
import { toast } from "sonner";
import { Copy, RotateCcw, Wifi } from "lucide-react";
import { useUiStore } from "@/lib/stores/ui-store";
import { getHealth } from "@/lib/api/health";
import { Input } from "@/components/ui/input";
import { Switch } from "@/components/ui/switch";
import { Button } from "@/components/ui/button";
import { SectionHeader } from "@/components/ui/section-header";
import { CommandCard } from "@/components/ui/command-card";
import { StatusBadge } from "@/components/ui/status-badge";
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";
import type { ChatMode, RagMode } from "@/lib/types/api";
import { pageShell } from "@/lib/config/design-tokens";

const modes: ChatMode[] = ["auto", "programacion", "ui_ux", "ciberseguridad", "bases_datos", "rag", "web", "general"];
const ragModes: RagMode[] = ["auto", "true", "false"];

export default function SettingsPage() {
  const ui = useUiStore();
  const health = useQuery({ queryKey: ["health"], queryFn: getHealth, staleTime: 15_000 });
  const webSearch = health.data?.web_search ?? {};

  const exportSettings = async () => {
    const json = JSON.stringify(ui, null, 2);
    await navigator.clipboard.writeText(json);
    toast.success("Settings copiados como JSON");
  };

  const resetSettings = () => {
    localStorage.removeItem("modelo-ia-ui");
    toast.success("Settings locales reiniciados. Recarga la app para aplicar defaults.");
  };

  const testConnection = async () => {
    try {
      const response = await fetch(`${ui.backendUrl}/health`);
      toast.success(`Backend respondio ${response.status}`);
    } catch {
      toast.error("No se pudo conectar al backend configurado");
    }
  };

  return (
    <div className={pageShell}>
      <SectionHeader eyebrow="Settings" title="Preferencias locales" description="Configuracion persistente de UI, chat y comportamiento visual sin tocar endpoints backend." />
      <Accordion className="space-y-3">
        <AccordionItem value="backend" className="surface rounded-lg border p-4">
          <AccordionTrigger className="py-0 hover:no-underline">Backend</AccordionTrigger>
          <AccordionContent className="space-y-3 pt-4">
            <label className="space-y-1 text-sm text-muted-foreground">Backend URL<Input value={ui.backendUrl} onChange={(e) => ui.setState({ backendUrl: e.target.value })} /></label>
            <div className="flex flex-wrap gap-2">
              <Button variant="secondary" onClick={testConnection}>Probar conexion</Button>
              <StatusBadge label="api" tone={health.data?.status === "ok" ? "ok" : "error"} />
              <StatusBadge label="ollama" tone={health.data?.ollama ? "ok" : "error"} />
              <StatusBadge label="chroma" tone={health.data?.chroma ? "ok" : "error"} />
            </div>
          </AccordionContent>
        </AccordionItem>

        <AccordionItem value="chat" className="surface rounded-lg border p-4">
          <AccordionTrigger className="py-0 hover:no-underline">Chat</AccordionTrigger>
          <AccordionContent className="grid gap-3 pt-4 md:grid-cols-2">
            <label className="space-y-1 text-sm text-muted-foreground">Modo por defecto<select className="h-9 w-full rounded-md border border-input bg-background px-2 text-sm text-foreground" value={ui.defaultMode} onChange={(e) => ui.setState({ defaultMode: e.target.value as ChatMode })}>{modes.map((m) => <option key={m}>{m}</option>)}</select></label>
            <label className="space-y-1 text-sm text-muted-foreground">RAG por defecto<select className="h-9 w-full rounded-md border border-input bg-background px-2 text-sm text-foreground" value={ui.defaultRag} onChange={(e) => ui.setState({ defaultRag: e.target.value as RagMode })}>{ragModes.map((m) => <option key={m}>{m}</option>)}</select></label>
            <label className="space-y-1 text-sm text-muted-foreground">Coleccion<Input value={ui.defaultCollection} onChange={(e) => ui.setState({ defaultCollection: e.target.value })} /></label>
            <label className="space-y-1 text-sm text-muted-foreground">Top K<Input type="number" value={ui.topK} onChange={(e) => ui.setState({ topK: Number(e.target.value) })} /></label>
          </AccordionContent>
        </AccordionItem>

        <AccordionItem value="appearance" className="surface rounded-lg border p-4">
          <AccordionTrigger className="py-0 hover:no-underline">Apariencia</AccordionTrigger>
          <AccordionContent className="space-y-3 pt-4">
            <label className="flex items-center justify-between gap-3 text-sm">Panel derecho<Switch checked={ui.rightPanel} onCheckedChange={(rightPanel) => ui.setState({ rightPanel })} /></label>
            <label className="flex items-center justify-between gap-3 text-sm">Layout compacto<Switch checked={ui.compact} onCheckedChange={(compact) => ui.setState({ compact })} /></label>
            <label className="space-y-1 text-sm text-muted-foreground">Fuente chat<Input type="number" value={ui.fontSize} onChange={(e) => ui.setState({ fontSize: Number(e.target.value) })} /></label>
            <Button variant="secondary" onClick={() => ui.setState({ theme: ui.theme === "dark" ? "light" : "dark" })}>Tema: {ui.theme}</Button>
          </AccordionContent>
        </AccordionItem>

        <CommandCard icon={Wifi} title="Web search" description="Estado actual de Vane y fallback SearXNG.">
          <div className="flex flex-wrap gap-2">
            <StatusBadge label="vane" tone={health.data?.vane ? "ok" : "degraded"} detail={String(webSearch.providers_endpoint ?? false)} />
            <StatusBadge label="searxng" tone={webSearch.search_endpoint ? "ok" : "error"} detail={String(webSearch.search_endpoint ?? false)} />
            <StatusBadge label="timeout" tone="warning" detail="8s configurado en backend" />
          </div>
          <p className="mt-3 text-sm text-muted-foreground">Mientras Vane este lento, mantener fallback SearXNG activo evita bloquear la experiencia de busqueda.</p>
        </CommandCard>

        <AccordionItem value="advanced" className="surface rounded-lg border p-4">
          <AccordionTrigger className="py-0 hover:no-underline">Avanzado</AccordionTrigger>
          <AccordionContent className="flex flex-wrap gap-2 pt-4">
            <Button variant="secondary" onClick={exportSettings}><Copy className="size-4" /> Exportar settings JSON</Button>
            <Button variant="destructive" onClick={resetSettings}><RotateCcw className="size-4" /> Reset localStorage</Button>
          </AccordionContent>
        </AccordionItem>
      </Accordion>
    </div>
  );
}
