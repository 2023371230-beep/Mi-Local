"use client";

import { useMutation } from "@tanstack/react-query";
import { Bot, Check, FileDiff, FolderOpen, ListChecks, Play, RotateCcw, X } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";
import {
  applyAgentStep,
  createAgentSession,
  proposeAgentEdit,
  proposeAgentPlan,
  rejectAgentStep,
  nextAgentStep,
  revertAgentStep,
} from "@/lib/api/agent";
import type { AgentSession, AgentStep } from "@/lib/types/agent";
import { pageShell } from "@/lib/config/design-tokens";
import { Button } from "@/components/ui/button";
import { CommandCard } from "@/components/ui/command-card";
import { EmptyState } from "@/components/ui/empty-state";
import { Input } from "@/components/ui/input";
import { SectionHeader } from "@/components/ui/section-header";
import { StatusBadge } from "@/components/ui/status-badge";
import { Textarea } from "@/components/ui/textarea";

const stepTone: Record<string, "ok" | "info" | "warning" | "degraded" | "error"> = {
  pending: "info",
  proposed: "warning",
  applied: "ok",
  executed: "ok",
  rejected: "degraded",
  failed: "error",
};

function errorMessage(error: unknown): string {
  return error instanceof Error ? error.message : "Error inesperado";
}

export function AgentView() {
  const [workspacePath, setWorkspacePath] = useState("");
  const [goal, setGoal] = useState("");
  const [session, setSession] = useState<AgentSession | null>(null);

  const openSession = useMutation({
    mutationFn: createAgentSession,
    onSuccess: (data) => {
      setSession(data);
      toast.success(`Workspace abierto (${data.tree.length} archivos)`);
    },
    onError: (error) => toast.error(errorMessage(error)),
  });

  const plan = useMutation({
    mutationFn: ({ sessionId, planGoal }: { sessionId: string; planGoal: string }) => proposeAgentPlan(sessionId, planGoal),
    onSuccess: (data) => {
      setSession(data);
      toast.success(`Plan con ${data.steps.length} pasos. Nada se aplica sin tu aprobacion.`);
    },
    onError: (error) => toast.error(errorMessage(error)),
  });

  const stepAction = useMutation({
    mutationFn: ({ action, stepIndex }: { action: "propose" | "apply" | "reject" | "revert"; stepIndex: number }) => {
      if (!session) throw new Error("Sin sesion activa");
      if (action === "propose") return proposeAgentEdit(session.session_id, stepIndex);
      if (action === "apply") return applyAgentStep(session.session_id, stepIndex);
      if (action === "revert") return revertAgentStep(session.session_id, stepIndex);
      return rejectAgentStep(session.session_id, stepIndex);
    },
    onSuccess: (data) => setSession(data),
    onError: (error) => toast.error(errorMessage(error)),
  });

  const nextStep = useMutation({
    mutationFn: () => {
      if (!session) throw new Error("Sin sesion activa");
      return nextAgentStep(session.session_id);
    },
    onSuccess: (data) => {
      setSession(data);
      toast.success("Paso siguiente propuesto. Revisalo y aprueba o rechaza.");
    },
    onError: (error) => toast.error(errorMessage(error)),
  });

  const busy = openSession.isPending || plan.isPending || stepAction.isPending || nextStep.isPending;
  const hasExecutedStep = session?.steps.some((step) => ["executed", "failed", "applied"].includes(step.status)) ?? false;

  return (
    <div className={pageShell}>
      <SectionHeader
        eyebrow="Agent"
        title="Modo agente"
        description="El agente planifica y propone; tu apruebas cada cambio y cada comando. Sin aprobacion no pasa nada."
        actions={<StatusBadge label="Aprobacion obligatoria" tone="warning" withIcon />}
      />

      <CommandCard icon={FolderOpen} title="1. Workspace" description="Carpeta del proyecto sobre la que trabajara el agente.">
        <div className="flex flex-col gap-2 sm:flex-row">
          <Input
            value={workspacePath}
            onChange={(event) => setWorkspacePath(event.target.value)}
            placeholder="C:\\Users\\angel\\mi-proyecto"
            className="font-mono text-xs"
          />
          <Button onClick={() => openSession.mutate(workspacePath)} disabled={busy || !workspacePath.trim()}>
            <FolderOpen className="size-4" />
            Abrir workspace
          </Button>
        </div>
        {session ? (
          <p className="mt-2 text-xs text-muted-foreground">
            Sesion <span className="font-mono">{session.session_id.slice(0, 8)}</span> · {session.tree.length} archivos indexados
          </p>
        ) : null}
      </CommandCard>

      {session ? (
        <CommandCard icon={Bot} title="2. Objetivo" description="Describe que quieres lograr; el agente genera un plan de pasos.">
          <div className="space-y-2">
            <Textarea
              value={goal}
              onChange={(event) => setGoal(event.target.value)}
              placeholder="Ej: agrega un endpoint /ping en FastAPI con su test"
              className="min-h-24 bg-background/55"
            />
            <Button onClick={() => plan.mutate({ sessionId: session.session_id, planGoal: goal })} disabled={busy || !goal.trim()}>
              <ListChecks className="size-4" />
              {plan.isPending ? "Generando plan (puede tardar minutos en CPU)..." : "Generar plan"}
            </Button>
          </div>
        </CommandCard>
      ) : null}

      {session && session.steps.length > 0 ? (
        <CommandCard icon={ListChecks} title="3. Plan y aprobaciones" description="Revisa cada paso. Propuesta -> diff -> aprobar o rechazar.">
          <div className="space-y-3">
            {session.steps.map((step) => (
              <StepCard key={step.index} step={step} busy={busy} onAction={(action) => stepAction.mutate({ action, stepIndex: step.index })} />
            ))}
            {hasExecutedStep ? (
              <Button variant="outline" disabled={busy} onClick={() => nextStep.mutate()}>
                <Play className="size-4" />
                {nextStep.isPending ? "Analizando la salida del ultimo paso..." : "Proponer siguiente paso"}
              </Button>
            ) : null}
          </div>
        </CommandCard>
      ) : null}

      {session && session.events.length > 0 ? (
        <CommandCard icon={Play} title="Actividad" description="Registro de eventos de la sesion.">
          <div className="max-h-48 overflow-y-auto rounded-md border border-border bg-background/40 p-3 font-mono text-xs leading-5 text-muted-foreground">
            {session.events.map((event, index) => (
              <div key={index}>{event}</div>
            ))}
          </div>
        </CommandCard>
      ) : null}

      {!session ? (
        <EmptyState
          title="Sin sesion activa"
          description="Abre un workspace para empezar. El agente solo puede leer, proponer y ejecutar comandos whitelisted con tu aprobacion."
        />
      ) : null}
    </div>
  );
}

