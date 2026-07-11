import type { ChatMessage } from "@/lib/types/chat";
import { cn } from "@/lib/utils";
import { MarkdownMessage } from "@/components/chat/markdown-message";
import { ChatMetadata } from "@/components/chat/chat-metadata";

export function MessageBubble({ message }: { message: ChatMessage }) {
  const user = message.role === "user";
  return (
    <div className={cn("flex", user ? "justify-end" : "justify-start")}>
      <div className={cn("max-w-[92%] rounded-lg border px-3 py-2 text-sm md:max-w-[86%]", user ? "border-primary/30 bg-primary/15" : "surface bg-card/70")}>
        {!user && message.response ? <div className="mb-3"><ChatMetadata response={message.response} compact /></div> : null}
        <MarkdownMessage content={message.content} />
        <div className="mt-2 font-mono text-[10px] text-muted-foreground">{new Date(message.createdAt).toLocaleTimeString()}</div>
      </div>
    </div>
  );
}
