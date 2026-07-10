# Frontend Design Brief - Asistente IA Local

## Fuentes RAG usadas

- `native_mobile_design_guide.pdf`, paginas 1, 2, 4, 5, 7 y 8.
- `Innov_Team_Design-Thinking-Framework.pdf`, pagina 1.
- `WCAG2-at-a-Glance.pdf`.
- `Best Practices Content Guide For Clients.pdf`.
- `User_Research_Methods_A4-compressed.pdf`.

## Principios de diseno

1. Priorizar claridad operativa: la interfaz debe explicar estado, modo, skill, modelo y fuentes sin esconder informacion critica.
2. Usar patrones familiares de herramientas tecnicas: sidebar, topbar de estado, panel principal, panel contextual derecho y vista tipo terminal para logs.
3. Mantener consistencia visual: mismos estados, mismos badges, mismas acciones y controles equivalentes en Chat, Skills, RAG y Logs.
4. Aplicar enfoque de design thinking: empezar por flujos reales de trabajo, no por decoracion. El usuario debe poder preguntar, consultar RAG, revisar fuentes y cambiar modo con poca friccion.
5. Disenar para confianza: toda respuesta con RAG o web debe mostrar origen, filename/url, pagina/chunk y metadata.
6. Reducir carga cognitiva: controles avanzados visibles pero compactos, agrupados por contexto.
7. Preparar extensibilidad: el modo agente debe verse listo para file explorer, diff, aprobaciones y terminal, aunque todavia no ejecute acciones reales.

## Layout recomendado

- Sidebar izquierda fija para navegacion: Dashboard, Chat, Skills, RAG, Documents, Models, Logs, Agent, Settings.
- Topbar persistente con estado de backend, Ollama, Chroma y Vane/SearXNG.
- Panel central como area de trabajo principal.
- Panel derecho redimensionable para fuentes, contexto, metadata y estado de ejecucion.
- En pantallas pequenas, el panel derecho debe colapsar a sheet/dialog.
- Chat no debe ocupar toda la identidad de la app; debe ser una herramienta dentro de un centro de comando.

## Color

- Dark mode por defecto.
- Fondo base oscuro no negro: grafito/azul muy oscuro.
- Superficies con borde sutil y contraste suficiente.
- Acentos tecnicos moderados: cyan para estado activo, verde para saludable, amber para advertencia, rojo para error, violeta solo como acento secundario.
- Evitar un tema monotono completamente azul o morado; usar acentos por estado y funcion.

## Tipografia

- Fuente sans legible para UI, con tamanos compactos tipo herramienta profesional.
- Fuente mono para logs, snippets, metadata, rutas y nombres de modelo.
- Jerarquia clara: titulos pequenos y funcionales, no hero text.
- No usar texto gigante en cards o paneles densos.

## Accesibilidad

- Contraste alto en texto, botones y badges.
- Focus states visibles en inputs, botones, tabs y navegacion.
- No depender solo del color para comunicar estado; acompanar con texto/icono.
- Areas clicables suficientemente grandes.
- Evitar paneles saturados, animaciones excesivas o informacion importante solo en hover.

## Componentes clave

- `AppShell`: sidebar + topbar + main + right context panel.
- `StatusPill`: backend, Ollama, Chroma, Vane.
- `ChatView`: modo, RAG, coleccion, top_k, historial, fuentes.
- `SourcesPanel`: filename/page/chunk/url con badges por origen.
- `SkillCard` y `SkillPlayground`: probar skills sin cambiar de pagina.
- `CollectionsView`, `RagQueryPanel`, `IngestPanel`.
- `ModelsGrid`: modelos Ollama con capacidades.
- `LogsView`: terminal visual con filtros.
- `AgentPlaceholder`: file explorer mock, diff preview, approval cards y terminal preview.
- `Settings`: preferencias locales persistentes.

## Patrones visuales

- Cards solo para elementos repetidos o paneles reales, no para envolver toda la pagina.
- Bordes sutiles y fondos por capas para separar areas.
- Densidad media: mas parecido a IDE que a landing page.
- Iconos lucide en navegacion y acciones.
- Badges compactos para modelo, skill, RAG, web y latencia.
- Panel derecho como "contexto vivo" que cambia segun vista.

## Como diferenciarlo de un chat generico

- Mostrar siempre modo operativo, modelo y skill.
- Hacer visibles RAG/web/fuentes como parte central de la experiencia.
- Dar rutas directas a Skills, RAG, Models y Logs.
- Incluir vista de agente preparada con estructura de trabajo real.
- Usar layout persistente tipo IDE, no pantalla unica de mensajes.

## Que no hacer

- No crear una landing page.
- No usar hero grande, frases de marketing ni tarjetas decorativas gigantes.
- No ocultar fuentes o metadata.
- No sobrecargar con gradientes pesados o paleta de un solo color.
- No usar UI brillante tipo demo; debe sentirse como herramienta diaria.
- No hacer que el modo agente parezca funcional si todavia no ejecuta acciones.
- No depender de endpoints inexistentes.
