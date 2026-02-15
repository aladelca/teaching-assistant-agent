import zipfile
from pathlib import Path

from mvp_agent.email_inbox import (
    BatchConfig,
    build_batch_args,
    compose_result_reply,
    parse_assignment_from_subject,
    prepare_submissions_root,
)


def test_parse_assignment_from_subject_extracts_override():
    subject = "Entrega final [assignment:examples/assignment.txt]"
    assert parse_assignment_from_subject(subject) == "examples/assignment.txt"


def test_prepare_submissions_root_from_notebook_attachment(tmp_path):
    nb = tmp_path / "perez_juan.ipynb"
    nb.write_text(
        '{"cells": [], "metadata": {}, "nbformat": 4, "nbformat_minor": 5}',
        encoding="utf-8",
    )

    submissions = prepare_submissions_root([nb], tmp_path / "work")

    student_dir = submissions / "perez_juan"
    assert student_dir.exists()
    assert any(p.suffix == ".ipynb" for p in student_dir.iterdir())


def test_prepare_submissions_root_normalizes_zip_root_notebook(tmp_path):
    zip_path = tmp_path / "entregas.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr(
            "perez_juan.ipynb",
            '{"cells": [], "metadata": {}, "nbformat": 4, "nbformat_minor": 5}',
        )

    submissions = prepare_submissions_root([zip_path], tmp_path / "work_zip")
    student_dir = submissions / "perez_juan"
    assert student_dir.exists()
    assert (student_dir / "perez_juan.ipynb").exists()


def test_compose_result_reply_attaches_csv(tmp_path):
    csv_path = tmp_path / "gradebook_summary.csv"
    csv_path.write_text("student_id,final_score\na,18\n", encoding="utf-8")

    msg = compose_result_reply(
        from_addr="agent@example.com",
        to_addr="teacher@example.com",
        subject="Entrega",
        report={"students_discovered": 1, "rows": 1, "ok": 1, "errors": 0, "skipped": 0},
        csv_path=csv_path,
    )

    assert msg["Subject"] == "Re: Entrega"
    attachments = list(msg.iter_attachments())
    assert len(attachments) == 1
    assert attachments[0].get_filename() == "gradebook_summary.csv"


def test_build_batch_args_uses_override_assignment(tmp_path):
    cfg = BatchConfig(rubric="examples/rubric.json", assignment="examples/assignment.txt")
    args = build_batch_args(Path(tmp_path), cfg, assignment_override="custom_assignment.txt")
    assert args.assignment == "custom_assignment.txt"