function StepCard({ step, busy, onAction }: { step: AgentStep; busy: boolean; onAction: (action: "propose" | "apply" | "reject" | "revert") => void }) {
  const isEdit = step.kind === "edit";
  return (
    <div className="surface-muted rounded-lg border p-4">
      <div className="flex flex-wrap items-center gap-2">
        <span className="font-mono text-xs text-primary">#{step.index + 1}</span>
        <StatusBadge label={step.status} tone={stepTone[step.status] ?? "info"} />
        <span className="font-mono text-xs text-muted-foreground">{isEdit ? step.path : step.command}</span>
      </div>
      <p className="mt-2 text-sm leading-6">{step.description}</p>

      {step.diff ? (
        <pre className="mt-3 max-h-64 overflow-auto rounded-md border border-border bg-background/60 p-3 text-xs leading-5">
          {step.diff.split("\n").map((line, index) => (
            <div
              key={index}
              className={
                line.startsWith("+") && !line.startsWith("+++")
                  ? "text-emerald-500"
                  : line.startsWith("-") && !line.startsWith("---")
                    ? "text-red-500"
                    : "text-muted-foreground"
              }
            >
              {line || " "}
            </div>
          ))}
        </pre>
      ) : null}

      {step.output ? (
        <pre className="mt-3 max-h-48 overflow-auto rounded-md border border-border bg-background/60 p-3 text-xs leading-5 text-muted-foreground">{step.output}</pre>
      ) : null}

      {step.error ? <p className="mt-2 text-xs text-red-500">{step.error}</p> : null}

      <div className="mt-3 flex flex-wrap gap-2">
        {isEdit && step.status === "pending" ? (
          <Button size="sm" variant="outline" disabled={busy} onClick={() => onAction("propose")}>
            <FileDiff className="size-4" />
            Proponer diff
          </Button>
        ) : null}
        {isEdit && step.status === "proposed" ? (
          <Button size="sm" disabled={busy} onClick={() => onAction("apply")}>
            <Check className="size-4" />
            Aprobar y aplicar
          </Button>
        ) : null}
        {!isEdit && (step.status === "pending" || step.status === "failed") ? (
          <Button size="sm" disabled={busy} onClick={() => onAction("apply")}>
            <Play className="size-4" />
            Aprobar y ejecutar
          </Button>
        ) : null}
        {step.status === "applied" && isEdit ? (
          <Button size="sm" variant="outline" disabled={busy} onClick={() => onAction("revert")}>
            <RotateCcw className="size-4" />
            Revertir
          </Button>
        ) : null}
        {step.status !== "rejected" && step.status !== "applied" && step.status !== "executed" ? (
          <Button size="sm" variant="ghost" disabled={busy} onClick={() => onAction("reject")}>
            <X className="size-4" />
            Rechazar
          </Button>
        ) : null}
      </div>
    </div>
  );
}
