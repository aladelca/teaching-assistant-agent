import csv
import glob
import json
import os
import re
from argparse import Namespace

from .cli import run_pipeline
from .utils import ensure_dir, utc_timestamp


def discover_student_folders(submissions_root: str, student_key_regex: str = r"^[^/]+_[^/]+$") -> list[str]:
    if not os.path.isdir(submissions_root):
        return []
    pat = re.compile(student_key_regex)
    out: list[str] = []
    for name in sorted(os.listdir(submissions_root)):
        full = os.path.join(submissions_root, name)
        if not os.path.isdir(full):
            continue
        if pat.match(name):
            out.append(full)
    return out


def find_notebook(student_dir: str, notebook_glob: str = "**/*.ipynb") -> str:
    matches = sorted(glob.glob(os.path.join(student_dir, notebook_glob), recursive=True))
    return matches[0] if matches else ""


def _default_row(student_key: str) -> dict:
    return {
        "student_key": student_key,
        "student_id": student_key,
        "final_score": "",
        "scale_min": 0,
        "scale_max": 20,
        "status": "skipped",
        "flags_count": 0,
        "top_feedback": "",
        "run_folder": "",
        "error": "",
    }


def run_batch(args) -> dict:
    batch_id = utc_timestamp()
    ensure_dir(args.output_dir)

    summary_rows: list[dict] = []
    student_dirs = discover_student_folders(args.submissions_root, args.student_key_regex)

    for student_dir in student_dirs:
        student_key = os.path.basename(student_dir)
        row = _default_row(student_key)

        notebook = find_notebook(student_dir, args.notebook_glob)
        if not notebook:
            row["error"] = "notebook_not_found"
            summary_rows.append(row)
            continue

        single_args = Namespace(
            notebook=notebook,
            rubric=args.rubric,
            assignment=args.assignment,
            materials=args.materials,
            student_id=student_key,
            output_dir=args.output_dir,
            gradebook_column=args.gradebook_column,
            llm_provider=args.llm_provider,
            model=args.model,
            prompt=args.prompt,
            temperature=args.temperature,
            max_tokens=args.max_tokens,
            execute_notebook=args.execute_notebook,
            exec_mode=args.exec_mode,
            execution_timeout=args.execution_timeout,
            allow_exec_errors=args.allow_exec_errors,
            docker_image=args.docker_image,
            docker_cpus=args.docker_cpus,
            docker_memory=args.docker_memory,
            docker_network=args.docker_network,
        )

        try:
            run_folder = run_pipeline(single_args)
            row["run_folder"] = run_folder
            row["status"] = "ok"

            eval_path = os.path.join(run_folder, "evaluation.json")
            if os.path.exists(eval_path):
                with open(eval_path, "r", encoding="utf-8") as f:
                    evaluation = json.load(f)
                row["final_score"] = f"{float(evaluation.get('final_score', 0.0)):.2f}"
                row["flags_count"] = len(evaluation.get("flags", []))
                summary = evaluation.get("summary", {})
                row["top_feedback"] = str(summary.get("priority", ""))[:240]
        except Exception as exc:  # noqa: BLE001
            row["status"] = "error"
            row["error"] = str(exc)[:300]

        summary_rows.append(row)

    summary_csv = os.path.join(args.output_dir, args.summary_csv)
    with open(summary_csv, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "student_key",
                "student_id",
                "final_score",
                "scale_min",
                "scale_max",
                "status",
                "flags_count",
                "top_feedback",
                "run_folder",
                "error",
            ],
        )
        writer.writeheader()
        for row in summary_rows:
            writer.writerow(row)

    report = {
        "batch_id": batch_id,
        "submissions_root": args.submissions_root,
        "students_discovered": len(student_dirs),
        "summary_csv": summary_csv,
        "rows": len(summary_rows),
        "ok": len([r for r in summary_rows if r["status"] == "ok"]),
        "errors": len([r for r in summary_rows if r["status"] == "error"]),
        "skipped": len([r for r in summary_rows if r["status"] == "skipped"]),
    }

    report_path = os.path.join(args.output_dir, "batch_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    report["report_path"] = report_path
    return report
