"use client";

import { useMutation } from "@tanstack/react-query";
import { useState } from "react";
import { toast } from "sonner";
import { sendChatStream } from "@/lib/api/chat";
import { useChatStore } from "@/lib/stores/chat-store";
import type { ChatRequest, ChatResponse } from "@/lib/types/api";
import { MessageList } from "@/components/chat/message-list";
import { ChatInput } from "@/components/chat/chat-input";

export function ChatView() {
  const { messages, addMessage, clear, setSources } = useChatStore();
  const [streamingText, setStreamingText] = useState("");

  const mutation = useMutation({
    mutationFn: (input: ChatRequest) =>
      sendChatStream(input, {
        onDelta: (chunk) => setStreamingText((current) => current + chunk),
      }),
    onSuccess: (response: ChatResponse) => {
      addMessage({
        id: crypto.randomUUID(),
        role: "assistant",
        content: response.answer,
        createdAt: new Date().toISOString(),
        response,
      });
      setSources(response.sources);
      if (response.web_fallback_used) {
        toast.warning("Vane no tuvo fuentes; se uso SearXNG como fallback.");
      }
    },
    onError: (error) => toast.error(error instanceof Error ? error.message : "Error de chat"),
    onSettled: () => setStreamingText(""),
  });

  const submit = (input: ChatRequest) => {
    addMessage({ id: crypto.randomUUID(), role: "user", content: input.message, createdAt: new Date().toISOString() });
    setStreamingText("");
    mutation.mutate(input);
  };

  const copyLast = async () => {
    const lastAssistant = [...messages].reverse().find((message) => message.role === "assistant");
    if (!lastAssistant) {
      toast.info("Todavia no hay respuesta para copiar");
      return;
    }
    await navigator.clipboard.writeText(lastAssistant.content);
    toast.success("Ultima respuesta copiada");
  };

  const exportChat = () => {
    const markdown = messages.map((m) => "## " + m.role + "\n\n" + m.content).join("\n\n");
    const blob = new Blob([markdown], { type: "text/markdown" });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = "chat-export.md";
    anchor.click();
    URL.revokeObjectURL(url);
    toast.success("Chat exportado");
  };

  return (
    <div className="mx-auto flex h-[calc(100dvh-7.5rem)] w-full max-w-3xl flex-col gap-3">
      <div className="min-h-0 flex-1">
        <MessageList
          messages={messages}
          loading={mutation.isPending}
          streamingText={streamingText}
          onExample={(message) => submit({ message, mode: "auto", use_rag: "auto", top_k: 5 })}
        />
      </div>
      <ChatInput
        disabled={mutation.isPending}
        onClear={clear}
        onCopyLast={copyLast}
        onExport={exportChat}
        onSubmit={submit}
      />
    </div>
  );
}
