import { StatusBadge } from "@/components/ui/status-badge";
import type { StatusTone } from "@/lib/config/design-tokens";

export function StatusPill({ label, tone = "idle", detail }: { label: string; tone?: StatusTone; detail?: string }) {
  return <StatusBadge label={label} tone={tone} detail={detail} compact />;
}
