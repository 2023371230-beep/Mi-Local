import { CollectionsView } from "@/components/rag/collections-view";
import { RagQueryPanel } from "@/components/rag/rag-query-panel";
import { SectionHeader } from "@/components/ui/section-header";
import { CommandCard } from "@/components/ui/command-card";
import { Database } from "lucide-react";
import { pageShell } from "@/lib/config/design-tokens";

export default function RagPage() {
  return (
    <div className={pageShell}>
      <SectionHeader eyebrow="RAG" title="Conocimiento local" description="Consulta tus PDFs y documentacion con fuentes visibles y control de coleccion cuando lo necesites." />
      <CommandCard icon={Database} title="Colecciones disponibles" description="Contextos locales listos para consulta.">
        <CollectionsView />
      </CommandCard>
      <RagQueryPanel />
    </div>
  );
}
