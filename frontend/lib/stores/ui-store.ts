"use client";

import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { ChatMode, RagMode } from "@/lib/types/api";

type UiState = {
  /** simple = chat limpio tipo Ollama; pro = centro de comando completo */
  uiMode: "simple" | "pro";
  /** true cuando el usuario eligio modo explicitamente (no auto-detectar mas) */
  uiModeChosen: boolean;
  backendUrl: string;
  theme: "dark" | "light";
  defaultMode: ChatMode;
  defaultRag: RagMode;
  defaultCollection: string;
  topK: number;
  rightPanel: boolean;
  compact: boolean;
  fontSize: number;
  setState: (patch: Partial<Omit<UiState, "setState">>) => void;
};

export const useUiStore = create<UiState>()(
  persist(
    (set) => ({
      uiMode: "pro",
      uiModeChosen: false,
      backendUrl: "http://127.0.0.1:8000",
      theme: "dark",
      defaultMode: "auto",
      defaultRag: "auto",
      defaultCollection: "ui_ux",
      topK: 5,
      rightPanel: true,
      compact: false,
      fontSize: 14,
      setState: (patch) => set(patch),
    }),
    { name: "modelo-ia-ui" },
  ),
);
