"use client";

import { useMutation } from "@tanstack/react-query";
import { toast } from "sonner";
import { Play } from "lucide-react";
import { useState } from "react";
import type { SkillInfo } from "@/components/skills/skill-card";
import { sendChat } from "@/lib/api/chat";
import { useChatStore } from "@/lib/stores/chat-store";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { MarkdownMessage } from "@/components/chat/markdown-message";
import { ChatMetadata } from "@/components/chat/chat-metadata";
import { CommandCard } from "@/components/ui/command-card";
import { EmptyState } from "@/components/ui/empty-state";

export function SkillPlayground({ skill }: { skill: SkillInfo }) {
  const [message, setMessage] = useState(skill.examples[0] ?? "");
  const setSources = useChatStore((state) => state.setSources);
  const mutation = useMutation({
    mutationFn: sendChat,
    onSuccess: (response) => {
      setSources(response.sources);
      toast.success(`Skill ${skill.title} respondio`);
    },
    onError: (error) => toast.error(error instanceof Error ? error.message : "Error al probar skill"),
  });

  return (
    <CommandCard icon={skill.icon} title={`Playground: ${skill.title}`} description="Un solo banco de pruebas para mantener la pantalla limpia.">
      <div className="grid gap-3 lg:grid-cols-[1fr_0.9fr]">
        <div className="space-y-3">
          <label className="space-y-1 text-sm text-muted-foreground">
            Prompt
            <Textarea value={message} onChange={(event) => setMessage(event.target.value)} className="min-h-32 bg-background/55" />
          </label>
          <div className="flex flex-wrap items-center gap-2">
            <Button disabled={!message.trim() || mutation.isPending} onClick={() => mutation.mutate({ message, mode: skill.mode, use_rag: "auto", top_k: 5, collection: "ui_ux" })}>
              <Play className="size-4" />
              Ejecutar skill
            </Button>
            {skill.examples.map((example) => (
              <button key={example} type="button" onClick={() => setMessage(example)} className="focus-ring rounded-md border border-border px-2 py-1 text-xs text-muted-foreground hover:text-foreground">
                {example}
              </button>
            ))}
          </div>
        </div>
        <div className="min-h-48 rounded-lg border border-border bg-background/40 p-3">
          <ChatMetadata response={mutation.data} />
          {mutation.data?.answer ? (
            <div className="mt-3 text-sm"><MarkdownMessage content={mutation.data.answer} /></div>
          ) : (
            <EmptyState title="Sin resultado todavia" description="Ejecuta el skill seleccionado para ver respuesta, metadata y fuentes." compact />
          )}
        </div>
      </div>
    </CommandCard>
  );
}
