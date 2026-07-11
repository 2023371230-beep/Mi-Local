"use client";

import { useQuery } from "@tanstack/react-query";
import { Menu, MoreHorizontal, RefreshCw } from "lucide-react";
import { useMemo } from "react";
import { getHealth } from "@/lib/api/health";
import { Button } from "@/components/ui/button";
import { DropdownMenu, DropdownMenuContent, DropdownMenuLabel, DropdownMenuSeparator, DropdownMenuTrigger } from "@/components/ui/dropdown-menu";
import { StatusPill } from "@/components/layout/status-pill";
import type { StatusTone } from "@/lib/config/design-tokens";

function boolTone(value?: boolean): StatusTone {
  if (value === true) return "ok";
  if (value === false) return "error";
  return "idle";
}

export function TopBar({ onMenuClick, onContextClick }: { onMenuClick: () => void; onContextClick?: () => void }) {
  const { data, refetch, isFetching, dataUpdatedAt } = useQuery({ queryKey: ["health"], queryFn: getHealth, staleTime: 15_000 });
  const webSearch = data?.web_search ?? {};
  const searxngOk = Boolean(webSearch.search_endpoint);
  const vaneOk = Boolean(data?.vane ?? data?.perplexica);
  const webTone: StatusTone = searxngOk && !vaneOk ? "fallback" : searxngOk || vaneOk ? "ok" : data?.status === "ok" ? "degraded" : "error";
  const updated = useMemo(() => (dataUpdatedAt ? `updated ${new Date(dataUpdatedAt).toLocaleTimeString()}` : "sin actualizar"), [dataUpdatedAt]);

  return (
    <header className="flex h-14 shrink-0 items-center justify-between border-b border-border bg-background/78 px-3 backdrop-blur-xl">
      <div className="flex min-w-0 items-center gap-2">
        <Button variant="ghost" size="icon" className="md:hidden" onClick={onMenuClick} aria-label="Abrir navegacion">
          <Menu className="size-4" />
        </Button>
        <div className="hidden min-w-0 items-center gap-2 sm:flex">
          <StatusPill label="api" tone={data?.status === "ok" ? "ok" : "error"} />
          <StatusPill label="ollama" tone={boolTone(data?.ollama)} />
          <StatusPill label="chroma" tone={boolTone(data?.chroma)} />
          <StatusPill label="web" tone={webTone} detail={webTone === "fallback" ? "fallback" : undefined} />
        </div>
        <div className="sm:hidden">
          <StatusPill label="system" tone={data?.status === "ok" ? "ok" : "error"} />
        </div>
      </div>

      <div className="flex items-center gap-2">
        <span className="hidden font-mono text-[11px] text-muted-foreground md:inline">{updated}</span>
        {onContextClick ? (
          <Button variant="secondary" size="sm" onClick={onContextClick} className="lg:hidden">
            Contexto
          </Button>
        ) : null}
        <Button size="icon" variant="ghost" onClick={() => refetch()} aria-label="Refrescar estado">
          <RefreshCw className={isFetching ? "size-4 animate-spin" : "size-4"} />
        </Button>
        <DropdownMenu>
          <DropdownMenuTrigger
            aria-label="Detalles del sistema"
            className="inline-flex size-8 items-center justify-center rounded-lg text-sm font-medium transition-colors hover:bg-muted hover:text-foreground focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50"
          >
            <MoreHorizontal className="size-4" />
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-72">
            <DropdownMenuLabel>System details</DropdownMenuLabel>
            <div className="space-y-2 px-2 py-1 text-xs text-muted-foreground">
              <div className="flex justify-between gap-3"><span>Backend</span><span className="font-mono">{data?.status ?? "unknown"}</span></div>
              <div className="flex justify-between gap-3"><span>Ollama</span><span className="font-mono">{String(data?.ollama ?? false)}</span></div>
              <div className="flex justify-between gap-3"><span>Chroma</span><span className="font-mono">{String(data?.chroma ?? false)}</span></div>
              <div className="flex justify-between gap-3"><span>Vane providers</span><span className="font-mono">{String(vaneOk)}</span></div>
              <div className="flex justify-between gap-3"><span>SearXNG fallback</span><span className="font-mono">{String(searxngOk)}</span></div>
            </div>
            <DropdownMenuSeparator />
            <p className="px-2 py-1.5 text-xs leading-5 text-muted-foreground">
              Si Vane esta lento o apagado, la busqueda web debe mostrarse como degradada o fallback.
            </p>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </header>
  );
}
