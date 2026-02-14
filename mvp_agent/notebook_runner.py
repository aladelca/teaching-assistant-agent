import json
import os
import tempfile
import shutil
import subprocess


def execute_notebook(
    input_path,
    output_path,
    timeout_sec=120,
    allow_errors=False,
):
    try:
        import nbformat
        from nbclient import NotebookClient
    except ImportError as exc:
        raise ImportError(
            "Dependencias faltantes para ejecutar notebooks. "
            "Instala con: pip install '.[exec]'"
        ) from exc

    nb = nbformat.read(input_path, as_version=4)

    with tempfile.TemporaryDirectory() as tmp_dir:
        client = NotebookClient(
            nb,
            timeout=timeout_sec,
            allow_errors=allow_errors,
            kernel_name="python3",
            resources={"metadata": {"path": tmp_dir}},
        )
        exec_error = None
        try:
            client.execute()
        except Exception as exc:
            exec_error = str(exc)

        nbformat.write(nb, output_path)

    errors = []
    for idx, cell in enumerate(nb.cells):
        for out in cell.get("outputs", []):
            if out.get("output_type") == "error":
                errors.append(
                    {
                        "cell_index": idx,
                        "ename": out.get("ename"),
                        "evalue": out.get("evalue"),
                    }
                )

    report = {
        "input_path": input_path,
        "output_path": output_path,
        "timeout_sec": timeout_sec,
        "allow_errors": allow_errors,
        "execution_error": exec_error,
        "cell_errors": errors,
        "success": exec_error is None and not errors,
        "mode": "local",
    }
    return report


def execute_notebook_docker(
    input_path,
    output_path,
    timeout_sec=120,
    image="mvp-notebook-exec:latest",
    cpus="2",
    memory="2g",
    network="none",
):
    if not shutil.which("docker"):
        raise RuntimeError("Docker no encontrado en PATH.")

    input_path = os.path.abspath(input_path)
    output_path = os.path.abspath(output_path)
    work_dir = os.path.dirname(input_path)
    runner_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "docker", "execute_nb.py"))

    input_name = os.path.basename(input_path)
    output_name = os.path.basename(output_path)

    cmd = [
        "docker",
        "run",
        "--rm",
        "--network",
        network,
        "--cpus",
        str(cpus),
        "--memory",
        str(memory),
        "-v",
        f"{work_dir}:/work",
        "-v",
        f"{runner_path}:/runner/execute_nb.py",
        image,
        "python",
        "/runner/execute_nb.py",
        f"/work/{input_name}",
        f"/work/{output_name}",
        str(timeout_sec),
    ]

    exec_error = None
    try:
        subprocess.run(cmd, check=True, timeout=timeout_sec + 30)
    except Exception as exc:
        exec_error = str(exc)

    report = {
        "input_path": input_path,
        "output_path": output_path,
        "timeout_sec": timeout_sec,
        "allow_errors": False,
        "execution_error": exec_error,
        "cell_errors": [],
        "success": exec_error is None,
        "mode": "docker",
        "docker_image": image,
    }
    return report
