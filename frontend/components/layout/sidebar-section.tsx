"use client";

import { ChevronDown } from "lucide-react";
import { useState } from "react";
import type { ReactNode } from "react";
import { cn } from "@/lib/utils";

export function SidebarSection({
  title,
  children,
  collapsed,
  defaultOpen = true,
}: {
  title: string;
  children: ReactNode;
  collapsed?: boolean;
  defaultOpen?: boolean;
}) {
  const [open, setOpen] = useState(defaultOpen);

  if (collapsed) {
    return <div className="space-y-1 border-t border-sidebar-border pt-2 first:border-t-0 first:pt-0">{children}</div>;
  }

  return (
    <section className="space-y-1">
      <button
        type="button"
        onClick={() => setOpen((value) => !value)}
        className="focus-ring flex h-7 w-full items-center justify-between rounded-md px-2 text-[11px] font-medium uppercase text-sidebar-foreground/45 hover:text-sidebar-foreground/75"
      >
        <span>{title}</span>
        <ChevronDown className={cn("size-3.5 transition-transform", !open && "-rotate-90")} />
      </button>
      {open ? <div className="space-y-1">{children}</div> : null}
    </section>
  );
}
