import json
import os

from . import llm_client
from .agents_sdk_client import agents_complete
from .utils import extract_json_block, read_text


def _to_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _normalize_weights(criteria):
    weights = []
    for c in criteria:
        w = _to_float(c.get("weight"))
        weights.append(w)
    if all(w is None for w in weights):
        n = len(criteria)
        return [1.0 / n for _ in criteria]
    total = sum(w for w in weights if w is not None)
    if total <= 0:
        n = len(criteria)
        return [1.0 / n for _ in criteria]
    return [(w if w is not None else 0.0) / total for w in weights]


def _default_evidence(notebook_cells):
    for cell in notebook_cells:
        if cell["source"]:
            snippet = cell["source"][:200]
            return [{"cell_ref": cell["ref"], "quote": snippet}]
    return []


def mock_evaluate(context):
    rubric = context["rubric"]
    criteria = rubric.get("criteria", [])
    weights = _normalize_weights(criteria)
    notebook_cells = context["notebook"]["cells"]
    evidence = _default_evidence(notebook_cells)

    base_score = 12.0 if notebook_cells else 8.0
    eval_criteria = []
    for idx, c in enumerate(criteria):
        eval_criteria.append(
            {
                "name": c.get("name", f"Criterio {idx+1}"),
                "score": base_score,
                "weight": weights[idx],
                "rationale": "Evaluación preliminar basada en verificación automática básica.",
                "evidence": evidence,
                "common_errors": [],
                "improvement": "Agregar más justificación y resultados verificables.",
                "confidence": 0.3,
            }
        )

    return {
        "student_id": context["student_id"],
        "scale_min": 0,
        "scale_max": 20,
        "criteria": eval_criteria,
        "summary": {
            "good": "El trabajo muestra avances parciales.",
            "missing": "Faltan evidencias claras para varios criterios.",
            "priority": "Mejorar la explicación y justificación de resultados.",
        },
        "top_improvements": [
            "Agregar explicación de resultados clave.",
            "Incluir evidencia reproducible en celdas.",
            "Mejorar la claridad de la conclusión.",
        ],
        "guiding_questions": [
            "¿Cuál es la evidencia más fuerte que respalda tu conclusión?",
            "¿Qué parte del análisis es más difícil de reproducir y por qué?",
        ],
        "flags": [
            {"type": "needs_review", "detail": "Salida generada en modo mock."}
        ],
    }


def evaluate_with_llm(context, prompt_path, model, temperature=0.2, max_tokens=1200):
    system = (
        "Eres un evaluador académico. Devuelve SOLO JSON válido según el esquema."
    )
    prompt_template = read_text(prompt_path)
    if not prompt_template:
        raise ValueError("Prompt template is empty")

    prompt = prompt_template.format(
        student_id=context["student_id"],
        rubric_json=json.dumps(context["rubric"], ensure_ascii=False, indent=2),
        assignment=context["assignment"],
        materials=context["materials"],
        notebook_text=context["notebook"]["text"],
        execution_report=json.dumps(context.get("execution_report", {}), ensure_ascii=False, indent=2),
    )

    text = llm_client.http_complete(
        prompt=prompt,
        system=system,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return extract_json_block(text)


def evaluate_with_agents(context, prompt_path, model):
    system = (
        "Eres un evaluador académico. Devuelve SOLO JSON válido según el esquema."
    )
    prompt_template = read_text(prompt_path)
    if not prompt_template:
        raise ValueError("Prompt template is empty")

    prompt = prompt_template.format(
        student_id=context["student_id"],
        rubric_json=json.dumps(context["rubric"], ensure_ascii=False, indent=2),
        assignment=context["assignment"],
        materials=context["materials"],
        notebook_text=context["notebook"]["text"],
        execution_report=json.dumps(context.get("execution_report", {}), ensure_ascii=False, indent=2),
    )

    text = agents_complete(prompt=prompt, system=system, model=model)
    return extract_json_block(text)
