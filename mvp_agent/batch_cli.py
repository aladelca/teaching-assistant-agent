import argparse
import json
import os

from .batch import run_batch


def parse_args():
    ap = argparse.ArgumentParser(description="Batch grading CLI for student folders (apellidos_nombres)")
    ap.add_argument("--submissions-root", required=True, help="Root path with one folder per student")
    ap.add_argument("--student-key-regex", default=r"^[^/]+_[^/]+$", help="Regex for valid folder names")
    ap.add_argument("--notebook-glob", default="**/*.ipynb", help="Notebook discovery glob inside student folder")

    ap.add_argument("--rubric", required=True, help="Ruta al rubric.json")
    ap.add_argument("--assignment", help="Ruta al enunciado (txt)")
    ap.add_argument("--materials", help="Ruta a material del curso (txt)")

    ap.add_argument("--output-dir", default="outputs_batch", help="Directorio de salida")
    ap.add_argument("--summary-csv", default="gradebook_summary.csv", help="Nombre de CSV consolidado")
    ap.add_argument("--gradebook-column", default="Final Score", help="Nombre de columna para nota final")

    ap.add_argument("--llm-provider", default="mock", choices=["mock", "http", "agents"], help="Proveedor LLM")
    ap.add_argument("--model", default=os.getenv("LLM_MODEL", ""), help="Modelo LLM")
    ap.add_argument("--prompt", default="mvp_agent/prompts/evaluator_prompt.txt", help="Prompt de evaluación")
    ap.add_argument("--temperature", type=float, default=0.2)
    ap.add_argument("--max-tokens", type=int, default=1200)

    ap.add_argument("--execute-notebook", action="store_true", help="Ejecutar notebook antes de evaluar")
    ap.add_argument("--exec-mode", choices=["local", "docker"], default="local", help="Modo de ejecución")
    ap.add_argument("--execution-timeout", type=int, default=120, help="Timeout ejecución (seg)")
    ap.add_argument("--allow-exec-errors", action="store_true", help="Permitir errores de ejecución")
    ap.add_argument("--docker-image", default="mvp-notebook-exec:latest", help="Imagen Docker")
    ap.add_argument("--docker-cpus", default="2", help="CPUs contenedor")
    ap.add_argument("--docker-memory", default="2g", help="Memoria contenedor")
    ap.add_argument("--docker-network", default="none", help="Red contenedor")
    return ap.parse_args()


def main():
    args = parse_args()
    report = run_batch(args)
    print(json.dumps(report, ensure_ascii=False))


if __name__ == "__main__":
    main()
