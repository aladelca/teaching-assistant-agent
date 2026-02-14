def _to_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _normalize_weights(weights):
    if not weights:
        return []
    if all(w is None for w in weights):
        n = len(weights)
        return [1.0 / n for _ in weights]
    total = sum(w for w in weights if w is not None)
    if total <= 0:
        n = len(weights)
        return [1.0 / n for _ in weights]
    return [(w if w is not None else 0.0) / total for w in weights]


def _find_text_evidence(quote, notebook_text):
    if not quote:
        return False
    return quote in notebook_text


def _extract_rubric_weights(context):
    rubric = context.get("rubric", {})
    crit = rubric.get("criteria", [])
    weights = []
    for c in crit:
        weights.append(_to_float(c.get("weight")))
    return weights


def validate_evaluation(evaluation, context):
    issues = []
    notebook_text = context["notebook"]["text"]

    criteria = evaluation.get("criteria", [])
    if not criteria:
        issues.append("No criteria in evaluation output.")

    rubric_weights_raw = _extract_rubric_weights(context)
    rubric_weights = _normalize_weights(rubric_weights_raw) if rubric_weights_raw else []
    llm_weights_raw = [_to_float(c.get("weight")) for c in criteria]
    llm_weights = _normalize_weights(llm_weights_raw) if criteria else []
    use_weights = rubric_weights if rubric_weights else llm_weights

    if rubric_weights and llm_weights:
        if len(rubric_weights) == len(llm_weights):
            diffs = [
                abs(rubric_weights[i] - llm_weights[i])
                for i in range(len(rubric_weights))
            ]
            if any(d > 0.05 for d in diffs):
                issues.append("LLM weights differ from rubric weights. Overriding with rubric.")
        else:
            issues.append("LLM criteria count differs from rubric. Using LLM weights.")
            use_weights = llm_weights

    total_score = 0.0

    for idx, crit in enumerate(criteria):
        score = _to_float(crit.get("score"))
        if score is None:
            issues.append(f"Missing score for criterion {crit.get('name', idx)}.")
            score = 0.0
        if score < 0 or score > 20:
            issues.append(f"Score out of range for {crit.get('name', idx)}.")
            score = max(0.0, min(20.0, score))
        crit["score"] = score

        if use_weights:
            crit["weight"] = use_weights[idx] if idx < len(use_weights) else 0.0
        else:
            crit["weight"] = _to_float(crit.get("weight")) or 0.0

        total_score += crit["score"] * (crit["weight"] or 0.0)

        evidence = crit.get("evidence", [])
        if not evidence:
            issues.append(f"No evidence for {crit.get('name', idx)}.")
        for ev in evidence:
            quote = ev.get("quote", "")
            if quote and not _find_text_evidence(quote, notebook_text):
                issues.append(
                    f"Evidence quote not found in notebook for {crit.get('name', idx)}."
                )
            if quote and len(quote.split()) > 25:
                issues.append(
                    f"Evidence quote too long for {crit.get('name', idx)}."
                )

    evaluation["final_score"] = round(total_score, 2)
    evaluation["scale_min"] = 0
    evaluation["scale_max"] = 20

    summary = evaluation.get("summary", {})
    if not summary or any(k not in summary for k in ("good", "missing", "priority")):
        issues.append("Summary incomplete.")

    top_improvements = evaluation.get("top_improvements", [])
    if len(top_improvements) == 0:
        issues.append("No top improvements provided.")

    guiding_questions = evaluation.get("guiding_questions", [])
    if len(guiding_questions) < 2:
        issues.append("Insufficient guiding questions.")

    flags = evaluation.get("flags", [])
    if issues:
        flags.append({"type": "validator_issue", "detail": "; ".join(issues)})
        evaluation["flags"] = flags

    return {"issues": issues, "evaluation": evaluation}
