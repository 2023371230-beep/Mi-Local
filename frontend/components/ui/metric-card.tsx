import type { LucideIcon } from "lucide-react";
import { cn } from "@/lib/utils";
import { StatusBadge } from "@/components/ui/status-badge";
import type { StatusTone } from "@/lib/config/design-tokens";

export function MetricCard({
  title,
  value,
  description,
  icon: Icon,
  tone = "idle",
  className,
}: {
  title: string;
  value: string;
  description?: string;
  icon?: LucideIcon;
  tone?: StatusTone;
  className?: string;
}) {
  return (
    <div className={cn("surface rounded-lg p-4 transition-colors hover:border-white/18", className)}>
      <div className="flex items-center justify-between gap-3">
        <p className="truncate text-sm text-muted-foreground">{title}</p>
        {Icon ? (
          <div className="shrink-0 rounded-md border border-border bg-background/50 p-2 text-muted-foreground">
            <Icon className="size-4" />
          </div>
        ) : (
          <StatusBadge label={tone} tone={tone} compact className="shrink-0" />
        )}
      </div>
      <p className="mt-2 text-lg font-semibold leading-6">{value}</p>
      {description ? <p className="mt-2 text-xs leading-5 text-muted-foreground">{description}</p> : null}
    </div>
  );
}
