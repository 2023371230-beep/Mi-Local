"use client";

import { usePathname } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { Bot, BrainCircuit, ChevronsLeft, ChevronsRight, Database, FileText, Home, ListTree, MessageSquare, ScrollText, Settings, TerminalSquare, X } from "lucide-react";
import { useState } from "react";
import { getHealth } from "@/lib/api/health";
import { useUiStore } from "@/lib/stores/ui-store";
import { cn } from "@/lib/utils";
import { Switch } from "@/components/ui/switch";
import { Button } from "@/components/ui/button";
import { Sheet, SheetContent, SheetHeader, SheetTitle } from "@/components/ui/sheet";
import { StatusBadge } from "@/components/ui/status-badge";
import { SidebarItem } from "@/components/layout/sidebar-item";

const navItems = [
  { href: "/", label: "Dashboard", icon: Home },
  { href: "/chat", label: "Chat", icon: MessageSquare },
  { href: "/skills", label: "Skills", icon: BrainCircuit },
  { href: "/rag", label: "RAG", icon: Database },
  { href: "/documents", label: "Documents", icon: FileText },
  { href: "/agent", label: "Agent", icon: Bot },
  { href: "/models", label: "Models", icon: ListTree },
  { href: "/logs", label: "Logs", icon: ScrollText },
  { href: "/settings", label: "Settings", icon: Settings },
];

// Modo simple: solo lo esencial para el uso diario.
const simpleNavHrefs = new Set(["/chat", "/documents", "/settings"]);

function SidebarContent({
  collapsed,
  onToggleCollapsed,
  onNavigate,
}: {
  collapsed?: boolean;
  onToggleCollapsed?: () => void;
  onNavigate?: () => void;
}) {
  const pathname = usePathname();
  const { uiMode, setState } = useUiStore();
  const items = uiMode === "simple" ? navItems.filter((item) => simpleNavHrefs.has(item.href)) : navItems;
  const health = useQuery({ queryKey: ["health"], queryFn: getHealth, staleTime: 15_000 });
  const apiOk = health.data?.status === "ok";
  const webSearch = health.data?.web_search ?? {};
  const webOk = Boolean(webSearch.search_endpoint);
  const webTone = webOk ? "ok" : apiOk ? "degraded" : "error";

  return (
    <div className="flex h-full flex-col">
      <div className={cn("flex h-16 items-center gap-3 border-b border-sidebar-border px-3", collapsed && "justify-center px-2")}>
        <div className="grid size-9 shrink-0 place-items-center rounded-lg border border-sidebar-border bg-sidebar-accent text-sidebar-primary">
          <TerminalSquare className="size-5" />
        </div>
        {!collapsed ? (
          <div className="min-w-0">
            <div className="truncate text-sm font-semibold text-sidebar-foreground">Modelo IA</div>
            <div className="truncate font-mono text-[11px] text-sidebar-foreground/45">local command center</div>
          </div>
        ) : null}
      </div>

      <nav className="min-h-0 flex-1 space-y-1 overflow-y-auto p-2 pt-3">
        {items.map((item) => (
          <SidebarItem
            key={item.href}
            href={item.href}
            label={item.label}
            icon={item.icon}
            active={pathname === item.href}
            collapsed={collapsed}
            onNavigate={onNavigate}
          />
        ))}
      </nav>

      <div className="space-y-2 border-t border-sidebar-border p-2">
        {!collapsed ? (
          <label className="flex items-center justify-between gap-2 rounded-lg border border-sidebar-border bg-sidebar-accent/45 px-3 py-2 text-xs text-sidebar-foreground/70">
            Modo pro
            <Switch
              checked={uiMode === "pro"}
              onCheckedChange={(checked) => setState({ uiMode: checked ? "pro" : "simple", uiModeChosen: true })}
              aria-label="Cambiar entre modo simple y modo pro"
            />
          </label>
        ) : null}
        {!collapsed ? (
          <div className="rounded-lg border border-sidebar-border bg-sidebar-accent/45 p-2">
            <div className="flex items-center justify-between gap-2">
              <StatusBadge label="api" tone={apiOk ? "ok" : "error"} compact />
              <StatusBadge label="web" tone={webTone} compact />
            </div>
            <p className="mt-2 text-xs leading-5 text-sidebar-foreground/50">
              {apiOk ? "Backend conectado." : "Backend no disponible."}
            </p>
          </div>
        ) : null}
        {onToggleCollapsed ? (
          <Button variant="ghost" size="icon" className={cn("w-full", collapsed && "w-10")} onClick={onToggleCollapsed} aria-label="Colapsar sidebar">
            {collapsed ? <ChevronsRight className="size-4" /> : <ChevronsLeft className="size-4" />}
          </Button>
        ) : null}
      </div>
    </div>
  );
}

export function AppSidebar({
  mobileOpen,
  onMobileOpenChange,
}: {
  mobileOpen: boolean;
  onMobileOpenChange: (open: boolean) => void;
}) {
  const [collapsed, setCollapsed] = useState(false);

  return (
    <>
      <aside className={cn("hidden shrink-0 border-r border-sidebar-border bg-sidebar md:block", collapsed ? "w-[72px]" : "w-64")}>
        <SidebarContent collapsed={collapsed} onToggleCollapsed={() => setCollapsed((value) => !value)} />
      </aside>
      <Sheet open={mobileOpen} onOpenChange={onMobileOpenChange}>
        <SheetContent side="left" className="w-[88vw] max-w-sm border-sidebar-border bg-sidebar p-0" showCloseButton={false}>
          <SheetHeader className="sr-only">
            <SheetTitle>Navegacion</SheetTitle>
          </SheetHeader>
          <Button variant="ghost" size="icon" className="absolute right-3 top-3 z-10" onClick={() => onMobileOpenChange(false)} aria-label="Cerrar navegacion">
            <X className="size-4" />
          </Button>
          <SidebarContent onNavigate={() => onMobileOpenChange(false)} />
        </SheetContent>
      </Sheet>
    </>
  );
}
