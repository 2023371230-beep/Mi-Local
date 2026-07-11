import type { ChatResponse } from "@/lib/types/api";

export type ChatMessage = {
  id: string;
  role: "user" | "assistant";
  content: string;
  createdAt: string;
  response?: ChatResponse;
};
