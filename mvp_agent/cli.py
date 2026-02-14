import argparse
import csv
import json
import os

from .extractor import build_context_pack
from .evaluator import evaluate_with_agents, evaluate_with_llm, mock_evaluate
from .notebook_runner import execute_notebook, execute_notebook_docker
from .render import render_instructor_feedback, render_student_feedback
from .utils import ensure_dir, read_json, read_text, utc_timestamp
from .validator import validate_evaluation


def _write_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _write_text(path, text):
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def _write_csv(path, fieldnames, rows):
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def parse_args():
    ap = argparse.ArgumentParser(description="MVP Agente de Corrección (notebooks)")
    ap.add_argument("--notebook", required=True, help="Ruta al .ipynb")
    ap.add_argument("--rubric", required=True, help="Ruta al rubric.json")
    ap.add_argument("--assignment", help="Ruta al enunciado (txt)")
    ap.add_argument("--materials", help="Ruta a material del curso (txt)")
    ap.add_argument("--student-id", required=True, help="ID o email del estudiante")
    ap.add_argument("--output-dir", default="outputs", help="Directorio de salida")
    ap.add_argument("--gradebook-column", default="Final Score", help="Nombre de columna para Blackboard")
    ap.add_argument(
        "--llm-provider",
        default="mock",
        choices=["mock", "http", "agents"],
        help="Proveedor LLM",
    )
    ap.add_argument("--model", default=os.getenv("LLM_MODEL", ""), help="Modelo LLM")
    ap.add_argument(
        "--prompt",
        default="mvp_agent/prompts/evaluator_prompt.txt",
        help="Prompt de evaluación",
    )
    ap.add_argument("--temperature", type=float, default=0.2)
    ap.add_argument("--max-tokens", type=int, default=1200)
    ap.add_argument("--execute-notebook", action="store_true", help="Ejecutar notebook antes de evaluar")
    ap.add_argument(
        "--exec-mode",
        choices=["local", "docker"],
        default="local",
        help="Modo de ejecución del notebook",
    )
    ap.add_argument("--execution-timeout", type=int, default=120, help="Timeout de ejecución (seg)")
    ap.add_argument("--allow-exec-errors", action="store_true", help="Permitir errores de ejecución")
    ap.add_argument("--docker-image", default="mvp-notebook-exec:latest", help="Imagen Docker para ejecución")
    ap.add_argument("--docker-cpus", default="2", help="CPUs asignados al contenedor")
    ap.add_argument("--docker-memory", default="2g", help="Memoria asignada al contenedor")
    ap.add_argument("--docker-network", default="none", help="Red del contenedor")
    return ap.parse_args()


def main():
    args = parse_args()
    rubric = read_json(args.rubric)
    assignment_text = read_text(args.assignment)
    materials_text = read_text(args.materials)

    run_id = utc_timestamp()
    out_dir = os.path.join(args.output_dir, f"{args.student_id}_{run_id}")
    ensure_dir(out_dir)

    notebook_path = args.notebook
    execution_report = None
    if args.execute_notebook:
        executed_path = os.path.join(out_dir, "executed_notebook.ipynb")
        if args.exec_mode == "docker":
            execution_report = execute_notebook_docker(
                args.notebook,
                executed_path,
                timeout_sec=args.execution_timeout,
                image=args.docker_image,
                cpus=args.docker_cpus,
                memory=args.docker_memory,
                network=args.docker_network,
            )
        else:
            execution_report = execute_notebook(
                args.notebook,
                executed_path,
                timeout_sec=args.execution_timeout,
                allow_errors=args.allow_exec_errors,
            )
        notebook_path = executed_path
        _write_json(os.path.join(out_dir, "execution_report.json"), execution_report)

    context = build_context_pack(
        student_id=args.student_id,
        rubric=rubric,
        assignment_text=assignment_text,
        materials_text=materials_text,
        notebook_path=notebook_path,
        execution_report=execution_report,
    )

    if args.llm_provider == "mock":
        evaluation = mock_evaluate(context)
    elif args.llm_provider == "agents":
        if not args.model:
            raise ValueError(
                "Model is required for agents provider. Set --model or LLM_MODEL."
            )
        evaluation = evaluate_with_agents(
            context=context,
            prompt_path=args.prompt,
            model=args.model,
        )
    else:
        if not args.model:
            raise ValueError("Model is required for http provider. Set --model or LLM_MODEL.")
        evaluation = evaluate_with_llm(
            context=context,
            prompt_path=args.prompt,
            model=args.model,
            temperature=args.temperature,
            max_tokens=args.max_tokens,
        )

    validation = validate_evaluation(evaluation, context)
    evaluation = validation["evaluation"]

    _write_json(os.path.join(out_dir, "context_package.json"), context)
    _write_json(os.path.join(out_dir, "evaluation.json"), evaluation)
    _write_json(os.path.join(out_dir, "validation.json"), validation)

    student_feedback = render_student_feedback(evaluation)
    instructor_feedback = render_instructor_feedback(evaluation)
    _write_text(os.path.join(out_dir, "feedback_student.txt"), student_feedback)
    _write_text(os.path.join(out_dir, "feedback_instructor.txt"), instructor_feedback)

    _write_csv(
        os.path.join(out_dir, "gradebook_updates.csv"),
        fieldnames=["student_id", args.gradebook_column, "scale_min", "scale_max"],
        rows=[
            {
                "student_id": args.student_id,
                args.gradebook_column: f"{evaluation.get('final_score',0):.2f}",
                "scale_min": 0,
                "scale_max": 20,
            }
        ],
    )

    flags = evaluation.get("flags", [])
    if flags:
        _write_csv(
            os.path.join(out_dir, "flags.csv"),
            fieldnames=["student_id", "flag", "detail"],
            rows=[
                {
                    "student_id": args.student_id,
                    "flag": f.get("type", ""),
                    "detail": f.get("detail", ""),
                }
                for f in flags
            ],
        )

    print(f"OK: outputs in {out_dir}")


if __name__ == "__main__":
    main()
