import argparse
import json

from .agents_sdk_client import agents_complete
from .codex_cli_client import codex_complete
from .llm_client import http_complete
from .syllabus import extract_syllabus_text
from .utils import extract_json_block, read_text


def parse_args():
    ap = argparse.ArgumentParser(description="Extraer rúbrica desde sílabo PDF")
    ap.add_argument("--syllabus-pdf", required=True, help="Ruta a sílabo en PDF")
    ap.add_argument("--output", required=True, help="Ruta de salida rubric.json")
    ap.add_argument(
        "--llm-provider",
        default="agents",
        choices=["agents", "http", "codex"],
        help="Proveedor LLM",
    )
    ap.add_argument("--model", required=True, help="Modelo LLM")
    ap.add_argument(
        "--ocr-mode",
        default="auto",
        choices=["auto", "off", "force"],
        help="OCR solo si no hay texto embebido",
    )
    ap.add_argument("--max-pages", type=int, default=5)
    ap.add_argument("--min-chars", type=int, default=200)
    ap.add_argument(
        "--prompt",
        default="mvp_agent/prompts/syllabus_prompt.txt",
        help="Prompt de extracción",
    )
    ap.add_argument("--diagnostics", help="Ruta para guardar diagnostico JSON")
    return ap.parse_args()


def main():
    args = parse_args()
    extraction = extract_syllabus_text(
        args.syllabus_pdf,
        min_chars=args.min_chars,
        ocr_mode=args.ocr_mode,
        max_pages=args.max_pages,
    )
    text = extraction["text"]
    if not text:
        raise SystemExit("No se pudo extraer texto del sílabo.")

    prompt_template = read_text(args.prompt)
    prompt = prompt_template.format(syllabus_text=text)
    system = "Extrae rúbrica y políticas. Devuelve SOLO JSON válido."

    if args.llm_provider == "agents":
        response = agents_complete(prompt=prompt, system=system, model=args.model)
    elif args.llm_provider == "codex":
        response = codex_complete(prompt=prompt, system=system, model=args.model)
    else:
        response = http_complete(
            prompt=prompt,
            system=system,
            model=args.model,
            temperature=0.2,
            max_tokens=1200,
        )

    rubric = extract_json_block(response)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(rubric, f, ensure_ascii=False, indent=2)

    if args.diagnostics:
        with open(args.diagnostics, "w", encoding="utf-8") as f:
            json.dump(extraction, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
