def _format_rubric_table(criteria):
    lines = []
    lines.append("Criterio | Puntaje (0-20) | Peso")
    lines.append("--- | --- | ---")
    for c in criteria:
        name = c.get("name", "")
        score = c.get("score", 0)
        weight = c.get("weight", 0)
        lines.append(f"{name} | {score:.2f} | {weight:.2f}")
    return "\n".join(lines)


def render_student_feedback(evaluation):
    summary = evaluation.get("summary", {})
    criteria = evaluation.get("criteria", [])
    top_improvements = evaluation.get("top_improvements", [])
    guiding_questions = evaluation.get("guiding_questions", [])

    lines = []
    lines.append("Resumen (3 líneas)")
    lines.append(f"Qué está bien: {summary.get('good','')}")
    lines.append(f"Qué falta: {summary.get('missing','')}")
    lines.append(f"Prioridad #1: {summary.get('priority','')}")
    lines.append("")
    lines.append("Mini-rúbrica")
    lines.append(_format_rubric_table(criteria))
    lines.append("")
    lines.append("Top 5 mejoras")
    for item in top_improvements[:5]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("Preguntas guía")
    for q in guiding_questions[:3]:
        lines.append(f"- {q}")
    lines.append("")
    lines.append(f"Nota final: {evaluation.get('final_score', 0):.2f}/20")
    return "\n".join(lines).strip()


def render_instructor_feedback(evaluation):
    criteria = evaluation.get("criteria", [])
    lines = []
    lines.append("Resumen para docente")
    lines.append(f"Nota final: {evaluation.get('final_score', 0):.2f}/20")
    lines.append("")
    lines.append("Detalle por criterio")
    for c in criteria:
        lines.append(f"- {c.get('name','')}: {c.get('score',0):.2f}/20 (peso {c.get('weight',0):.2f})")
        lines.append(f"  Evidencia: {c.get('evidence', [])}")
        lines.append(f"  Rationale: {c.get('rationale','')}")
        lines.append(f"  Mejora: {c.get('improvement','')}")
    flags = evaluation.get("flags", [])
    if flags:
        lines.append("")
        lines.append("Alertas")
        for f in flags:
            lines.append(f"- {f.get('type')}: {f.get('detail')}")
    return "\n".join(lines).strip()

