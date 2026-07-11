import type { Source } from "@/lib/types/api";
import { Badge } from "@/components/ui/badge";

export function RagSourceCard({ source }: { source: Source }) {
  return (
    <div className="surface-muted rounded-lg border p-3 text-sm">
      <div className="flex flex-wrap gap-2">
        <Badge variant="outline">{source.filename ?? source.source}</Badge>
        {typeof source.page === "number" && <Badge variant="secondary">page {source.page}</Badge>}
        {typeof source.chunk_index === "number" && <Badge variant="secondary">chunk {source.chunk_index}</Badge>}
        {typeof source.score === "number" && <Badge variant="secondary">score {source.score.toFixed(2)}</Badge>}
      </div>
      {source.content && <p className="mt-3 line-clamp-4 text-xs leading-5 text-muted-foreground">{source.content}</p>}
      {source.path && <p className="mt-2 break-all font-mono text-[11px] text-muted-foreground">{source.path}</p>}
    </div>
  );
}
