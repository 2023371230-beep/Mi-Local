import { appConfig } from "@/lib/config/app-config";
import type { ZodSchema } from "zod";

export class ApiError extends Error {
  constructor(message: string, public status?: number) {
    super(message);
  }
}

export async function apiFetch<T>(path: string, schema: ZodSchema<T>, init?: RequestInit & { timeoutMs?: number }): Promise<T> {
  const controller = new AbortController();
  const timeout = window.setTimeout(() => controller.abort(), init?.timeoutMs ?? 120_000);
  try {
    const response = await fetch(`${appConfig.backendUrl}${path}`, {
      ...init,
      headers: {
        "Content-Type": "application/json",
        ...init?.headers,
      },
      signal: controller.signal,
    });
    if (!response.ok) {
      throw new ApiError(`Backend responded with ${response.status}`, response.status);
    }
    const data = await response.json();
    return schema.parse(data);
  } finally {
    window.clearTimeout(timeout);
  }
}
