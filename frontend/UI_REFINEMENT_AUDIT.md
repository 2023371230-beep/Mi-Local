# UI Refinement Audit

Fecha: 2026-07-08
Fase: 0 - Auditoria visual y tecnica

## Resultado base

Validaciones iniciales ejecutadas:

```text
npm run lint
npm run build
```

Resultado:

```text
lint: ok
build: ok
```

Rutas actuales mantenidas:

- `/`
- `/chat`
- `/skills`
- `/rag`
- `/documents`
- `/models`
- `/logs`
- `/agent`
- `/settings`

## Diagnostico general

La UI actual esta funcional y bien separada para una primera version, pero visualmente todavia se percibe como MVP tecnico. La mayor oportunidad no es cambiar arquitectura ni endpoints, sino crear una capa de presentacion mas consistente: tokens, componentes base, estados, disclosure progresivo y layouts con jerarquia.

Hay buena base para refinar:

- App Router ya esta organizado por rutas.
- Componentes por dominio ya existen: layout, chat, rag, skills, models, logs, agent.
- TanStack Query y Zustand ya estan integrados.
- shadcn/ui ya esta instalado.
- Dark mode esta como default.
- El panel derecho ya existe y usa sources del chat store.

La refinacion debe preservar esta estructura y trabajar por componentes.

## Problemas visuales detectados

- El dashboard funciona como launcher basico, pero no como vista operativa. Tiene pocos indicadores utiles y acciones limitadas.
- Las paginas interiores usan titulos muy simples y no comparten un patron de header, descripcion, acciones y metadata.
- Las cards tienen estilo correcto pero generico; casi todas son `rounded-lg border bg-card/50` sin jerarquia visual.
- Hay demasiados bordes con el mismo peso. Esto hace que la interfaz se vea plana.
- El sidebar es una lista plana. No hay agrupacion por intencion ni secciones desplegables.
- La topbar muestra estados binarios `ok/off`; no representa bien estados degradados como Vane timeout con fallback SearXNG.
- El panel derecho ocupa ancho fijo aunque no haya contexto util.
- Chat muestra controles tecnicos siempre visibles; esto aumenta ruido antes de escribir.
- Skills muestra un playground por cada skill; esto escala mal y ensucia la pantalla.
- RAG y Documents son funcionales, pero no guian el flujo del usuario.
- Logs se ven como dump de texto sin severidad, agrupacion ni diagnostico.
- Agent placeholder comunica la idea, pero aun parece maqueta minima.
- Settings agrupa todo en una sola card y mezcla backend, chat, apariencia y opciones avanzadas.

## Componentes repetidos

Patrones repetidos que conviene unificar:

- Headers de pagina: titulo + descripcion + acciones.
- Cards de estado: icono + titulo + descripcion + badge + accion.
- Estados vacios: RAG sin resultados, chat inicial, sources vacias, models/logs cargando.
- Badges de estado: ok, warning, error, degraded, idle.
- Inputs con label: settings, chat options, ingest, RAG query.
- Contenedores `rounded-lg border border-border bg-card/50 p-3`.
- Bloques de metadata: skill, model, rag/web, latency.
- Panels tecnicos con fuente mono: logs, terminal preview, paths, modelos.

## Componentes que conviene unificar

Crear o refactorizar sin cambiar arquitectura:

- `lib/config/design-tokens.ts`
- `components/ui/status-badge.tsx`
- `components/ui/section-header.tsx`
- `components/ui/empty-state.tsx`
- `components/ui/metric-card.tsx`
- `components/ui/action-card.tsx`
- `components/ui/command-card.tsx`
- `components/ui/context-drawer.tsx`
- `components/ui/app-tooltip.tsx`
- `components/layout/sidebar-section.tsx`
- `components/layout/sidebar-item.tsx`
- `components/layout/context-panel-toggle.tsx`

Estos componentes deben ser presentacionales y consumir los stores/API existentes.

