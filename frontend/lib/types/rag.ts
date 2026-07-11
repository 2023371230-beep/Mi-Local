import type { Source } from "@/lib/types/api";

export type RagQueryResult = {
  answer: string;
  sources: Source[];
};
