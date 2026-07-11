"use client";

import type { LucideIcon } from "lucide-react";
import type { ChatMode } from "@/lib/types/api";
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";
import { Button } from "@/components/ui/button";
import { StatusBadge } from "@/components/ui/status-badge";

export type SkillInfo = {
  title: string;
  mode: ChatMode;
  model: string;
  description: string;
  icon: LucideIcon;
  when: string;
  rag: string;
  limitations: string;
  examples: string[];
};

export function SkillCard({ skill, selected, onSelect }: { skill: SkillInfo; selected?: boolean; onSelect: () => void }) {
  const Icon = skill.icon;
  return (
    <div className={selected ? "surface-elevated rounded-lg p-4" : "surface rounded-lg p-4"}>
      <div className="flex items-start justify-between gap-3">
        <div className="rounded-md border border-border bg-background/60 p-2 text-primary">
          <Icon className="size-5" />
        </div>
        <StatusBadge label={skill.mode} tone={selected ? "ok" : "idle"} compact />
      </div>
      <div className="mt-4">
        <h3 className="text-base font-semibold">{skill.title}</h3>
        <p className="mt-2 text-sm leading-6 text-muted-foreground">{skill.description}</p>
      </div>
      <div className="mt-4 flex items-center justify-between gap-2">
        <StatusBadge label={skill.model} tone="info" compact className="max-w-[170px]" />
        <Button size="sm" variant={selected ? "default" : "secondary"} onClick={onSelect}>Probar</Button>
      </div>
      <Accordion className="mt-3">
        <AccordionItem value="details" className="border-0">
          <AccordionTrigger className="py-2 text-xs text-muted-foreground hover:no-underline">Detalles</AccordionTrigger>
          <AccordionContent className="space-y-3 text-sm text-muted-foreground">
            <p><span className="text-foreground">Cuando usar:</span> {skill.when}</p>
            <p><span className="text-foreground">RAG:</span> {skill.rag}</p>
            <p><span className="text-foreground">Limites:</span> {skill.limitations}</p>
            <div className="flex flex-wrap gap-2">
              {skill.examples.map((example) => <span key={example} className="rounded-md border border-border px-2 py-1 text-xs">{example}</span>)}
            </div>
          </AccordionContent>
        </AccordionItem>
      </Accordion>
    </div>
  );
}