## Problemas de jerarquia

- El dashboard no diferencia claramente acciones principales, estado del sistema y actividad reciente.
- En `/chat`, el input y las opciones tecnicas compiten con el historial.
- En `/skills`, cada skill tiene la misma prioridad visual y cada playground tiene el mismo peso.
- En `/models`, el dump tecnico del modelo no esta traducido a roles utiles.
- En `/logs`, todos los eventos se ven igual.
- En `/settings`, todas las preferencias tienen la misma importancia.

Prioridad visual recomendada:

1. Accion principal de la pantalla.
2. Estado o feedback inmediato.
3. Opciones frecuentes.
4. Opciones avanzadas ocultas.
5. Metadata tecnica secundaria.

## Problemas de espaciado

- Muchas pantallas usan `space-y-4` y cards con `p-3`; esto es consistente pero poco expresivo.
- No hay ritmo claro entre header, contenido primario y contenido secundario.
- El panel derecho fijo de `w-80` reduce espacio en laptops.
- Chat usa altura calculada `h-[calc(100vh-20rem)]`, que puede sentirse apretada en pantallas pequenas.
- Skills con multiples playgrounds duplica mucho espacio vertical.

Recomendacion:

- Mantener densidad de dashboard profesional, no landing page.
- Usar headers compactos.
- Reservar `p-4`/`p-5` para cards primarias y `p-3` para elementos secundarios.
- Usar `gap-4` en layouts principales y `gap-2` para metadata.

## Problemas de tipografia

- Geist esta bien como sans moderna, pero no hay escala tipografica propia.
- Titulos de pagina usan `text-lg`, a veces demasiado pequeno para orientacion.
- Metadata tecnica y badges no tienen patron unificado.
- Logs, paths y modelos usan mono, correcto, pero falta diferenciar severidad y legibilidad.

Recomendacion:

- Definir escala: page title, section title, body, caption, metadata.
- Mantener mono solo para logs, rutas, modelos, codigo y timestamps.
- Evitar textos largos dentro de badges.

## Problemas responsive

- Sidebar desaparece en mobile y no hay alternativa visible tipo Sheet.
- Panel derecho solo existe en `lg:block`; no hay acceso en mobile.
- El dashboard usa grid de cuatro columnas en `md`, puede quedar compacto en laptops pequenas.
- Chat input muestra cuatro controles tecnicos en grid antes del textarea.
- Skills con muchos playgrounds sera pesado en mobile.
- Logs usan altura fija relativa y pueden comerse la pantalla sin controles pegajosos.

Recomendacion:

- Sidebar mobile como Sheet.
- Panel derecho como Sheet en mobile.
- Ocultar opciones avanzadas en accordion.
- Cards a una columna en mobile, dos en laptop, tres maximo en desktop grande.

## Riesgos de romper funcionalidad

- `apiFetch` usa `appConfig.backendUrl`, no el valor persistido de `ui.backendUrl`. Cambiar settings runtime podria requerir ajuste cuidadoso; no tocar en refinamiento visual salvo fase Settings.
- `RightContextPanel` depende de `useChatStore.sources`; si se reemplaza, conservar `setSources`.
- Chat export usa mensajes en memoria; conservar `messages`.
- RAG query tambien actualiza sources globales; mantener este comportamiento para el panel derecho.
- `/web/search` devuelve `engine` y `error`; la UI debe interpretar fallback sin cambiar contrato.
- shadcn/ui `Button` actual no soporta `asChild`; evitar asumir API no existente.
- Next 16/Turbopack puede ser estricto con props no soportadas y tipos.
- No implementar modo agente real en esta fase; solo mejorar placeholder.

## Plan de refinamiento

### Fase 1 - Design system interno

Crear tokens y primitives visuales reutilizables:

- Status badge con estados `ok`, `warning`, `error`, `degraded`, `idle`.
- Section header compacto.
- Empty state reutilizable.
- Metric/action/command cards.
- Clases globales para surfaces, focus visible, fondos por capas y estados.

