from __future__ import annotations

import csv
import email
import email.policy
import imaplib
import os
import re
import smtplib
import zipfile
from argparse import Namespace
from dataclasses import dataclass
from email.message import EmailMessage
from email.utils import parseaddr
from pathlib import Path
from typing import Iterable

from .batch import run_batch
from .utils import ensure_dir, utc_timestamp

DEFAULT_SUBJECT_ASSIGNMENT_RE = re.compile(r"\[assignment:(?P<name>[^\]]+)\]", re.IGNORECASE)
DEFAULT_STUDENT_FOLDER_RE = re.compile(r"^[^/]+_[^/]+$")

ROSTER_ID_KEYS = {"student_id", "id", "matricula", "codigo", "codigo_alumno"}
ROSTER_NAME_KEYS = {"student_name", "name", "nombre", "alumno"}
ROSTER_FILE_KEYS = {"expected_filename", "filename", "file", "notebook", "archivo"}


@dataclass
class BatchConfig:
    rubric: str
    assignment: str | None = None
    materials: str | None = None
    student_key_regex: str = r"^[^/]+_[^/]+$"
    notebook_glob: str = "**/*.ipynb"
    output_dir: str = "outputs_email"
    summary_csv: str = "gradebook_summary.csv"
    gradebook_column: str = "Final Score"
    llm_provider: str = "mock"
    model: str = ""
    prompt: str = "mvp_agent/prompts/evaluator_prompt.txt"
    temperature: float = 0.2
    max_tokens: int = 1200
    execute_notebook: bool = False
    exec_mode: str = "local"
    execution_timeout: int = 120
    allow_exec_errors: bool = False
    docker_image: str = "mvp-notebook-exec:latest"
    docker_cpus: str = "2"
    docker_memory: str = "2g"
    docker_network: str = "none"


@dataclass
class MailConfig:
    imap_host: str
    imap_user: str
    imap_password: str
    smtp_host: str
    smtp_port: int
    smtp_user: str
    smtp_password: str
    mailbox: str = "INBOX"


def parse_assignment_from_subject(subject: str) -> str | None:
    if not subject:
        return None
    match = DEFAULT_SUBJECT_ASSIGNMENT_RE.search(subject)
    if not match:
        return None
    return match.group("name").strip()


def _safe_filename(name: str) -> str:
    base = os.path.basename(name or "attachment")
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", base).strip("._")
    return cleaned or "attachment"


def _safe_extract_zip(zip_path: Path, dest_dir: Path) -> None:
    with zipfile.ZipFile(zip_path) as zf:
        for member in zf.infolist():
            target = (dest_dir / member.filename).resolve()
            if not str(target).startswith(str(dest_dir.resolve())):
                continue
            if member.is_dir():
                target.mkdir(parents=True, exist_ok=True)
                continue
            ensure_dir(str(target.parent))
            with zf.open(member, "r") as src, open(target, "wb") as out:
                out.write(src.read())


def extract_attachments_to_dir(message: EmailMessage, dest_dir: Path) -> list[Path]:
    ensure_dir(str(dest_dir))
    files: list[Path] = []
    for part in message.iter_attachments():
        filename = _safe_filename(part.get_filename() or "attachment.bin")
        payload = part.get_payload(decode=True)
        if payload is None:
            continue
        path = dest_dir / filename
        with open(path, "wb") as f:
            f.write(payload)
        files.append(path)
    return files


def _build_student_key_from_notebook(path: Path) -> str:
    stem = re.sub(r"[^A-Za-z0-9_]+", "_", path.stem).strip("_")
    if DEFAULT_STUDENT_FOLDER_RE.match(stem):
        return stem
    return f"inbox_{stem or 'student'}"


def _normalize_notebooks_in_root(submissions: Path) -> None:
    for nb_path in submissions.glob("*.ipynb"):
        student_key = _build_student_key_from_notebook(nb_path)
        student_dir = submissions / student_key
        student_dir.mkdir(parents=True, exist_ok=True)
        target = student_dir / nb_path.name
        if target != nb_path:
            target.write_bytes(nb_path.read_bytes())
            nb_path.unlink(missing_ok=True)


def select_config_and_submission_attachments(
    attachments: Iterable[Path],
) -> dict[str, Path | list[Path] | None]:
    rubric: Path | None = None
    assignment: Path | None = None
    materials: Path | None = None
    roster: Path | None = None
    submissions: list[Path] = []

    for attachment in attachments:
        name = attachment.name.lower()
        if name == "rubric.json":
            rubric = attachment
            continue
        if name in {"assignment.txt", "enunciado.txt"}:
            assignment = attachment
            continue
        if name in {"materials.txt", "materiales.txt"}:
            materials = attachment
            continue
        if name in {"students.csv", "roster.csv", "alumnos.csv"}:
            roster = attachment
            continue
        if attachment.suffix.lower() in {".zip", ".ipynb"}:
            submissions.append(attachment)

    return {
        "rubric": rubric,
        "assignment": assignment,
        "materials": materials,
        "roster": roster,
        "submissions": submissions,
    }


