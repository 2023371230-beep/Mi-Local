"use client";

import { IngestPanel } from "@/components/rag/ingest-panel";
import { DocumentGenerator } from "@/components/documents/document-generator";
import { SectionHeader } from "@/components/ui/section-header";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { pageShell } from "@/lib/config/design-tokens";

export default function DocumentsPage() {
  return (
    <div className={pageShell}>
      <SectionHeader
        eyebrow="Documents"
        title="Documentos"
        description="Genera documentos profesionales con el modelo local o ingesta material hacia tu RAG."
      />
      <Tabs defaultValue="generar">
        <TabsList>
          <TabsTrigger value="generar">Generar</TabsTrigger>
          <TabsTrigger value="ingestar">Ingestar al RAG</TabsTrigger>
        </TabsList>
        <TabsContent value="generar" className="mt-4">
          <DocumentGenerator />
        </TabsContent>
        <TabsContent value="ingestar" className="mt-4">
          <IngestPanel />
        </TabsContent>
      </Tabs>
    </div>
  );
}
