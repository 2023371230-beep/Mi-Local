import type { Source } from "@/lib/types/api";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Badge } from "@/components/ui/badge";
import { EmptyState } from "@/components/ui/empty-state";
import { FileSearch } from "lucide-react";

export function SourcesPanel({ sources, embedded }: { sources: Source[]; embedded?: boolean }) {
  return (
    <div className="flex h-full flex-col">
      {!embedded ? (
        <div className="border-b border-border p-3">
          <div className="text-sm font-medium">Contexto</div>
          <div className="text-xs text-muted-foreground">{sources.length} fuentes activas</div>
        </div>
      ) : null}
      <ScrollArea className="min-h-0 flex-1">
        <div className="space-y-2 p-3">
          {sources.length === 0 ? (
            <EmptyState icon={FileSearch} title="Sin fuentes activas" description="Cuando una respuesta use RAG o web, sus fuentes apareceran aqui." compact />
          ) : (
            sources.map((source, index) => (
              <div key={`${source.source}-${index}`} className="surface-muted rounded-lg border p-3">
                <div className="mb-2 flex items-center justify-between gap-2">
                  <Badge variant="outline" className="max-w-full truncate">{source.filename ?? source.title ?? source.source}</Badge>
                  {typeof source.page === "number" && <span className="font-mono text-[11px] text-muted-foreground">p.{source.page}</span>}
                </div>
                {source.url && <a className="break-all text-xs text-primary hover:underline" href={source.url} target="_blank" rel="noreferrer">{source.url}</a>}
                {source.content && <p className="mt-2 line-clamp-4 text-xs text-muted-foreground">{source.content}</p>}
                {source.path && <p className="mt-2 break-all font-mono text-[11px] text-muted-foreground">{source.path}</p>}
                {typeof source.chunk_index === "number" && <p className="mt-2 font-mono text-[11px] text-muted-foreground">chunk {source.chunk_index}</p>}
              </div>
            ))
          )}
        </div>
      </ScrollArea>
    </div>
  );
}
