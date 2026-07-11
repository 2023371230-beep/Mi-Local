import { apiFetch } from "@/lib/api/client";
import { appConfig } from "@/lib/config/app-config";
import { chatResponseSchema, type ChatRequest, type ChatResponse, type Source } from "@/lib/types/api";

export function sendChat(request: ChatRequest) {
  return apiFetch("/chat", chatResponseSchema, {
    method: "POST",
    body: JSON.stringify(request),
    timeoutMs: 240_000,
  });
}

export type ChatStreamCallbacks = {
  onMeta?: (meta: { skill: string; model: string }) => void;
  onDelta: (chunk: string) => void;
  onSources?: (sources: Source[]) => void;
};

/** Consume POST /chat/stream (NDJSON) y devuelve la respuesta ensamblada. */
export async function sendChatStream(
  request: ChatRequest,
  callbacks: ChatStreamCallbacks,
  signal?: AbortSignal,
): Promise<ChatResponse> {
  const response = await fetch(`${appConfig.backendUrl}/chat/stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
    signal,
  });
  if (!response.ok || !response.body) {
    throw new Error(`Backend respondio ${response.status}`);
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  let answer = "";
  let skill = "";
  let model = "";
  let sources: Source[] = [];
  let done: Record<string, unknown> = {};

  const handleLine = (line: string) => {
    if (!line.trim()) return;
    let event: Record<string, unknown>;
    try {
      event = JSON.parse(line);
    } catch {
      return;
    }
    if (event.type === "meta") {
      skill = String(event.skill ?? "");
      model = String(event.model ?? "");
      callbacks.onMeta?.({ skill, model });
    } else if (event.type === "delta") {
      const chunk = String(event.data ?? "");
      answer += chunk;
      callbacks.onDelta(chunk);
    } else if (event.type === "sources") {
      sources = (event.data as Source[]) ?? [];
      callbacks.onSources?.(sources);
    } else if (event.type === "done") {
      done = event;
    } else if (event.type === "error") {
      throw new Error(String(event.data ?? "Error en el stream"));
    }
  };

  for (;;) {
    const { value, done: finished } = await reader.read();
    if (finished) break;
    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop() ?? "";
    for (const line of lines) handleLine(line);
  }
  if (buffer.trim()) handleLine(buffer);

  return {
    answer,
    skill_used: skill,
    model_used: model,
    rag_used: Boolean(done.rag_used),
    web_used: Boolean(done.web_used),
    web_engine: (done.web_engine as string | null) ?? null,
    web_fallback_used: Boolean(done.web_fallback_used),
    sources,
    latency_ms: Number(done.latency_ms ?? 0),
  };
}
