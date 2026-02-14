import os
import shutil
import subprocess
import tempfile


def codex_complete(prompt, system, model, timeout=240):
    if not shutil.which("codex"):
        raise RuntimeError(
            "Codex CLI no está instalado o no está en PATH. "
            "Instala Codex y ejecuta `codex login`."
        )

    model_name = model or os.getenv("CODEX_MODEL") or os.getenv("LLM_MODEL")
    if not model_name:
        raise ValueError("Model is required. Set --model, CODEX_MODEL, or LLM_MODEL.")

    combined_prompt = (
        f"System instructions:\n{system}\n\n"
        f"User prompt:\n{prompt}\n\n"
        "Return only the final answer content."
    )
    reasoning_effort = os.getenv("CODEX_REASONING_EFFORT", "high")

    with tempfile.TemporaryDirectory() as tmp_dir:
        output_path = os.path.join(tmp_dir, "codex_last_message.txt")
        cmd = [
            "codex",
            "exec",
            "-c",
            f'model_reasoning_effort="{reasoning_effort}"',
            "--sandbox",
            "read-only",
            "--skip-git-repo-check",
            "--ephemeral",
            "--model",
            model_name,
            "--output-last-message",
            output_path,
            "-",
        ]

        result = subprocess.run(
            cmd,
            input=combined_prompt,
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
        )

        if result.returncode != 0:
            detail = (result.stderr or result.stdout or "").strip()
            lowered = detail.lower()
            if "login" in lowered or "auth" in lowered or "unauthorized" in lowered:
                raise RuntimeError(
                    "Codex CLI no está autenticado. Ejecuta `codex login` "
                    "y vuelve a intentar."
                )
            raise RuntimeError(f"codex exec failed: {detail[:500]}")

        if not os.path.exists(output_path):
            raise RuntimeError("Codex no devolvió salida final.")

        with open(output_path, "r", encoding="utf-8") as f:
            text = f.read().strip()

    if not text:
        raise RuntimeError("Codex devolvió una respuesta vacía.")
    return text
