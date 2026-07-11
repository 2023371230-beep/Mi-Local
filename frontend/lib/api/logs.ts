import { apiFetch } from "@/lib/api/client";
import { logsResponseSchema } from "@/lib/types/api";

export function getLogs(lines = 100) {
  return apiFetch(`/logs?lines=${lines}`, logsResponseSchema, { timeoutMs: 30_000 });
}
