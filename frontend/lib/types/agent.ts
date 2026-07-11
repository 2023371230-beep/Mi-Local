import { z } from "zod";

export const agentStepSchema = z.object({
  index: z.number(),
  kind: z.string(),
  description: z.string(),
  path: z.string().nullable().optional(),
  command: z.string().nullable().optional(),
  status: z.string(),
  diff: z.string().nullable().optional(),
  output: z.string().nullable().optional(),
  error: z.string().nullable().optional(),
});

export const agentSessionSchema = z.object({
  session_id: z.string(),
  workspace: z.string(),
  tree: z.array(z.string()),
  goal: z.string().nullable().optional(),
  steps: z.array(agentStepSchema),
  created_at: z.string(),
  events: z.array(z.string()),
});

export type AgentStep = z.infer<typeof agentStepSchema>;
export type AgentSession = z.infer<typeof agentSessionSchema>;
