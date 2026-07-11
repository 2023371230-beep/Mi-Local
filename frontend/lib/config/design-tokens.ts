import type { LucideIcon } from "lucide-react";
import { AlertTriangle, CheckCircle2, Circle, Info, ShieldAlert, Wifi } from "lucide-react";

export type StatusTone = "ok" | "warning" | "error" | "degraded" | "idle" | "fallback" | "info";

export const statusTone: Record<StatusTone, { label: string; className: string; dot: string; icon: LucideIcon }> = {
  ok: {
    label: "ok",
    className: "border-emerald-400/25 bg-emerald-400/10 text-emerald-100",
    dot: "bg-emerald-300",
    icon: CheckCircle2,
  },
  warning: {
    label: "warning",
    className: "border-amber-300/25 bg-amber-300/10 text-amber-100",
    dot: "bg-amber-300",
    icon: AlertTriangle,
  },
  error: {
    label: "error",
    className: "border-rose-300/25 bg-rose-300/10 text-rose-100",
    dot: "bg-rose-300",
    icon: ShieldAlert,
  },
  degraded: {
    label: "degraded",
    className: "border-orange-300/25 bg-orange-300/10 text-orange-100",
    dot: "bg-orange-300",
    icon: AlertTriangle,
  },
  idle: {
    label: "idle",
    className: "border-white/12 bg-white/[0.045] text-zinc-300",
    dot: "bg-zinc-400",
    icon: Circle,
  },
  fallback: {
    label: "fallback",
    className: "border-cyan-300/25 bg-cyan-300/10 text-cyan-100",
    dot: "bg-cyan-300",
    icon: Wifi,
  },
  info: {
    label: "info",
    className: "border-sky-300/25 bg-sky-300/10 text-sky-100",
    dot: "bg-sky-300",
    icon: Info,
  },
};

export const pageShell = "mx-auto w-full max-w-[1480px] space-y-5";
export const pageGrid = "grid gap-4";
export const metadataText = "font-mono text-[11px] uppercase tracking-normal text-muted-foreground";
