import { apiFetch } from "@/lib/api/client";
import { chatResponseSchema, collectionsResponseSchema, ingestResponseSchema } from "@/lib/types/api";

export function getCollections() {
  return apiFetch("/rag/collections", collectionsResponseSchema, { timeoutMs: 30_000 });
}

export function queryRag(input: { message: string; collection: string; top_k: number }) {
  return apiFetch("/rag/query", chatResponseSchema, {
    method: "POST",
    body: JSON.stringify(input),
    timeoutMs: 240_000,
  });
}

export function ingestDocuments(input: { path?: string; collection?: string; topic?: string; limit_files?: number }) {
  return apiFetch("/ingest", ingestResponseSchema, {
    method: "POST",
    body: JSON.stringify(input),
    timeoutMs: 600_000,
  });
}