Criterio de salida:

- `npm run lint` ok.
- `npm run build` ok.
- UI carga sin cambios de endpoints.

### Fase 2 - Sidebar premium

Agrupar navegacion:

- Inicio: Dashboard
- IA: Chat, Skills, Agent
- Conocimiento: RAG, Documents
- Sistema: Models, Logs, Settings

Agregar collapsible sections, active state sutil, collapse desktop y alternativa mobile.

### Fase 3 - Topbar y estados reales

Refinar health:

- backend
- ollama
- chroma
- web engine
- Vane degraded si hay fallback/timeouts conocidos

Agregar refresh, last updated y menu compacto de detalles.

### Fase 4 - Panel derecho inteligente

No ocupar ancho si no hay contexto:

- Collapsible en desktop.
- Sheet en mobile.
- Empty state compacto.
- Mantener setting `rightPanel`.

### Fase 5 - Dashboard profesional

Convertir el dashboard en vista operativa:

- Acciones principales.
- Cards de Chat, RAG, Web, Agent.
- Estado del sistema.
- Actividad reciente.
- Colecciones.

### Fase 6 - Chat refinado

Reducir ruido:

- Empty state con ejemplos.
- Opciones avanzadas en accordion.
- Metadata integrada al mensaje asistente.
- Fuentes en panel derecho.
- Loading y toasts.

### Fase 7 - Skills limpio

Un solo playground global:

- Cards expandibles.
- Boton Probar que selecciona skill.
- Detalles en accordion.

### Fase 8 - RAG/Documents guiado

Hacerlos flujos:

- Colecciones visibles.
- Opciones avanzadas escondidas.
- Resultados con metadata clara.
- Ingesta rapida con resumen y avisos.

### Fase 9 - Models

Traducir modelos a roles:

- general
- coder
- embedding
- auxiliar/router

Mostrar tamano humano y recomendaciones.

### Fase 10 - Logs

Pasar de dump a diagnostico:

- Filtros por severidad y dominio.
- Agrupacion de timeouts.
- Cards de problemas detectados.
- Copiar logs.

### Fase 11 - Agent placeholder premium

Mejorar percepcion sin acciones reales:

- Permisos simulados.
- Timeline.
- Diff y terminal mas legibles.
- Aviso claro de no ejecucion real.

### Fase 12 - Settings

Agrupar preferencias:

- Backend
- Chat
- Apariencia
- Web search
- Avanzado

Mantener persistencia Zustand.

### Fase 13 - Microinteracciones

Agregar:

- Skeletons.
- Estados disabled/loading.
- Tooltips.
- Hover/focus sutil.
- Toasts.

### Fase 14 - Accesibilidad y responsive

Validar:

- Focus visible.
- Labels.
- Aria labels en icon buttons.
- Contraste.
- Mobile para sidebar y panel derecho.

### Fase 15 - Vane/Web search UX

Reflejar realidad:

- Si `engine=searxng` y hay error de Vane, mostrar fallback.
- Topbar: web fallback / vane degraded.
- Logs: agrupar timeouts.
- Settings: recomendacion temporal.

### Fase 16 - QA completa

Ejecutar:

- `npm run lint`
- `npm run build`
- Validacion manual de rutas.
- Flujos: chat, skills, RAG, ingest, web fallback, models, logs, settings, sidebar, panel derecho, responsive.

Crear:

- `FINAL_UI_REFINEMENT_REPORT.md`

## Recomendacion de alcance inmediato

La siguiente fase debe ser Fase 1. No conviene empezar por dashboard o chat sin design tokens, porque aumentaria duplicacion. Primero crear primitives pequenas y luego aplicarlas por ruta.

## Estado de Fase 0

Fase 0 completada cuando:

- `npm run lint` pasa.
- `npm run build` pasa.
- Este archivo existe.

Estado actual:

```text
Fase 0: completada
```
