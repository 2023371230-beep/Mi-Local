# FINAL_UI_REPORT

Estado: 🟢 lint + build + 20 Playwright en verde. Modo simple/pro + Motion.

## Modos de UI
- **Simple** (uso diario, tipo Ollama): chat centrado (max-w-3xl), sidebar con 3 rutas
  (Chat, Documents, Settings), composer tipo pill. Mobile arranca aquí.
- **Pro** (centro de comando): 9 rutas, dashboard, panel contextual, diagnósticos.
- Toggle persistente en el footer del sidebar (zustand persist). Modo simple redirige rutas pro
  a /chat. Verificado: pro=9 links, simple=3 links.

## Composer de chat (estilo Ollama, sin assets propietarios)
Pill redondeada, textarea limpia, menú `+` (modelo/RAG/colección/top-k/atajos), globo web,
selector de skill, botón enviar redondo. **Streaming token a token** con cursor.
Crash del menú `+` (DropdownMenuLabel sin Group) corregido + test de regresión interactivo.

## Motion (moderado)
- Fade+slide en mensajes nuevos (0.25s, solo los 2 últimos para no re-animar el historial).
- Fade+slide del empty state.
- Sin animaciones pesadas, sin gradientes, sin landing.

## Generador de documentos (/documents)
Tabs Generar/Ingestar. Formulario con tipo/formato/RAG, preview Markdown, descarga, historial.

## Accesibilidad
aria-labels en botones del composer, aria-live en el bloque de streaming, aria-pressed en el
globo. Focus visible (focus-ring). Responsive validado en mobile (Playwright Pixel 7).

## Estado (persistencia)
- chat-history: últimos 100 mensajes + fuentes (sobrevive F5).
- ui: modo simple/pro, tema, defaults de chat.

## Pendiente (refinamiento fino, opcional)
- Skeletons en dashboard/models/logs durante carga (hoy LoadingState genérico).
- File explorer real en /agent (hoy lista el árbol como texto).
- Tooltips en los badges de estado del sidebar.
