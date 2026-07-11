"use client";

import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { Bot, BrainCircuit, Database, FileText, MessageSquare, Radar, ScrollText, ShieldCheck } from "lucide-react";
import { getHealth } from "@/lib/api/health";
import { getCollections } from "@/lib/api/rag";
import { getLogs } from "@/lib/api/logs";
import { pageShell } from "@/lib/config/design-tokens";
import { ActionCard } from "@/components/ui/action-card";
import { CommandCard } from "@/components/ui/command-card";
import { MetricCard } from "@/components/ui/metric-card";
import { SectionHeader } from "@/components/ui/section-header";
import { StatusBadge } from "@/components/ui/status-badge";
import { Button } from "@/components/ui/button";

export function DashboardView() {
  const health = useQuery({ queryKey: ["health"], queryFn: getHealth, staleTime: 15_000 });
  const collections = useQuery({ queryKey: ["collections"], queryFn: getCollections, staleTime: 30_000 });
  const logs = useQuery({ queryKey: ["logs", 40], queryFn: () => getLogs(40), staleTime: 20_000 });
  const webSearch = health.data?.web_search ?? {};
  const apiOk = health.data?.status === "ok";
  const vaneOk = Boolean(health.data?.vane ?? health.data?.perplexica);
  const searxngOk = Boolean(webSearch.search_endpoint);
  const systemTone = apiOk && health.data?.ollama && health.data?.chroma ? (vaneOk || searxngOk ? "ok" : "degraded") : "error";
  const recentWarnings = (logs.data?.logs ?? [])
    .map((item) => (typeof item === "string" ? item : JSON.stringify(item)))
    .filter((line) => /error|warning|timeout|vane|fallback/i.test(line))
    .slice(0, 4);

  return (
    <div className={pageShell}>
      <SectionHeader
        eyebrow="Modelo IA Carrera"
        title="Centro de comando local"
        description="Consulta modelos locales, RAG, web fallback y herramientas tecnicas desde una superficie limpia."
        actions={
          <>
            <Link className="focus-ring inline-flex h-9 items-center gap-2 rounded-md bg-primary px-3 text-sm font-medium text-primary-foreground hover:bg-primary/90" href="/chat">
              <MessageSquare className="size-4" />
              Nuevo chat
            </Link>
            <Link className="focus-ring inline-flex h-9 items-center gap-2 rounded-md bg-secondary px-3 text-sm font-medium text-secondary-foreground hover:bg-secondary/80" href="/documents">
              <FileText className="size-4" />
              Ingestar docs
            </Link>
            <Link className="focus-ring inline-flex h-9 items-center gap-2 rounded-md border border-border px-3 text-sm font-medium hover:bg-muted" href="/rag">
              <Database className="size-4" />
              Probar RAG
            </Link>
          </>
        }
      />

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <ActionCard title="Chat operativo" description="Conversacion con routing de skills, RAG opcional y metadata visible." href="/chat" icon={MessageSquare} tone={apiOk ? "ok" : "error"} status={apiOk ? "listo" : "offline"} />
        <ActionCard title="RAG local" description="Consulta la coleccion UI/UX y tus documentos con fuentes recuperadas." href="/rag" icon={Database} tone={health.data?.chroma ? "ok" : "error"} status={health.data?.chroma ? "chroma ok" : "sin vector db"} />
        <ActionCard title="Web search" description="Usa Vane cuando responda y SearXNG como fallback controlado." href="/chat" icon={Radar} tone={vaneOk ? "ok" : searxngOk ? "fallback" : "degraded"} status={vaneOk ? "vane ok" : searxngOk ? "fallback" : "degraded"} />
        <ActionCard title="Agent mode" description="Modulo futuro con permisos, diffs y aprobaciones, sin ejecutar acciones reales todavia." href="/agent" icon={Bot} tone="idle" status="planned" />
      </div>

      <div className="grid gap-4 xl:grid-cols-[1.15fr_0.85fr]">
        <CommandCard icon={ShieldCheck} title="Estado del sistema" description="Resumen compacto de servicios locales y fallback web.">
          <div className="grid gap-3 sm:grid-cols-2">
            <MetricCard title="API" value={apiOk ? "Operativa" : "Sin respuesta"} tone={apiOk ? "ok" : "error"} description="FastAPI local en 127.0.0.1:8000" />
            <MetricCard title="Ollama" value={health.data?.ollama ? "Conectado" : "Off"} tone={health.data?.ollama ? "ok" : "error"} description="Modelos locales disponibles" />
            <MetricCard title="Chroma" value={health.data?.chroma ? "Activo" : "Off"} tone={health.data?.chroma ? "ok" : "error"} description="Vector DB persistente" />
            <MetricCard title="Web" value={vaneOk ? "Vane" : searxngOk ? "Fallback" : "Degradado"} tone={vaneOk ? "ok" : searxngOk ? "fallback" : "degraded"} description="Busqueda externa controlada" />
          </div>
        </CommandCard>

        <CommandCard icon={ScrollText} title="Actividad reciente" description="Senales utiles para diagnostico rapido.">
          <div className="space-y-2">
            {recentWarnings.length > 0 ? (
              recentWarnings.map((line, index) => (
                <div key={`${line}-${index}`} className="surface-muted rounded-md border p-2 font-mono text-[11px] leading-5 text-muted-foreground">
                  {line.slice(0, 180)}
                </div>
              ))
            ) : (
              <div className="surface-muted rounded-md border p-3 text-sm text-muted-foreground">Sin warnings recientes detectados.</div>
            )}
          </div>
        </CommandCard>
      </div>

      <CommandCard icon={BrainCircuit} title="Colecciones RAG" description="Colecciones disponibles para recuperar contexto local.">
        <div className="flex flex-wrap items-center gap-2">
          {(collections.data?.collections ?? []).length > 0 ? (
            (collections.data?.collections ?? []).map((item) => <StatusBadge key={item} label={item} tone="info" />)
          ) : (
            <span className="text-sm text-muted-foreground">No hay colecciones visibles todavia.</span>
          )}
          <Button variant="secondary" size="sm" onClick={() => health.refetch()}>
            Refrescar estado
          </Button>
          <Link className="focus-ring inline-flex h-8 items-center rounded-md border border-border px-3 text-sm hover:bg-muted" href="/rag">
            Ver RAG
          </Link>
        </div>
      </CommandCard>

      <div className="sr-only">Estado general: {systemTone}</div>
    </div>
  );
}
