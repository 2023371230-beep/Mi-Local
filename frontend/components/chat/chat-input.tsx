"use client";

import { ArrowUp, ChevronDown, Copy, Database, Download, FileText, Globe, Plus, Trash2 } from "lucide-react";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import type { ChatMode, RagMode } from "@/lib/types/api";
import { getModels } from "@/lib/api/models";
import { getCollections } from "@/lib/api/rag";
import { cn } from "@/lib/utils";
import { Textarea } from "@/components/ui/textarea";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuRadioGroup,
  DropdownMenuRadioItem,
  DropdownMenuSeparator,
  DropdownMenuSub,
  DropdownMenuSubContent,
  DropdownMenuSubTrigger,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

const skillLabels: Record<string, string> = {
  auto: "Auto",
  programacion: "Programacion",
  ui_ux: "UI/UX",
  ciberseguridad: "Ciberseguridad",
  bases_datos: "Bases de datos",
  rag: "RAG local",
  general: "General",
};

const skills = Object.keys(skillLabels) as ChatMode[];

export function ChatInput({
  disabled,
  onSubmit,
  onClear,
  onExport,
  onCopyLast,
}: {
  disabled?: boolean;
  onSubmit: (input: { message: string; mode: ChatMode; use_rag: RagMode; collection?: string; top_k: number; model?: string }) => void;
  onClear: () => void;
  onExport: () => void;
  onCopyLast: () => void;
}) {
  const router = useRouter();
  const [message, setMessage] = useState("");
  const [skill, setSkill] = useState<ChatMode>("auto");
  const [webOn, setWebOn] = useState(false);
  const [useRag, setUseRag] = useState<RagMode>("auto");
  const [collection, setCollection] = useState("auto");
  const [topK, setTopK] = useState("5");
  const [model, setModel] = useState("auto");

  const models = useQuery({ queryKey: ["models"], queryFn: getModels, staleTime: 60_000 });
  const collections = useQuery({ queryKey: ["collections"], queryFn: getCollections, staleTime: 60_000 });

  const modelNames: string[] = (models.data?.models ?? [])
    .map((item) => String((item as Record<string, unknown>).name ?? (item as Record<string, unknown>).model ?? ""))
    .filter(Boolean);
  const collectionNames = collections.data?.collections ?? [];

  const submit = () => {
    if (disabled || !message.trim()) return;
    onSubmit({
      message,
      mode: webOn ? "web" : skill,
      use_rag: useRag,
      collection: collection !== "auto" ? collection : undefined,
      top_k: Number(topK),
      ...(model !== "auto" ? { model } : {}),
    });
    setMessage("");
  };

  return (
    <div className="surface-elevated rounded-3xl border border-white/10 p-2 shadow-lg shadow-black/20">
      <label className="sr-only" htmlFor="chat-message">Mensaje</label>
      <Textarea
        id="chat-message"
        value={message}
        onChange={(event) => setMessage(event.target.value)}
        onKeyDown={(event) => {
          if (event.key === "Enter" && !event.shiftKey) {
            event.preventDefault();
            submit();
          }
        }}
        placeholder="Pregunta lo que quieras..."
        className="max-h-44 min-h-[52px] resize-none border-0 bg-transparent px-3 py-2 text-sm leading-6 shadow-none focus-visible:border-0 focus-visible:ring-0"
      />

      <div className="flex items-center gap-1.5 px-1 pb-1">
        <DropdownMenu>
          <DropdownMenuTrigger
            aria-label="Mas opciones"
            className="focus-ring grid size-9 shrink-0 place-items-center rounded-full border border-white/12 text-muted-foreground transition-colors hover:bg-muted hover:text-foreground"
          >
            <Plus className="size-4" />
          </DropdownMenuTrigger>
          <DropdownMenuContent align="start" className="w-60">
            <DropdownMenuGroup>
              <DropdownMenuLabel>Opciones</DropdownMenuLabel>
            </DropdownMenuGroup>
            <DropdownMenuSub>
              <DropdownMenuSubTrigger>Modelo: {model === "auto" ? "auto" : model}</DropdownMenuSubTrigger>
              <DropdownMenuSubContent className="max-h-64 overflow-y-auto">
                <DropdownMenuRadioGroup value={model} onValueChange={setModel}>
                  <DropdownMenuRadioItem value="auto">auto (segun skill)</DropdownMenuRadioItem>
                  {modelNames.map((name) => (
                    <DropdownMenuRadioItem key={name} value={name}>{name}</DropdownMenuRadioItem>
                  ))}
                </DropdownMenuRadioGroup>
              </DropdownMenuSubContent>
            </DropdownMenuSub>
            <DropdownMenuSub>
              <DropdownMenuSubTrigger>RAG: {useRag}</DropdownMenuSubTrigger>
              <DropdownMenuSubContent>
                <DropdownMenuRadioGroup value={useRag} onValueChange={(value) => setUseRag(value as RagMode)}>
                  <DropdownMenuRadioItem value="auto">auto</DropdownMenuRadioItem>
                  <DropdownMenuRadioItem value="true">siempre</DropdownMenuRadioItem>
                  <DropdownMenuRadioItem value="false">nunca</DropdownMenuRadioItem>
                </DropdownMenuRadioGroup>
              </DropdownMenuSubContent>
            </DropdownMenuSub>
            <DropdownMenuSub>
              <DropdownMenuSubTrigger>Coleccion: {collection}</DropdownMenuSubTrigger>
              <DropdownMenuSubContent>
                <DropdownMenuRadioGroup value={collection} onValueChange={setCollection}>
                  <DropdownMenuRadioItem value="auto">auto</DropdownMenuRadioItem>
                  {collectionNames.map((name) => (
                    <DropdownMenuRadioItem key={name} value={name}>{name}</DropdownMenuRadioItem>
                  ))}
                </DropdownMenuRadioGroup>
              </DropdownMenuSubContent>
            </DropdownMenuSub>
            <DropdownMenuSub>
              <DropdownMenuSubTrigger>Top K: {topK}</DropdownMenuSubTrigger>
              <DropdownMenuSubContent>
                <DropdownMenuRadioGroup value={topK} onValueChange={setTopK}>
                  {["3", "5", "8", "12"].map((value) => (
                    <DropdownMenuRadioItem key={value} value={value}>{value}</DropdownMenuRadioItem>
                  ))}
                </DropdownMenuRadioGroup>
              </DropdownMenuSubContent>
            </DropdownMenuSub>
            <DropdownMenuSeparator />
            <DropdownMenuItem onSelect={() => router.push("/documents")}>
              <FileText className="size-4" /> Ingestar documentos
            </DropdownMenuItem>
            <DropdownMenuItem onSelect={() => router.push("/rag")}>
              <Database className="size-4" /> Consultar RAG
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem onSelect={onExport}>
              <Download className="size-4" /> Exportar chat
            </DropdownMenuItem>
            <DropdownMenuItem onSelect={onCopyLast}>
              <Copy className="size-4" /> Copiar ultima respuesta
            </DropdownMenuItem>
            <DropdownMenuItem variant="destructive" onSelect={onClear}>
              <Trash2 className="size-4" /> Limpiar chat
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>

        <button
          type="button"
          aria-label="Buscar en web"
          aria-pressed={webOn}
          title={webOn ? "Busqueda web activada (Vane/SearXNG)" : "Activar busqueda web"}
          onClick={() => setWebOn((value) => !value)}
          className={cn(
            "focus-ring grid size-9 shrink-0 place-items-center rounded-full border transition-colors",
            webOn
              ? "border-primary/50 bg-primary/15 text-primary"
              : "border-white/12 text-muted-foreground hover:bg-muted hover:text-foreground",
          )}
        >
          <Globe className="size-4" />
        </button>

        <div className="flex-1" />

        <DropdownMenu>
          <DropdownMenuTrigger
            aria-label="Elegir skill"
            className="focus-ring flex h-9 shrink-0 items-center gap-1.5 rounded-full border border-white/12 px-3 text-sm text-foreground/85 transition-colors hover:bg-muted"
          >
            {webOn ? "Web" : skillLabels[skill]}
            <ChevronDown className="size-3.5 text-muted-foreground" />
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-52">
            <DropdownMenuGroup>
              <DropdownMenuLabel>Skill</DropdownMenuLabel>
            </DropdownMenuGroup>
            <DropdownMenuRadioGroup
              value={skill}
              onValueChange={(value) => {
                setSkill(value as ChatMode);
                setWebOn(false);
              }}
            >
              {skills.map((item) => (
                <DropdownMenuRadioItem key={item} value={item}>{skillLabels[item]}</DropdownMenuRadioItem>
              ))}
            </DropdownMenuRadioGroup>
          </DropdownMenuContent>
        </DropdownMenu>

        <button
          type="button"
          aria-label="Enviar mensaje"
          disabled={disabled || !message.trim()}
          onClick={submit}
          className="focus-ring grid size-9 shrink-0 place-items-center rounded-full bg-primary text-primary-foreground transition-opacity hover:opacity-90 disabled:opacity-35"
        >
          <ArrowUp className="size-4" />
        </button>
      </div>
    </div>
  );
}
