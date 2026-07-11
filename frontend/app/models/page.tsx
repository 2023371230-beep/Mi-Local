import { ModelsGrid } from "@/components/models/models-grid";
import { SectionHeader } from "@/components/ui/section-header";
import { CommandCard } from "@/components/ui/command-card";
import { Cpu } from "lucide-react";
import { pageShell } from "@/lib/config/design-tokens";

export default function ModelsPage() {
  return (
    <div className={pageShell}>
      <SectionHeader eyebrow="Models" title="Modelos locales" description="Vista legible de modelos Ollama: rol, tamano, cuantizacion y recomendacion de uso." />
      <CommandCard icon={Cpu} title="Inventario Ollama" description="qwen2.5 para general, qwen2.5-coder para codigo, qwen3-embedding para RAG ligero.">
        <ModelsGrid />
      </CommandCard>
    </div>
  );
}
