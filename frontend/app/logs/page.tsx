import { LogsView } from "@/components/logs/logs-view";
import { SectionHeader } from "@/components/ui/section-header";
import { pageShell } from "@/lib/config/design-tokens";

export default function LogsPage() {
  return (
    <div className={pageShell}>
      <SectionHeader eyebrow="Logs" title="Diagnostico del sistema" description="Filtra eventos, revisa timeouts de Vane y copia logs sin leer un muro crudo de texto." />
      <LogsView />
    </div>
  );
}
