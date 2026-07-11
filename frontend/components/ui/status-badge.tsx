import { cn } from "@/lib/utils";
import { statusTone, type StatusTone } from "@/lib/config/design-tokens";

export function StatusBadge({
  label,
  tone = "idle",
  detail,
  compact,
  withIcon,
  className,
}: {
  label: string;
  tone?: StatusTone;
  detail?: string;
  compact?: boolean;
  withIcon?: boolean;
  className?: string;
}) {
  const toneConfig = statusTone[tone];
  const Icon = toneConfig.icon;
  return (
    <span
      className={cn(
        "inline-flex min-w-0 items-center gap-1.5 rounded-md border px-2 py-1 text-xs font-medium",
        toneConfig.className,
        compact && "h-6 px-1.5 py-0 font-mono text-[11px]",
        className,
      )}
    >
      {withIcon ? <Icon className="size-3.5 shrink-0" /> : <span className={cn("size-1.5 shrink-0 rounded-full", toneConfig.dot)} />}
      <span className="truncate">{label}</span>
      {detail ? <span className="truncate text-white/55">{detail}</span> : null}
    </span>
  );
}
