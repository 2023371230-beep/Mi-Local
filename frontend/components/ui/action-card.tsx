import Link from "next/link";
import type { LucideIcon } from "lucide-react";
import { ArrowRight } from "lucide-react";
import type { ReactNode } from "react";
import { cn } from "@/lib/utils";
import { StatusBadge } from "@/components/ui/status-badge";
import type { StatusTone } from "@/lib/config/design-tokens";

export function ActionCard({
  title,
  description,
  href,
  actionLabel = "Abrir",
  icon: Icon,
  tone = "idle",
  status,
  children,
  className,
}: {
  title: string;
  description: string;
  href: string;
  actionLabel?: string;
  icon: LucideIcon;
  tone?: StatusTone;
  status?: string;
  children?: ReactNode;
  className?: string;
}) {
  return (
    <div className={cn("surface-elevated group flex min-h-[180px] flex-col rounded-lg p-4 transition-all hover:-translate-y-0.5 hover:border-white/18", className)}>
      <div className="flex items-start justify-between gap-3">
        <div className="rounded-md border border-border bg-background/60 p-2 text-primary">
          <Icon className="size-5" />
        </div>
        <StatusBadge label={status ?? tone} tone={tone} compact />
      </div>
      <div className="mt-4 min-w-0">
        <h3 className="text-base font-semibold">{title}</h3>
        <p className="mt-2 text-sm leading-6 text-muted-foreground">{description}</p>
      </div>
      {children ? <div className="mt-3">{children}</div> : null}
      <Link
        href={href}
        className="focus-ring mt-auto inline-flex h-9 items-center justify-between rounded-md bg-primary px-3 text-sm font-medium text-primary-foreground transition-colors hover:bg-primary/90"
      >
        {actionLabel}
        <ArrowRight className="size-4 transition-transform group-hover:translate-x-0.5" />
      </Link>
    </div>
  );
}