def prepare_submissions_root(attachments: Iterable[Path], work_dir: Path) -> Path:
    submissions = work_dir / "submissions"
    submissions.mkdir(parents=True, exist_ok=True)

    for attachment in attachments:
        suffix = attachment.suffix.lower()
        if suffix == ".zip":
            _safe_extract_zip(attachment, submissions)
            continue
        if suffix == ".ipynb":
            student_key = _build_student_key_from_notebook(attachment)
            student_dir = submissions / student_key
            student_dir.mkdir(parents=True, exist_ok=True)
            (student_dir / attachment.name).write_bytes(attachment.read_bytes())

    _normalize_notebooks_in_root(submissions)
    return submissions


def build_notebook_student_index(submissions_root: Path) -> dict[str, str]:
    index: dict[str, str] = {}
    for nb in submissions_root.rglob("*.ipynb"):
        try:
            rel = nb.relative_to(submissions_root)
            student_key = rel.parts[0]
        except (ValueError, IndexError):
            continue
        index[nb.name.lower()] = student_key
    return index


def _normalize_row_keys(row: dict) -> dict[str, str]:
    return {str(k).strip().lower(): str(v or "").strip() for k, v in row.items()}


def load_roster_csv(roster_path: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    with open(roster_path, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for raw_row in reader:
            row = _normalize_row_keys(raw_row)
            sid = next((row[k] for k in ROSTER_ID_KEYS if k in row and row[k]), "")
            sname = next((row[k] for k in ROSTER_NAME_KEYS if k in row and row[k]), "")
            expected = next((row[k] for k in ROSTER_FILE_KEYS if k in row and row[k]), "")
            if sid or sname or expected:
                rows.append(
                    {
                        "student_id": sid,
                        "student_name": sname,
                        "expected_filename": os.path.basename(expected).lower(),
                    }
                )
    return rows


def apply_roster_mapping(
    summary_csv: Path,
    roster_rows: list[dict[str, str]],
    notebook_index: dict[str, str],
) -> None:
    if not summary_csv.exists() or not roster_rows:
        return

    roster_by_student_key: dict[str, dict[str, str]] = {}
    for row in roster_rows:
        expected = row.get("expected_filename", "").lower()
        if not expected:
            continue
        student_key = notebook_index.get(expected)
        if not student_key:
            continue
        roster_by_student_key[student_key] = row

    with open(summary_csv, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames or [])
        rows = list(reader)

    extra_fields = ["student_name", "expected_filename", "match_source"]
    for f in extra_fields:
        if f not in fieldnames:
            fieldnames.append(f)

    for row in rows:
        student_key = str(row.get("student_key", ""))
        mapped = roster_by_student_key.get(student_key)
        if not mapped:
            row.setdefault("student_name", "")
            row.setdefault("expected_filename", "")
            row["match_source"] = "unmatched"
            continue

        if mapped.get("student_id"):
            row["student_id"] = mapped["student_id"]
        row["student_name"] = mapped.get("student_name", "")
        row["expected_filename"] = mapped.get("expected_filename", "")
        row["match_source"] = "expected_filename"

    with open(summary_csv, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def build_batch_args(
    submissions_root: Path,
    batch_cfg: BatchConfig,
    assignment_override: str | None = None,
    rubric_override: str | None = None,
    materials_override: str | None = None,
) -> Namespace:
    return Namespace(
        submissions_root=str(submissions_root),
        student_key_regex=batch_cfg.student_key_regex,
        notebook_glob=batch_cfg.notebook_glob,
        rubric=rubric_override or batch_cfg.rubric,
        assignment=assignment_override or batch_cfg.assignment,
        materials=materials_override or batch_cfg.materials,
        output_dir=batch_cfg.output_dir,
        summary_csv=batch_cfg.summary_csv,
        gradebook_column=batch_cfg.gradebook_column,
        llm_provider=batch_cfg.llm_provider,
        model=batch_cfg.model,
        prompt=batch_cfg.prompt,
        temperature=batch_cfg.temperature,
        max_tokens=batch_cfg.max_tokens,
        execute_notebook=batch_cfg.execute_notebook,
        exec_mode=batch_cfg.exec_mode,
        execution_timeout=batch_cfg.execution_timeout,
        allow_exec_errors=batch_cfg.allow_exec_errors,
        docker_image=batch_cfg.docker_image,
        docker_cpus=batch_cfg.docker_cpus,
        docker_memory=batch_cfg.docker_memory,
        docker_network=batch_cfg.docker_network,
    )


def compose_result_reply(
    from_addr: str,
    to_addr: str,
    subject: str,
    report: dict,
    csv_path: Path | None,
) -> EmailMessage:
    msg = EmailMessage()
    msg["From"] = from_addr
    msg["To"] = to_addr
    msg["Subject"] = f"Re: {subject}"

    body = [
        "Procesamiento completado.",
        "",
        f"Students discovered: {report.get('students_discovered', 0)}",
        f"Rows: {report.get('rows', 0)}",
        f"OK: {report.get('ok', 0)}",
        f"Errors: {report.get('errors', 0)}",
        f"Skipped: {report.get('skipped', 0)}",
    ]
    msg.set_content("\n".join(body))

    if csv_path and csv_path.exists():
        data = csv_path.read_bytes()
        msg.add_attachment(data, maintype="text", subtype="csv", filename=csv_path.name)

    return msg


def _decode_subject(raw_msg: email.message.Message) -> str:
    value = raw_msg.get("Subject", "")
    decoded = email.header.decode_header(value)
    chunks: list[str] = []
    for part, enc in decoded:
        if isinstance(part, bytes):
            chunks.append(part.decode(enc or "utf-8", errors="replace"))
        else:
            chunks.append(part)
    return "".join(chunks)


def process_single_message(
    raw_msg: email.message.Message,
    batch_cfg: BatchConfig,
    sender_from: str,
) -> tuple[dict, Path | None, str]:
    subject = _decode_subject(raw_msg)
    sender = parseaddr(raw_msg.get("From", ""))[1] or sender_from

    run_base = Path(batch_cfg.output_dir) / f"email_{utc_timestamp()}"
    run_base.mkdir(parents=True, exist_ok=True)

    all_attachments = extract_attachments_to_dir(raw_msg, run_base / "attachments")
    selected = select_config_and_submission_attachments(all_attachments)

    submission_attachments = selected["submissions"] or []
    submissions_root = prepare_submissions_root(submission_attachments, run_base)
    notebook_index = build_notebook_student_index(submissions_root)

    assignment_override = parse_assignment_from_subject(subject)
    if selected["assignment"]:
        assignment_override = str(selected["assignment"])

    rubric_override = str(selected["rubric"]) if selected["rubric"] else None
    materials_override = str(selected["materials"]) if selected["materials"] else None

    batch_args = build_batch_args(
        submissions_root,
        batch_cfg,
        assignment_override=assignment_override,
        rubric_override=rubric_override,
        materials_override=materials_override,
    )
    report = run_batch(batch_args)

    csv_path = Path(report.get("summary_csv", "")) if report.get("summary_csv") else None

    if selected["roster"] and csv_path:
        roster_rows = load_roster_csv(Path(selected["roster"]))
        apply_roster_mapping(csv_path, roster_rows, notebook_index)

    return report, csv_path, sender


def poll_and_process_once(mail_cfg: MailConfig, batch_cfg: BatchConfig) -> dict:
    imap = imaplib.IMAP4_SSL(mail_cfg.imap_host)
    imap.login(mail_cfg.imap_user, mail_cfg.imap_password)
    imap.select(mail_cfg.mailbox)
    status, data = imap.search(None, "UNSEEN")
    if status != "OK":
        imap.logout()
        return {"processed": 0, "sent": 0, "errors": 1}

    ids = data[0].split()
    sent = 0
    errors = 0

    smtp = smtplib.SMTP_SSL(mail_cfg.smtp_host, mail_cfg.smtp_port)
    smtp.login(mail_cfg.smtp_user, mail_cfg.smtp_password)

    for msg_id in ids:
        try:
            st, raw_data = imap.fetch(msg_id, "(RFC822)")
            if st != "OK" or not raw_data or not raw_data[0]:
                errors += 1
                continue

            parsed = email.message_from_bytes(raw_data[0][1], policy=email.policy.default)
            report, csv_path, sender = process_single_message(parsed, batch_cfg, mail_cfg.smtp_user)
            reply = compose_result_reply(
                mail_cfg.smtp_user,
                sender,
                _decode_subject(parsed),
                report,
                csv_path,
            )
            smtp.send_message(reply)
            sent += 1
        except Exception:  # noqa: BLE001
            errors += 1

    smtp.quit()
    imap.logout()
    return {"processed": len(ids), "sent": sent, "errors": errors}
