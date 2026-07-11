"use client";

import { useQuery } from "@tanstack/react-query";
import { getCollections } from "@/lib/api/rag";
import { StatusBadge } from "@/components/ui/status-badge";
import { LoadingState } from "@/components/ui/loading-state";
import { EmptyState } from "@/components/ui/empty-state";

export function CollectionsView() {
  const query = useQuery({ queryKey: ["collections"], queryFn: getCollections, staleTime: 30_000 });
  if (query.isLoading) return <LoadingState label="Cargando colecciones" />;
  const collections = query.data?.collections ?? [];
  if (collections.length === 0) return <EmptyState title="Sin colecciones visibles" description="Ingesta documentos para crear contexto local." compact />;
  return <div className="flex flex-wrap gap-2">{collections.map((item) => <StatusBadge key={item} label={item} tone="info" />)}</div>;
}
