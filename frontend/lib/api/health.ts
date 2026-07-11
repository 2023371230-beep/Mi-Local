import { apiFetch } from "@/lib/api/client";
import { healthSchema } from "@/lib/types/api";

export function getHealth() {
  return apiFetch("/health", healthSchema, { timeoutMs: 20_000 });
}
