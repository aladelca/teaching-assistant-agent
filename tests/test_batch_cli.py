import csv
import shutil
import subprocess
import sys


def test_batch_cli_generates_consolidated_summary(tmp_path):
    submissions = tmp_path / "submissions"
    submissions.mkdir(parents=True)

    s1 = submissions / "perez_juan"
    s1.mkdir()
    shutil.copy("examples/sample.ipynb", s1 / "entrega.ipynb")

    s2 = submissions / "garcia_maria"
    s2.mkdir()
    shutil.copy("examples/sample.ipynb", s2 / "trabajo.ipynb")

    out_dir = tmp_path / "outputs_batch"

    cmd = [
        sys.executable,
        "-m",
        "mvp_agent.batch_cli",
        "--submissions-root",
        str(submissions),
        "--rubric",
        "examples/rubric.json",
        "--assignment",
        "examples/assignment.txt",
        "--materials",
        "examples/materials.txt",
        "--output-dir",
        str(out_dir),
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    assert res.returncode == 0, res.stderr

    summary_csv = out_dir / "gradebook_summary.csv"
    assert summary_csv.exists()

    with open(summary_csv, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    assert len(rows) == 2
    assert all(r["status"] == "ok" for r in rows)
    assert all(r["final_score"] for r in rows)


def test_batch_cli_marks_missing_notebook_as_skipped(tmp_path):
    submissions = tmp_path / "submissions"
    submissions.mkdir(parents=True)
    (submissions / "sin_notebook_alumno").mkdir()

    out_dir = tmp_path / "outputs_batch"

    cmd = [
        sys.executable,
        "-m",
        "mvp_agent.batch_cli",
        "--submissions-root",
        str(submissions),
        "--student-key-regex",
        r"^sin_notebook_alumno$",
        "--rubric",
        "examples/rubric.json",
        "--assignment",
        "examples/assignment.txt",
        "--materials",
        "examples/materials.txt",
        "--output-dir",
        str(out_dir),
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    assert res.returncode == 0, res.stderr

    summary_csv = out_dir / "gradebook_summary.csv"
    with open(summary_csv, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    assert len(rows) == 1
    assert rows[0]["status"] == "skipped"
    assert rows[0]["error"] == "notebook_not_found"
