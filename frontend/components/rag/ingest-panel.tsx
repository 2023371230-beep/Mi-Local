"use client";

import { useMutation } from "@tanstack/react-query";
import { toast } from "sonner";
import { FileText, ShieldCheck } from "lucide-react";
import { useState } from "react";
import { ingestDocuments } from "@/lib/api/rag";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { StatusBadge } from "@/components/ui/status-badge";
import { CommandCard } from "@/components/ui/command-card";
import { EmptyState } from "@/components/ui/empty-state";

const uiPath = "C:\\Users\\angel\\Modelo local\\RAG\\UI";
const ragPath = "C:\\Users\\angel\\Modelo local\\RAG";

export function IngestPanel() {
  const [path, setPath] = useState(uiPath);
  const [collection, setCollection] = useState("ui_ux");
  const [topic, setTopic] = useState("ui_ux");
  const mutation = useMutation({
    mutationFn: ingestDocuments,
    onSuccess: (data) => toast.success(`Ingesta terminada: ${data.files_processed} archivos, ${data.chunks_created} chunks`),
    onError: (error) => toast.error(error instanceof Error ? error.message : "Error de ingesta"),
  });

  return (
    <CommandCard icon={FileText} title="Ingesta rapida" description="Agrega documentos al RAG local sin modificar tus PDFs originales.">
      <div className="space-y-4">
        <div className="flex flex-wrap gap-2">
          <Button variant="secondary" size="sm" onClick={() => { setPath(uiPath); setCollection("ui_ux"); setTopic("ui_ux"); }}>Usar ruta UI/UX</Button>
          <Button variant="secondary" size="sm" onClick={() => { setPath(ragPath); setCollection("general"); setTopic("general"); }}>Usar ruta RAG completa</Button>
          <StatusBadge label="No modifica PDFs originales" tone="ok" withIcon />
        </div>
        <label className="space-y-1 text-sm text-muted-foreground">
          Ruta local
          <Input value={path} onChange={(event) => setPath(event.target.value)} className="font-mono" />
        </label>
        <div className="grid gap-2 md:grid-cols-[1fr_1fr_auto]">
          <label className="space-y-1 text-sm text-muted-foreground">Coleccion<Input value={collection} onChange={(event) => setCollection(event.target.value)} /></label>
          <label className="space-y-1 text-sm text-muted-foreground">Tema<Input value={topic} onChange={(event) => setTopic(event.target.value)} /></label>
          <div className="flex items-end">
            <Button className="w-full" onClick={() => mutation.mutate({ path, collection, topic })} disabled={mutation.isPending}>
              Ingestar
            </Button>
          </div>
        </div>
        {mutation.data ? (
          <div className="grid gap-3 md:grid-cols-4">
            <StatusBadge label="files" detail={String(mutation.data.files_processed)} tone="info" />
            <StatusBadge label="chunks" detail={String(mutation.data.chunks_created)} tone="ok" />
            <StatusBadge label="duplicates" detail={String(mutation.data.duplicates_skipped)} tone="idle" />
            <StatusBadge label="errors" detail={String(mutation.data.errors.length)} tone={mutation.data.errors.length ? "error" : "ok"} />
          </div>
        ) : (
          <EmptyState icon={ShieldCheck} title="Flujo controlado" description="Selecciona una ruta, define coleccion/tema y ejecuta la ingesta cuando estes listo." compact />
        )}
        {mutation.data?.errors.length ? (
          <div className="rounded-lg border border-rose-300/25 bg-rose-300/10 p-3 font-mono text-xs text-rose-100">
            {mutation.data.errors.join("\n")}
          </div>
        ) : null}
      </div>
    </CommandCard>
  );
}
