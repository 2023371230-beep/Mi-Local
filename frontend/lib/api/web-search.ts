import { apiFetch } from "@/lib/api/client";
import { webSearchResponseSchema } from "@/lib/types/api";

export function searchWeb(input: { query: string; top_k?: number; sources?: string[]; optimization_mode?: string }) {
  return apiFetch("/web/search", webSearchResponseSchema, {
    method: "POST",
    body: JSON.stringify(input),
    timeoutMs: 240_000,
  });
}
