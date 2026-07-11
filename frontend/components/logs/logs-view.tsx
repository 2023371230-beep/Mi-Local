"use client";

import { useQuery } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import { Copy, RefreshCw, Terminal } from "lucide-react";
import { toast } from "sonner";
import { getLogs } from "@/lib/api/logs";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { StatusBadge } from "@/components/ui/status-badge";
import { CommandCard } from "@/components/ui/command-card";

const filters = ["ALL", "INFO", "WARNING", "ERROR", "Vane", "chat", "RAG", "web"];

function normalize(item: unknown) {
  return typeof item === "string" ? item : JSON.stringify(item);
}

function lineClass(line: string) {
  if (/error|exception|failed/i.test(line)) return "text-rose-200";
  if (/warning|timeout|degraded|fallback|vane/i.test(line)) return "text-amber-100";
  return "text-emerald-100/85";
}

export function LogsView() {
  const [filter, setFilter] = useState("");
  const [level, setLevel] = useState("ALL");
  const query = useQuery({ queryKey: ["logs"], queryFn: () => getLogs(300), staleTime: 10_000 });
  const rawLogs = useMemo(() => (query.data?.logs ?? []).map(normalize), [query.data]);
  const vaneTimeouts = rawLogs.filter((line) => /Vane search timed out/i.test(line)).length;
  const logs = useMemo(() => rawLogs.filter((line) => {
    const textMatch = line.toLowerCase().includes(filter.toLowerCase());
    const levelMatch = level === "ALL" || line.toLowerCase().includes(level.toLowerCase());
    return textMatch && levelMatch;
  }), [rawLogs, filter, level]);

  return (
    <div className="space-y-4">
      <div className="grid gap-3 md:grid-cols-3">
        <div className="surface rounded-lg p-3">
          <StatusBadge label="Vane timeout frecuente" tone={vaneTimeouts > 0 ? "degraded" : "ok"} withIcon />
          <p className="mt-2 text-sm text-muted-foreground">{vaneTimeouts > 0 ? `${vaneTimeouts} ocurrencias detectadas. Usar SearXNG como fallback.` : "Sin timeouts recientes detectados."}</p>
        </div>
        <div className="surface rounded-lg p-3">
          <StatusBadge label="Web search" tone={vaneTimeouts > 0 ? "fallback" : "ok"} withIcon />
          <p className="mt-2 text-sm text-muted-foreground">La UI debe mostrar fallback cuando Vane no completa busqueda.</p>
        </div>
        <div className="surface rounded-lg p-3">
          <StatusBadge label="Lineas" detail={String(rawLogs.length)} tone="info" withIcon />
          <p className="mt-2 text-sm text-muted-foreground">Filtra por severidad, modulo o texto libre.</p>
        </div>
      </div>

      <CommandCard icon={Terminal} title="Terminal de logs" description="Vista legible con filtros y highlight basico.">
        <div className="mb-3 flex flex-col gap-2 lg:flex-row">
          <Input value={filter} onChange={(event) => setFilter(event.target.value)} placeholder="Buscar en logs" className="lg:max-w-sm" />
          <div className="flex flex-wrap gap-2">
            {filters.map((item) => (
              <Button key={item} size="sm" variant={level === item ? "default" : "secondary"} onClick={() => setLevel(item)}>
                {item}
              </Button>
            ))}
            <Button variant="secondary" size="sm" onClick={() => query.refetch()}><RefreshCw className="size-4" /> Refresh</Button>
            <Button variant="secondary" size="sm" onClick={async () => { await navigator.clipboard.writeText(logs.join("\n")); toast.success("Logs copiados"); }}><Copy className="size-4" /> Copiar</Button>
          </div>
        </div>
        <ScrollArea className="h-[calc(100vh-22rem)] min-h-96 rounded-lg border border-border bg-black/45 p-3">
          <pre className="whitespace-pre-wrap font-mono text-xs leading-5">
            {logs.map((line, index) => <div key={`${line}-${index}`} className={lineClass(line)}>{line}</div>)}
          </pre>
        </ScrollArea>
      </CommandCard>
    </div>
  );
}
