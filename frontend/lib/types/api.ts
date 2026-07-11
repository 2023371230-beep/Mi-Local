import { z } from "zod";

export const sourceSchema = z.object({
  source: z.string(),
  title: z.string().nullable().optional(),
  content: z.string().nullable().optional(),
  path: z.string().nullable().optional(),
  filename: z.string().nullable().optional(),
  page: z.number().nullable().optional(),
  chunk_index: z.number().nullable().optional(),
  url: z.string().nullable().optional(),
  score: z.number().nullable().optional(),
});

export const healthSchema = z.object({
  status: z.string(),
  ollama: z.boolean(),
  chroma: z.boolean(),
  perplexica: z.boolean(),
  vane: z.boolean().optional().default(false),
  web_search: z.record(z.string(), z.unknown()).optional().default({}),
});

export const chatModeSchema = z.enum(["auto", "programacion", "ui_ux", "ciberseguridad", "bases_datos", "rag", "web", "general"]);
export const ragModeSchema = z.enum(["auto", "true", "false"]);

export const chatRequestSchema = z.object({
  message: z.string().min(1),
  mode: chatModeSchema.default("auto"),
  use_rag: ragModeSchema.default("auto"),
  collection: z.string().optional(),
  top_k: z.number().min(1).max(20).default(5),
  model: z.string().optional(),
});

export const chatResponseSchema = z.object({
  answer: z.string(),
  skill_used: z.string(),
  model_used: z.string(),
  rag_used: z.boolean(),
  web_used: z.boolean(),
  web_engine: z.string().nullable().optional(),
  web_fallback_used: z.boolean().optional(),
  sources: z.array(sourceSchema),
  latency_ms: z.number(),
});

export const modelsResponseSchema = z.object({
  models: z.array(z.record(z.string(), z.unknown())),
});

export const collectionsResponseSchema = z.object({
  collections: z.array(z.string()),
});

export const ingestResponseSchema = z.object({
  status: z.string(),
  files_processed: z.number(),
  chunks_created: z.number(),
  duplicates_skipped: z.number(),
  errors: z.array(z.string()),
});

export const logsResponseSchema = z.object({
  logs: z.array(z.union([z.string(), z.record(z.string(), z.unknown())])),
});

export const webSearchResponseSchema = z.object({
  answer: z.string(),
  web_used: z.boolean(),
  engine: z.string(),
  sources: z.array(sourceSchema),
  error: z.string().nullable().optional(),
  latency_ms: z.number(),
});

export type Source = z.infer<typeof sourceSchema>;
export type HealthResponse = z.infer<typeof healthSchema>;
export type ChatMode = z.infer<typeof chatModeSchema>;
export type RagMode = z.infer<typeof ragModeSchema>;
export type ChatRequest = z.infer<typeof chatRequestSchema>;
export type ChatResponse = z.infer<typeof chatResponseSchema>;
export type ModelsResponse = z.infer<typeof modelsResponseSchema>;
export type CollectionsResponse = z.infer<typeof collectionsResponseSchema>;
export type IngestResponse = z.infer<typeof ingestResponseSchema>;
export type LogsResponse = z.infer<typeof logsResponseSchema>;
export type WebSearchResponse = z.infer<typeof webSearchResponseSchema>;
