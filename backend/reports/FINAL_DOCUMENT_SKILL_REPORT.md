# FINAL_DOCUMENT_SKILL_REPORT

Estado: 🟢 funcional. 7 tests. Verificado en vivo (checklist PDF generado y descargado).

## Qué genera
9 tipos: reporte_tecnico, manual_usuario, manual_tecnico, documentacion_api, readme,
reporte_practica, requerimientos, politica, checklist. Cada uno con su plantilla de estructura.

4 formatos: **md, html, docx, pdf**.

## Cómo funciona
`DocumentService.generate` → LLM (qwen2.5:7b, temp 0.3, ctx 8192) redacta Markdown siguiendo la
plantilla del tipo → generador por formato → `outputs/<slug>-<timestamp>.<fmt>`.

- **HTML**: markdown → HTML con CSS embebido (light/dark, tablas, código).
- **DOCX**: parser de bloques → python-docx (headings, listas, código en Consolas).
- **PDF**: parser de bloques → reportlab (Title/Heading/BodyText/listas/Preformatted).
- **MD**: directo.

Parser común `md_blocks.py`: headings, párrafos, listas (bullet/numbered), bloques de código.

## RAG opcional
Si `use_rag=true` + colección: hace query, filtra por umbral, inyecta contexto y lo cita.

## Endpoints
- `POST /documents/generate` → markdown + metadata + archivo.
- `GET /documents/outputs` → historial + tipos + formatos disponibles.
- `GET /documents/download/{filename}` → descarga (sin traversal; media type correcto).

## Frontend (/documents, tab "Generar")
Formulario (tipo, formato, título, indicaciones, toggle RAG + colección) → preview Markdown →
descarga → historial. Tab "Ingestar al RAG" conserva el panel de ingesta anterior.

## Seguridad
`resolve_output` impide traversal (el archivo debe resolver dentro de outputs/). Test incluido.

## Pendiente opcional
- PPTX (requiere python-pptx; el pedido lo marca como "si no complica").
- Plantillas con logo/portada para reportes de práctica formales.
