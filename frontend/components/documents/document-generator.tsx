"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Download, FilePlus2, FileText, History } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";
import {
  documentDownloadUrl,
  generateDocument,
  getDocumentOutputs,
} from "@/lib/api/documents";
import { getCollections } from "@/lib/api/rag";
import { Button, buttonVariants } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { CommandCard } from "@/components/ui/command-card";
import { EmptyState } from "@/components/ui/empty-state";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
import { Textarea } from "@/components/ui/textarea";
import { MarkdownMessage } from "@/components/chat/markdown-message";

const typeLabels: Record<string, string> = {
  reporte_tecnico: "Reporte tecnico",
  manual_usuario: "Manual de usuario",
  manual_tecnico: "Manual tecnico",
  documentacion_api: "Documentacion de API",
  readme: "README profesional",
  reporte_practica: "Reporte de practica",
  requerimientos: "Requerimientos",
  politica: "Politica",
  checklist: "Checklist",
};

export function DocumentGenerator() {
  const queryClient = useQueryClient();
  const [docType, setDocType] = useState("reporte_tecnico");
  const [title, setTitle] = useState("");
  const [instructions, setInstructions] = useState("");
  const [format, setFormat] = useState("md");
  const [useRag, setUseRag] = useState(false);
  const [collection, setCollection] = useState("asistente");

  const meta = useQuery({ queryKey: ["document-outputs"], queryFn: getDocumentOutputs, staleTime: 15_000 });
  const collections = useQuery({ queryKey: ["collections"], queryFn: getCollections, staleTime: 60_000 });

  const mutation = useMutation({
    mutationFn: generateDocument,
    onSuccess: (data) => {
      toast.success(`Documento generado: ${data.filename}`);
      queryClient.invalidateQueries({ queryKey: ["document-outputs"] });
    },
    onError: (error) => toast.error(error instanceof Error ? error.message : "Error generando documento"),
  });

  const docTypes = meta.data?.doc_types ?? Object.keys(typeLabels);
  const formats = meta.data?.formats ?? ["md", "html", "docx", "pdf"];
  const outputs = meta.data?.outputs ?? [];

  return (
    <div className="space-y-4">
      <CommandCard
        icon={FilePlus2}
        title="Generar documento"
        description="El modelo local redacta el documento con la estructura del tipo elegido; puedes usar tus documentos RAG como fuentes."
      >
        <div className="space-y-3">
          <div className="grid gap-2 sm:grid-cols-2">
            <label className="space-y-1 text-xs text-muted-foreground">
              Tipo
              <Select value={docType} onValueChange={(value) => value && setDocType(value)}>
                <SelectTrigger className="w-full"><SelectValue /></SelectTrigger>
                <SelectContent>
                  {docTypes.map((value) => (
                    <SelectItem key={value} value={value}>{typeLabels[value] ?? value}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </label>
            <label className="space-y-1 text-xs text-muted-foreground">
              Formato
              <Select value={format} onValueChange={(value) => value && setFormat(value)}>
                <SelectTrigger className="w-full"><SelectValue /></SelectTrigger>
                <SelectContent>
                  {formats.map((value) => (
                    <SelectItem key={value} value={value}>{value.toUpperCase()}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </label>
          </div>
          <label className="space-y-1 text-xs text-muted-foreground">
            Titulo
            <Input value={title} onChange={(event) => setTitle(event.target.value)} placeholder="Reporte de practica: hardening de Windows" />
          </label>
          <label className="space-y-1 text-xs text-muted-foreground">
            Indicaciones
            <Textarea
              value={instructions}
              onChange={(event) => setInstructions(event.target.value)}
              placeholder="Que debe cubrir, tono, secciones extra..."
              className="min-h-20"
            />
          </label>
          <div className="flex flex-wrap items-center gap-3">
            <label className="flex items-center gap-2 text-xs text-muted-foreground">
              <Switch checked={useRag} onCheckedChange={setUseRag} aria-label="Usar mis documentos RAG" />
              Usar mis documentos (RAG)
            </label>
            {useRag ? (
              <Select value={collection} onValueChange={(value) => value && setCollection(value)}>
                <SelectTrigger className="h-8 w-44"><SelectValue /></SelectTrigger>
                <SelectContent>
                  {(collections.data?.collections ?? []).map((name) => (
                    <SelectItem key={name} value={name}>{name}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            ) : null}
          </div>
          <Button
            onClick={() =>
              mutation.mutate({
                doc_type: docType,
                title,
                instructions,
                output_format: format,
                use_rag: useRag,
                collection: useRag ? collection : undefined,
              })
            }
            disabled={mutation.isPending || !title.trim()}
          >
            <FileText className="size-4" />
            {mutation.isPending ? "Generando (el modelo local esta escribiendo)..." : "Generar documento"}
          </Button>
        </div>
      </CommandCard>

      {mutation.data ? (
        <CommandCard icon={FileText} title="Preview" description={`${mutation.data.filename} · ${Math.round(mutation.data.latency_ms / 1000)}s`}>
          <div className="max-h-96 overflow-y-auto rounded-md border border-border bg-background/40 p-4 text-sm">
            <MarkdownMessage content={mutation.data.markdown} />
          </div>
          <a
            href={documentDownloadUrl(mutation.data.filename)}
            download
            className={cn(buttonVariants({ variant: "outline" }), "mt-3")}
          >
            <Download className="size-4" />
            Descargar {mutation.data.format.toUpperCase()}
          </a>
        </CommandCard>
      ) : null}

      <CommandCard icon={History} title="Historial" description="Documentos generados anteriormente.">
        {outputs.length === 0 ? (
          <EmptyState title="Sin documentos" description="Genera tu primer documento arriba." compact />
        ) : (
          <ul className="divide-y divide-border text-sm">
            {outputs.slice(0, 12).map((item) => (
              <li key={item.filename} className="flex items-center justify-between gap-2 py-2">
                <span className="min-w-0 truncate font-mono text-xs">{item.filename}</span>
                <a
                  href={documentDownloadUrl(item.filename)}
                  download
                  aria-label={`Descargar ${item.filename}`}
                  className={cn(buttonVariants({ variant: "ghost", size: "sm" }))}
                >
                  <Download className="size-4" />
                </a>
              </li>
            ))}
          </ul>
        )}
      </CommandCard>
    </div>
  );
}
