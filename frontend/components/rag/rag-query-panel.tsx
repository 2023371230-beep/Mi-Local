"use client";

import { useMutation } from "@tanstack/react-query";
import { toast } from "sonner";
import { Search } from "lucide-react";
import { useState } from "react";
import { queryRag } from "@/lib/api/rag";
import { useChatStore } from "@/lib/stores/chat-store";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Input } from "@/components/ui/input";
import { MarkdownMessage } from "@/components/chat/markdown-message";
import { RagSourceCard } from "@/components/rag/rag-source-card";
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";
import { CommandCard } from "@/components/ui/command-card";
import { EmptyState } from "@/components/ui/empty-state";

export function RagQueryPanel() {
  const [message, setMessage] = useState("Con base en mis documentos UI/UX, dame principios de interfaz tipo IDE.");
  const [collection, setCollection] = useState("ui_ux");
  const [topK, setTopK] = useState(5);
  const setSources = useChatStore((state) => state.setSources);
  const mutation = useMutation({
    mutationFn: queryRag,
    onSuccess: (data) => {
      setSources(data.sources);
      if (data.sources.length === 0) toast.info("RAG no devolvio fuentes");
      else toast.success(`RAG recupero ${data.sources.length} fuentes`);
    },
    onError: (error) => toast.error(error instanceof Error ? error.message : "Error consultando RAG"),
  });

  return (
    <CommandCard icon={Search} title="Consulta RAG" description="Pregunta a tus documentos locales. Las opciones tecnicas se mantienen ocultas hasta necesitarlas.">
      <div className="space-y-3">
        <label className="space-y-1 text-sm text-muted-foreground">
          Pregunta
          <Textarea value={message} onChange={(event) => setMessage(event.target.value)} className="min-h-28 bg-background/55" />
        </label>
        <Accordion className="rounded-md border border-border bg-background/30 px-2">
          <AccordionItem value="advanced" className="border-0">
            <AccordionTrigger className="py-2 text-xs text-muted-foreground hover:no-underline">Opciones avanzadas</AccordionTrigger>
            <AccordionContent className="grid gap-2 pb-3 md:grid-cols-2">
              <label className="space-y-1 text-xs text-muted-foreground">Coleccion<Input value={collection} onChange={(event) => setCollection(event.target.value)} /></label>
              <label className="space-y-1 text-xs text-muted-foreground">Top K<Input type="number" min={1} max={20} value={topK} onChange={(event) => setTopK(Number(event.target.value))} /></label>
            </AccordionContent>
          </AccordionItem>
        </Accordion>
        <Button onClick={() => mutation.mutate({ message, collection, top_k: topK })} disabled={mutation.isPending || !message.trim()}>
          <Search className="size-4" />
          Consultar documentos
        </Button>
        {mutation.data?.answer ? <div className="surface-muted rounded-lg border p-4 text-sm"><MarkdownMessage content={mutation.data.answer} /></div> : null}
        {mutation.data ? (
          mutation.data.sources.length > 0 ? <div className="grid gap-3 md:grid-cols-2">{mutation.data.sources.map((source, index) => <RagSourceCard key={index} source={source} />)}</div> : <EmptyState title="Sin fuentes" description="Prueba otra coleccion o una pregunta mas cercana a tus documentos." compact />
        ) : null}
      </div>
    </CommandCard>
  );
}
