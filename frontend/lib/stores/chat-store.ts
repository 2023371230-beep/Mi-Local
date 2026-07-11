"use client";

import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { ChatMessage } from "@/lib/types/chat";
import type { Source } from "@/lib/types/api";

type ChatState = {
  messages: ChatMessage[];
  sources: Source[];
  setSources: (sources: Source[]) => void;
  addMessage: (message: ChatMessage) => void;
  clear: () => void;
};

export const useChatStore = create<ChatState>()(
  persist(
    (set) => ({
      messages: [],
      sources: [],
      setSources: (sources) => set({ sources }),
      addMessage: (message) => set((state) => ({ messages: [...state.messages, message] })),
      clear: () => set({ messages: [], sources: [] }),
    }),
    {
      name: "chat-history",
      // Solo lo esencial: el historial sobrevive un F5 sin llenar localStorage.
      partialize: (state) => ({ messages: state.messages.slice(-100), sources: state.sources }),
    },
  ),
);
