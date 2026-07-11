import { z } from "zod";
import { apiFetch } from "@/lib/api/client";
import { appConfig } from "@/lib/config/app-config";

export const documentGenerateResponseSchema = z.object({
  filename: z.string(),
  format: z.string(),
  doc_type: z.string(),
  markdown: z.string(),
  sources: z.array(z.record(z.string(), z.unknown())),
  latency_ms: z.number(),
});

export const documentOutputsResponseSchema = z.object({
  outputs: z.array(
    z.object({
      filename: z.string(),
      size_bytes: z.number(),
      modified_at: z.string(),
    }),
  ),
  doc_types: z.array(z.string()),
  formats: z.array(z.string()),
});

export type DocumentGenerateResponse = z.infer<typeof documentGenerateResponseSchema>;
export type DocumentOutputs = z.infer<typeof documentOutputsResponseSchema>;

export function generateDocument(input: {
  doc_type: string;
  title: string;
  instructions: string;
  output_format: string;
  use_rag: boolean;
  collection?: string;
}) {
  return apiFetch("/documents/generate", documentGenerateResponseSchema, {
    method: "POST",
    body: JSON.stringify(input),
    timeoutMs: 600_000,
  });
}

export function getDocumentOutputs() {
  return apiFetch("/documents/outputs", documentOutputsResponseSchema, { timeoutMs: 30_000 });
}

export function documentDownloadUrl(filename: string) {
  return `${appConfig.backendUrl}/documents/download/${encodeURIComponent(filename)}`;
}
