import type { ChatResponse } from "@/lib/types/api";
import { Badge } from "@/components/ui/badge";

export function ChatMetadata({ response, compact }: { response?: ChatResponse; compact?: boolean }) {
  if (!response) return null;
  return (
    <div className="flex flex-wrap gap-1.5">
      <Badge variant="outline" className={compact ? "h-5 font-mono text-[10px]" : undefined}>skill {response.skill_used}</Badge>
      <Badge variant="outline" className={compact ? "h-5 font-mono text-[10px]" : undefined}>model {response.model_used}</Badge>
      <Badge variant={response.rag_used ? "default" : "secondary"} className={compact ? "h-5 font-mono text-[10px]" : undefined}>rag {String(response.rag_used)}</Badge>
      <Badge variant={response.web_used ? "default" : "secondary"} className={compact ? "h-5 font-mono text-[10px]" : undefined}>web {String(response.web_used)}</Badge>
      <Badge variant="outline" className={compact ? "h-5 font-mono text-[10px]" : undefined}>{response.latency_ms} ms</Badge>
    </div>
  );
}
