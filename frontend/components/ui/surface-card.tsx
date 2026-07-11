import type { ReactNode } from "react";
import { cn } from "@/lib/utils";

export function SurfaceCard({
  children,
  elevated,
  className,
}: {
  children: ReactNode;
  elevated?: boolean;
  className?: string;
}) {
  return <div className={cn(elevated ? "surface-elevated" : "surface", "rounded-lg", className)}>{children}</div>;
}
