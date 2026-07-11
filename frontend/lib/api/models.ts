import { apiFetch } from "@/lib/api/client";
import { modelsResponseSchema } from "@/lib/types/api";

export function getModels() {
  return apiFetch("/models", modelsResponseSchema, { timeoutMs: 30_000 });
}
