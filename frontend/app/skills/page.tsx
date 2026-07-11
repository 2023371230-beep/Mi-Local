"use client";

import { Bot, BrainCircuit, Code2, Database, Globe2, Palette, Shield } from "lucide-react";
import { useState } from "react";
import { SkillCard, type SkillInfo } from "@/components/skills/skill-card";
import { SkillPlayground } from "@/components/skills/skill-playground";
import { SectionHeader } from "@/components/ui/section-header";
import { pageShell } from "@/lib/config/design-tokens";

const skills: SkillInfo[] = [
  { title: "Programacion", mode: "programacion", model: "qwen2.5-coder:7b", icon: Code2, description: "Codigo, debugging, APIs, refactor y arquitectura.", when: "Cuando la pregunta incluye codigo, errores, endpoints, scripts o diseno tecnico.", rag: "Opcional, util si hay docs del proyecto.", limitations: "No ejecuta codigo por si solo desde esta pantalla.", examples: ["Corrige este endpoint FastAPI", "Genera un script Python seguro"] },
  { title: "UI/UX", mode: "ui_ux", model: "qwen2.5-coder:7b", icon: Palette, description: "Interfaz, accesibilidad, contraste y componentes.", when: "Para layouts, jerarquia visual, accesibilidad y microcopy.", rag: "Recomendado con coleccion ui_ux.", limitations: "No ve screenshots salvo que se integren al flujo.", examples: ["Evalua contraste y jerarquia visual", "Propone layout responsive"] },
  { title: "Ciberseguridad", mode: "ciberseguridad", model: "qwen2.5:7b", icon: Shield, description: "Analisis defensivo, OWASP, hardening y logs.", when: "Para analisis defensivo, checklist y explicaciones de riesgos.", rag: "Util si consultas normas o guias locales.", limitations: "No debe usarse para abuso ofensivo.", examples: ["Analiza este log defensivamente", "Checklist OWASP para mi app"] },
  { title: "Bases de datos", mode: "bases_datos", model: "qwen2.5-coder:7b", icon: Database, description: "SQL, indices, normalizacion y seguridad.", when: "Para queries, esquemas, indices y diseno relacional.", rag: "Opcional si hay docs de DB.", limitations: "No se conecta a bases reales desde UI.", examples: ["Optimiza esta query PostgreSQL", "Disena un esquema normalizado"] },
  { title: "RAG local", mode: "rag", model: "qwen2.5:7b", icon: BrainCircuit, description: "Consulta documentos locales con fuentes.", when: "Cuando la respuesta debe salir de tus PDFs.", rag: "Siempre recomendado.", limitations: "Depende de documentos ingeridos.", examples: ["Segun mis documentos, resume WCAG", "Busca en mis PDFs sobre UX research"] },
  { title: "Web search", mode: "web", model: "qwen2.5:7b", icon: Globe2, description: "Busqueda web con Vane/SearXNG y URLs.", when: "Para informacion externa o reciente.", rag: "No necesario.", limitations: "Vane puede estar degradado; SearXNG actua como fallback.", examples: ["Busca en web OWASP Top 10", "Noticias actuales de React"] },
  { title: "Chat general", mode: "general", model: "qwen2.5:7b", icon: Bot, description: "Conversacion tecnica sin RAG por defecto.", when: "Para teoria, redes, explicaciones y lluvia de ideas.", rag: "Auto si la pregunta lo amerita.", limitations: "No cita docs si RAG esta apagado.", examples: ["Explica BGP con ejemplos", "Resume una idea tecnica"] },
];

export default function SkillsPage() {
  const [selectedMode, setSelectedMode] = useState(skills[0].mode);
  const selectedSkill = skills.find((skill) => skill.mode === selectedMode) ?? skills[0];

  return (
    <div className={pageShell}>
      <SectionHeader eyebrow="Skills" title="Capacidades especializadas" description="Elige un modo, revisa detalles solo si hacen falta y prueba desde un playground unico." />
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {skills.map((skill) => <SkillCard key={skill.mode} skill={skill} selected={skill.mode === selectedMode} onSelect={() => setSelectedMode(skill.mode)} />)}
      </div>
      <SkillPlayground skill={selectedSkill} />
    </div>
  );
}
