import argparse
import json
import os

from .email_inbox import BatchConfig, MailConfig, poll_and_process_once


def parse_args():
    ap = argparse.ArgumentParser(description="Email inbox grading processor")

    ap.add_argument("--imap-host", default=os.getenv("EMAIL_IMAP_HOST", ""))
    ap.add_argument("--imap-user", default=os.getenv("EMAIL_IMAP_USER", ""))
    ap.add_argument("--imap-password", default=os.getenv("EMAIL_IMAP_PASSWORD", ""))
    ap.add_argument("--mailbox", default=os.getenv("EMAIL_IMAP_MAILBOX", "INBOX"))

    ap.add_argument("--smtp-host", default=os.getenv("EMAIL_SMTP_HOST", ""))
    ap.add_argument("--smtp-port", type=int, default=int(os.getenv("EMAIL_SMTP_PORT", "465")))
    ap.add_argument("--smtp-user", default=os.getenv("EMAIL_SMTP_USER", ""))
    ap.add_argument("--smtp-password", default=os.getenv("EMAIL_SMTP_PASSWORD", ""))

    ap.add_argument("--rubric", required=True, help="Ruta al rubric.json")
    ap.add_argument("--assignment", help="Ruta al enunciado (txt)")
    ap.add_argument("--materials", help="Ruta a material del curso (txt)")

    ap.add_argument(
        "--student-key-regex",
        default=r"^[^/]+_[^/]+$",
        help="Regex para carpetas de alumno",
    )
    ap.add_argument("--notebook-glob", default="**/*.ipynb", help="Glob de notebooks")
    ap.add_argument("--output-dir", default="outputs_email", help="Directorio salida")
    ap.add_argument("--summary-csv", default="gradebook_summary.csv", help="CSV consolidado")
    ap.add_argument("--gradebook-column", default="Final Score", help="Columna de nota final")

    ap.add_argument("--llm-provider", default="mock", choices=["mock", "http", "agents"])
    ap.add_argument("--model", default=os.getenv("LLM_MODEL", ""))
    ap.add_argument("--prompt", default="mvp_agent/prompts/evaluator_prompt.txt")
    ap.add_argument("--temperature", type=float, default=0.2)
    ap.add_argument("--max-tokens", type=int, default=1200)

    ap.add_argument("--execute-notebook", action="store_true")
    ap.add_argument("--exec-mode", choices=["local", "docker"], default="local")
    ap.add_argument("--execution-timeout", type=int, default=120)
    ap.add_argument("--allow-exec-errors", action="store_true")
    ap.add_argument("--docker-image", default="mvp-notebook-exec:latest")
    ap.add_argument("--docker-cpus", default="2")
    ap.add_argument("--docker-memory", default="2g")
    ap.add_argument("--docker-network", default="none")

    return ap.parse_args()


def _validate_mail_args(args):
    required = {
        "imap-host": args.imap_host,
        "imap-user": args.imap_user,
        "imap-password": args.imap_password,
        "smtp-host": args.smtp_host,
        "smtp-user": args.smtp_user,
        "smtp-password": args.smtp_password,
    }
    missing = [k for k, v in required.items() if not v]
    if missing:
        raise ValueError(f"Missing required mail config: {', '.join(missing)}")


def main():
    args = parse_args()
    _validate_mail_args(args)

    mail_cfg = MailConfig(
        imap_host=args.imap_host,
        imap_user=args.imap_user,
        imap_password=args.imap_password,
        mailbox=args.mailbox,
        smtp_host=args.smtp_host,
        smtp_port=args.smtp_port,
        smtp_user=args.smtp_user,
        smtp_password=args.smtp_password,
    )

    batch_cfg = BatchConfig(
        rubric=args.rubric,
        assignment=args.assignment,
        materials=args.materials,
        student_key_regex=args.student_key_regex,
        notebook_glob=args.notebook_glob,
        output_dir=args.output_dir,
        summary_csv=args.summary_csv,
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

    result = poll_and_process_once(mail_cfg, batch_cfg)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
