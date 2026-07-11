import type { LucideIcon } from "lucide-react";
import { Inbox } from "lucide-react";
import type { ReactNode } from "react";
import { cn } from "@/lib/utils";

export function EmptyState({
  icon: Icon = Inbox,
  title,
  description,
  action,
  compact,
  className,
}: {
  icon?: LucideIcon;
  title: string;
  description?: string;
  action?: ReactNode;
  compact?: boolean;
  className?: string;
}) {
  return (
    <div className={cn("surface-muted flex flex-col items-start gap-3 rounded-lg border border-dashed p-5", compact && "p-3", className)}>
      <div className="rounded-md border border-border bg-background/60 p-2 text-muted-foreground">
        <Icon className="size-4" />
      </div>
      <div>
        <div className={cn("font-medium text-foreground", compact ? "text-sm" : "text-base")}>{title}</div>
        {description ? <p className="mt-1 text-sm leading-6 text-muted-foreground">{description}</p> : null}
      </div>
      {action ? <div>{action}</div> : null}
    </div>
  );
}
