import zipfile
from pathlib import Path

from mvp_agent.email_inbox import (
    BatchConfig,
    apply_roster_mapping,
    build_batch_args,
    build_notebook_student_index,
    compose_result_reply,
    parse_assignment_from_subject,
    prepare_submissions_root,
    select_config_and_submission_attachments,
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


def test_select_config_and_submission_attachments(tmp_path):
    files = []
    for name in [
        "rubric.json",
        "assignment.txt",
        "materials.txt",
        "students.csv",
        "entregas.zip",
        "solo.ipynb",
    ]:
        p = tmp_path / name
        p.write_text("x", encoding="utf-8")
        files.append(p)

    selected = select_config_and_submission_attachments(files)

    assert selected["rubric"].name == "rubric.json"
    assert selected["assignment"].name == "assignment.txt"
    assert selected["materials"].name == "materials.txt"
    assert selected["roster"].name == "students.csv"
    assert len(selected["submissions"]) == 2


def test_apply_roster_mapping_updates_summary_csv(tmp_path):
    summary = tmp_path / "gradebook_summary.csv"
    summary.write_text(
        "student_key,student_id,final_score\n"
        "perez_juan,perez_juan,18.00\n",
        encoding="utf-8",
    )

    submissions = tmp_path / "submissions"
    (submissions / "perez_juan").mkdir(parents=True)
    (submissions / "perez_juan" / "entrega1.ipynb").write_text("{}", encoding="utf-8")
    index = build_notebook_student_index(submissions)

    roster = [
        {
            "student_id": "2026001",
            "student_name": "Juan Perez",
            "expected_filename": "entrega1.ipynb",
        }
    ]
    apply_roster_mapping(summary, roster, index)

    rows = summary.read_text(encoding="utf-8")
    assert "2026001" in rows
    assert "Juan Perez" in rows


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
