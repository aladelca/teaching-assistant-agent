from mvp_agent.validator import validate_evaluation


def _context():
    return {
        "rubric": {
            "criteria": [
                {"name": "A", "weight": 0.5},
                {"name": "B", "weight": 0.5},
            ]
        },
        "notebook": {
            "text": "Fragmento de prueba en notebook.",
        },
    }


def test_validator_overrides_weights_and_scores():
    evaluation = {
        "criteria": [
            {
                "name": "A",
                "score": 18,
                "weight": 0.8,
                "evidence": [{"cell_ref": "C001", "quote": "Fragmento"}],
            },
            {
                "name": "B",
                "score": 10,
                "weight": 0.2,
                "evidence": [{"cell_ref": "C002", "quote": "notebook"}],
            },
        ],
        "summary": {"good": "g", "missing": "m", "priority": "p"},
        "top_improvements": ["x"],
        "guiding_questions": ["q1", "q2"],
        "flags": [],
    }
    result = validate_evaluation(evaluation, _context())
    eval_out = result["evaluation"]
    assert round(eval_out["final_score"], 2) == 14.0
    assert eval_out["criteria"][0]["weight"] == 0.5
    assert eval_out["criteria"][1]["weight"] == 0.5


def test_validator_flags_long_quote():
    long_quote = (
        "uno dos tres cuatro cinco seis siete ocho nueve diez once doce trece catorce quince "
        "dieciseis diecisiete dieciocho diecinueve veinte veintiuno veintidos veintitres "
        "veinticuatro veinticinco veintiseis"
    )
    evaluation = {
        "criteria": [
            {
                "name": "A",
                "score": 12,
                "weight": 0.5,
                "evidence": [
                    {
                        "cell_ref": "C001",
                        "quote": long_quote,
                    }
                ],
            }
        ],
        "summary": {"good": "g", "missing": "m", "priority": "p"},
        "top_improvements": ["x"],
        "guiding_questions": ["q1", "q2"],
        "flags": [],
    }
    result = validate_evaluation(evaluation, _context())
    assert "Evidence quote too long" in "; ".join(result["issues"])
