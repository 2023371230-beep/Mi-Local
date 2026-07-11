import { motion } from "motion/react";
import type { ChatMessage } from "@/lib/types/chat";
import { ScrollArea } from "@/components/ui/scroll-area";
import { MessageBubble } from "@/components/chat/message-bubble";
import { MarkdownMessage } from "@/components/chat/markdown-message";
import { Bot } from "lucide-react";
import { LoadingState } from "@/components/ui/loading-state";

const examples = [
  "Crea una pagina React con Vite",
  "Consulta mis documentos UI/UX",
  "Analiza este log defensivamente",
  "Optimiza esta query PostgreSQL",
];

export function MessageList({
  messages,
  loading,
  streamingText,
  onExample,
}: {
  messages: ChatMessage[];
  loading?: boolean;
  streamingText?: string;
  onExample?: (message: string) => void;
}) {
  if (messages.length === 0 && !loading) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.35, ease: "easeOut" }}
        className="flex h-full flex-col items-center justify-center gap-4 px-4 text-center"
      >
        <div className="grid size-16 place-items-center rounded-full border border-white/10 bg-card">
          <Bot className="size-7 text-foreground/80" />
        </div>
        <div className="space-y-1">
          <p className="text-base font-medium">En que trabajamos hoy?</p>
          <p className="text-sm text-muted-foreground">
            Elige una skill, activa el globo para buscar en web o pregunta directo.
          </p>
        </div>
        <div className="flex max-w-md flex-wrap justify-center gap-2">
          {examples.map((example) => (
            <button
              key={example}
              type="button"
              onClick={() => onExample?.(example)}
              className="focus-ring rounded-full border border-white/10 bg-card/60 px-3 py-1.5 text-xs text-muted-foreground transition-colors hover:bg-muted hover:text-foreground"
            >
              {example}
            </button>
          ))}
        </div>
      </motion.div>
    );
  }

  return (
    <ScrollArea className="h-full">
      <div className="space-y-3 py-2">
        {messages.map((message, index) => (
          <motion.div
            key={message.id}
            initial={index >= messages.length - 2 ? { opacity: 0, y: 8 } : false}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.25, ease: "easeOut" }}
          >
            <MessageBubble message={message} />
          </motion.div>
        ))}
        {loading && streamingText ? (
          <div className="surface-muted rounded-lg border p-3 text-sm" aria-live="polite">
            <MarkdownMessage content={streamingText} />
            <span className="ml-0.5 inline-block h-4 w-1.5 animate-pulse rounded-sm bg-primary align-text-bottom" />
          </div>
        ) : null}
        {loading && !streamingText ? (
          <div className="surface-muted rounded-lg border p-3">
            <LoadingState label="El modelo local esta pensando" />
          </div>
        ) : null}
      </div>
    </ScrollArea>
  );
}
