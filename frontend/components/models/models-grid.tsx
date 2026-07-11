"use client";

import { useQuery } from "@tanstack/react-query";
import { getModels } from "@/lib/api/models";
import { ModelCard } from "@/components/models/model-card";
import { LoadingState } from "@/components/ui/loading-state";
import { EmptyState } from "@/components/ui/empty-state";

export function ModelsGrid() {
  const query = useQuery({ queryKey: ["models"], queryFn: getModels, staleTime: 60_000 });
  if (query.isLoading) return <LoadingState label="Cargando modelos de Ollama" />;
  const models = query.data?.models ?? [];
  if (models.length === 0) return <EmptyState title="Sin modelos visibles" description="Revisa que Ollama este activo y tenga modelos instalados." />;
  return <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">{models.map((model, index) => <ModelCard key={String(model.name ?? index)} model={model} />)}</div>;
}
