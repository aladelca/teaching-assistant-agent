import argparse
import json
import os
import sys

from .utils import read_text


def _render_value(template, variables):
    if template is None:
        return None
    return template.format(**variables)


def _load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _load_outputs(output_dir, mode):
    feedback_student = read_text(os.path.join(output_dir, "feedback_student.txt"))
    feedback_instructor = read_text(
        os.path.join(output_dir, "feedback_instructor.txt")
    )
    evaluation_path = os.path.join(output_dir, "evaluation.json")
    evaluation = _load_json(evaluation_path)

    return {
        "feedback_student": feedback_student,
        "feedback_instructor": feedback_instructor,
        "feedback": feedback_student if mode == "student" else feedback_instructor,
        "final_score": evaluation.get("final_score", 0),
        "gradebook_csv": os.path.join(output_dir, "gradebook_updates.csv"),
    }


def parse_args():
    ap = argparse.ArgumentParser(
        description="Browser Assist (Playwright) para ingresar notas/feedback"
    )
    ap.add_argument("--config", required=True, help="Ruta a archivo JSON de pasos")
    ap.add_argument("--output-dir", required=True, help="Carpeta de outputs del agente")
    ap.add_argument(
        "--mode",
        default="student",
        choices=["student", "instructor"],
        help="Cuál feedback usar",
    )
    ap.add_argument("--headless", action="store_true", help="Ejecutar en headless")
    ap.add_argument(
        "--storage-state",
        help="Ruta a storage_state.json (sesión guardada)",
    )
    return ap.parse_args()


def run_steps(page, steps, variables):
    for step in steps:
        action = step.get("action")
        if action == "goto":
            page.goto(_render_value(step.get("url"), variables))
        elif action == "wait_for":
            selector = _render_value(step.get("selector"), variables)
            timeout = step.get("timeout", 30000)
            page.wait_for_selector(selector, timeout=timeout)
        elif action == "click":
            selector = _render_value(step.get("selector"), variables)
            page.click(selector)
        elif action == "fill":
            selector = _render_value(step.get("selector"), variables)
            value = _render_value(step.get("value", ""), variables)
            page.fill(selector, value)
        elif action == "type":
            selector = _render_value(step.get("selector"), variables)
            value = _render_value(step.get("value", ""), variables)
            page.type(selector, value)
        elif action == "press":
            key = _render_value(step.get("key"), variables)
            page.keyboard.press(key)
        elif action == "upload":
            selector = _render_value(step.get("selector"), variables)
            path = _render_value(step.get("path"), variables)
            page.set_input_files(selector, path)
        elif action == "pause":
            message = step.get("message", "Presiona Enter para continuar...")
            input(message)
        else:
            raise ValueError(f"Unknown action: {action}")


def main():
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise SystemExit(
            "Playwright no está instalado. Instala con: pip install playwright && playwright install"
        ) from exc

    args = parse_args()
    steps_config = _load_json(args.config)
    steps = steps_config.get("steps", [])
    if not steps:
        raise SystemExit("Config sin pasos.")

    variables = _load_outputs(args.output_dir, args.mode)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=args.headless)
        context = (
            browser.new_context(storage_state=args.storage_state)
            if args.storage_state
            else browser.new_context()
        )
        page = context.new_page()
        run_steps(page, steps, variables)
        context.close()
        browser.close()


if __name__ == "__main__":
    main()

