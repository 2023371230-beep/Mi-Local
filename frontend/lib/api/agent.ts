import { apiFetch } from "@/lib/api/client";
import { agentSessionSchema } from "@/lib/types/agent";

const PLAN_TIMEOUT = 600_000;

export function createAgentSession(workspacePath: string) {
  return apiFetch("/agent/sessions", agentSessionSchema, {
    method: "POST",
    body: JSON.stringify({ workspace_path: workspacePath }),
    timeoutMs: 60_000,
  });
}

export function proposeAgentPlan(sessionId: string, goal: string) {
  return apiFetch(`/agent/sessions/${sessionId}/plan`, agentSessionSchema, {
    method: "POST",
    body: JSON.stringify({ goal }),
    timeoutMs: PLAN_TIMEOUT,
  });
}

export function proposeAgentEdit(sessionId: string, stepIndex: number) {
  return apiFetch(`/agent/sessions/${sessionId}/steps/${stepIndex}/propose`, agentSessionSchema, {
    method: "POST",
    timeoutMs: PLAN_TIMEOUT,
  });
}

export function applyAgentStep(sessionId: string, stepIndex: number) {
  return apiFetch(`/agent/sessions/${sessionId}/steps/${stepIndex}/apply`, agentSessionSchema, {
    method: "POST",
    body: JSON.stringify({ approved: true }),
    timeoutMs: 180_000,
  });
}

export function rejectAgentStep(sessionId: string, stepIndex: number) {
  return apiFetch(`/agent/sessions/${sessionId}/steps/${stepIndex}/reject`, agentSessionSchema, {
    method: "POST",
    timeoutMs: 30_000,
  });
}

export function revertAgentStep(sessionId: string, stepIndex: number) {
  return apiFetch(`/agent/sessions/${sessionId}/steps/${stepIndex}/revert`, agentSessionSchema, {
    method: "POST",
    timeoutMs: 60_000,
  });
}
