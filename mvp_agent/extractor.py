import json


def load_notebook(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _cell_ref(index):
    return f"C{index + 1:03d}"


def extract_notebook_cells(nb):
    cells_out = []
    cells = nb.get("cells", [])
    for idx, cell in enumerate(cells):
        cell_type = cell.get("cell_type", "unknown")
        source = cell.get("source", "")
        if isinstance(source, list):
            source = "".join(source)
        outputs = []
        for out in cell.get("outputs", []):
            if out.get("output_type") == "stream":
                outputs.append("".join(out.get("text", "")))
            elif out.get("output_type") in ("execute_result", "display_data"):
                data = out.get("data", {})
                text_plain = data.get("text/plain", "")
                if isinstance(text_plain, list):
                    text_plain = "".join(text_plain)
                outputs.append(text_plain)
        cells_out.append(
            {
                "ref": _cell_ref(idx),
                "type": cell_type,
                "source": source.strip(),
                "outputs": "\n".join([o for o in outputs if o]).strip(),
            }
        )
    return cells_out


def build_notebook_text(cells):
    parts = []
    for cell in cells:
        parts.append(f"[CELL {cell['ref']}][{cell['type'].upper()}]")
        if cell["source"]:
            parts.append(cell["source"])
        if cell["outputs"]:
            parts.append(f"[OUTPUT {cell['ref']}]")
            parts.append(cell["outputs"])
        parts.append("")
    return "\n".join(parts).strip()


def build_context_pack(
    student_id,
    rubric,
    assignment_text,
    materials_text,
    notebook_path,
    execution_report=None,
):
    nb = load_notebook(notebook_path)
    cells = extract_notebook_cells(nb)
    notebook_text = build_notebook_text(cells)
    return {
        "student_id": student_id,
        "rubric": rubric,
        "assignment": assignment_text or "",
        "materials": materials_text or "",
        "notebook": {
            "path": notebook_path,
            "cells": cells,
            "text": notebook_text,
        },
        "execution_report": execution_report,
    }
