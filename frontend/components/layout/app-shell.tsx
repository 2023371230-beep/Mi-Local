"use client";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState, type ReactNode } from "react";
import { SidebarProvider } from "@/components/ui/sidebar";
import { AppSidebar } from "@/components/layout/app-sidebar";
import { TopBar } from "@/components/layout/top-bar";
import { RightContextPanel } from "@/components/layout/right-context-panel";
import { useUiStore } from "@/lib/stores/ui-store";

const SIMPLE_ROUTES = new Set(["/chat", "/documents", "/settings"]);

function UiModeManager() {
  const { uiMode, uiModeChosen, setState } = useUiStore();
  const pathname = usePathname();
  const router = useRouter();

  // Mobile arranca en simple la primera vez (hasta que el usuario elija).
  useEffect(() => {
    if (!uiModeChosen && window.innerWidth < 768 && uiMode !== "simple") {
      setState({ uiMode: "simple" });
    }
  }, [uiModeChosen, uiMode, setState]);

  // En modo simple las rutas pro redirigen al chat.
  useEffect(() => {
    if (uiMode === "simple" && !SIMPLE_ROUTES.has(pathname)) {
      router.replace("/chat");
    }
  }, [uiMode, pathname, router]);

  return null;
}

export function AppShell({ children }: { children: ReactNode }) {
  const [queryClient] = useState(() => new QueryClient());
  const [mobileNavOpen, setMobileNavOpen] = useState(false);
  const [contextOpen, setContextOpen] = useState(false);
  return (
    <QueryClientProvider client={queryClient}>
      <SidebarProvider>
        <UiModeManager />
        <div className="app-bg flex min-h-screen w-full overflow-hidden">
          <AppSidebar mobileOpen={mobileNavOpen} onMobileOpenChange={setMobileNavOpen} />
          <div className="flex min-w-0 flex-1 flex-col">
            <TopBar onMenuClick={() => setMobileNavOpen(true)} onContextClick={() => setContextOpen(true)} />
            <div className="flex min-h-0 flex-1">
              <main className="min-w-0 flex-1 overflow-y-auto p-4 md:p-5">{children}</main>
              <RightContextPanel open={contextOpen} onOpenChange={setContextOpen} />
            </div>
          </div>
        </div>
      </SidebarProvider>
    </QueryClientProvider>
  );
}
