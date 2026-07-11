"""Evaluacion de calidad RAG con dataset fijo de 20 preguntas.

Uso:
    cd backend
    .\\.venv\\Scripts\\python.exe .\\scripts\\eval_rag.py            # solo retrieval (rapido)
    .\\.venv\\Scripts\\python.exe .\\scripts\\eval_rag.py --answers  # tambien genera respuestas (lento)

Mide por pregunta: si la fuente esperada aparece en el top-3 y la distancia del top-1.
Las preguntas 16-20 son trampa (temas NO ingestados): el sistema debe decir que no hay
contexto relevante; si "responde", el umbral rag_max_distance esta muy alto.
"""

from __future__ import annotations

import sys
import time

import httpx

BASE = "http://127.0.0.1:8000"

# (pregunta, coleccion, fragmento esperado en filename del top-3; None = trampa)
DATASET: list[tuple[str, str, str | None]] = [
    ("Que recetas de uso tengo para programacion?", "asistente", "recetas_de_uso"),
    ("Como debo pedirle debugging al asistente?", "asistente", "guia_del_asistente"),
    ("Que reglas de prompting para LLMs locales tengo?", "programacion", "prompting_llms_locales"),
    ("Que buenas practicas de desarrollo defini?", "programacion", "buenas_practicas"),
    ("Como estructurar un endpoint FastAPI segun mis guias?", "programacion", "buenas_practicas"),
    ("Que dice mi guia sobre indices en PostgreSQL?", "bases_datos", "postgresql_guia"),
    ("Como hago EXPLAIN ANALYZE segun mis documentos?", "bases_datos", "postgresql_guia"),
    ("Que fundamentos defensivos tengo documentados?", "ciberseguridad", "fundamentos_defensivos"),
    ("Que dice mi material sobre logging defensivo?", "ciberseguridad", "fundamentos_defensivos"),
    ("Que principios de contraste de color tengo?", "ui_ux", "principios_ui_ux"),
    ("Que dice WCAG2 at a Glance sobre alternativas de texto?", "ui_ux", "WCAG2"),
    ("Que metodos de investigacion de usuarios lista mi PDF?", "ui_ux", "User_Research"),
    ("Que fases tiene el design thinking segun mi material?", "ui_ux", "Design-Thinking"),
    ("Que guia de diseno movil nativo tengo?", "ui_ux", "native_mobile"),
    ("Que cubren las best practices de contenido para clientes?", "ui_ux", "Best Practices"),
    # Trampas: temas no ingestados. Esperado: sin fuentes / "no relevante".
    ("Como configuro un cluster de Kubernetes?", "programacion", None),
    ("Que es ownership en Rust?", "programacion", None),
    ("Como monto un API Gateway en AWS?", "bases_datos", None),
    ("Como funcionan las particiones en Kafka?", "ciberseguridad", None),
    ("Que mutaciones soporta GraphQL?", "ui_ux", None),
]


def main() -> int:
    generate_answers = "--answers" in sys.argv
    hits = 0
    trap_ok = 0
    total_real = sum(1 for _, _, expected in DATASET if expected)
    total_traps = len(DATASET) - total_real

    print(f"{'#':>2} {'ok':^4} {'dist':>5}  pregunta -> top1")
    for index, (question, collection, expected) in enumerate(DATASET, start=1):
        endpoint = "/rag/query" if generate_answers else "/rag/query"
        started = time.perf_counter()
        try:
            response = httpx.post(
                f"{BASE}{endpoint}",
                json={"message": question, "collection": collection, "top_k": 3},
                timeout=300.0,
            )
            response.raise_for_status()
            data = response.json()
        except httpx.HTTPError as exc:
            print(f"{index:>2} ERR  {exc}")
            continue
        elapsed = time.perf_counter() - started
        sources = data.get("sources") or []
        top = sources[0] if sources else {}
        top_name = top.get("filename") or "-"
        top_dist = top.get("score")
        dist_text = f"{top_dist:.2f}" if isinstance(top_dist, (int, float)) else "  - "

        if expected is None:
            ok = not sources
            trap_ok += 1 if ok else 0
            mark = "PASS" if ok else "FAIL"
            print(f"{index:>2} {mark:^4} {dist_text:>5}  [trampa] {question[:48]} -> {top_name} ({elapsed:.0f}s)")
        else:
            ok = any(expected.lower() in (s.get("filename") or "").lower() for s in sources[:3])
            hits += 1 if ok else 0
            mark = "PASS" if ok else "FAIL"
            print(f"{index:>2} {mark:^4} {dist_text:>5}  {question[:48]} -> {top_name} ({elapsed:.0f}s)")

    print()
    print(f"Retrieval: {hits}/{total_real} preguntas reales con fuente esperada en top-3")
    print(f"Trampas:   {trap_ok}/{total_traps} correctamente rechazadas (sin fuentes)")
    print("Si las trampas fallan: bajar rag_max_distance. Si las reales fallan: subirlo o revisar ingesta.")
    return 0 if (hits >= total_real * 0.7 and trap_ok >= total_traps * 0.8) else 1


if __name__ == "__main__":
    raise SystemExit(main())
