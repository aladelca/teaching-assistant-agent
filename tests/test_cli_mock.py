import subprocess
import sys


def test_cli_mock(tmp_path):
    out_dir = tmp_path / "outputs"
    cmd = [
        sys.executable,
        "-m",
        "mvp_agent.cli",
        "--notebook",
        "examples/sample.ipynb",
        "--rubric",
        "examples/rubric.json",
        "--assignment",
        "examples/assignment.txt",
        "--materials",
        "examples/materials.txt",
        "--student-id",
        "test@correo.com",
        "--output-dir",
        str(out_dir),
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    assert res.returncode == 0, res.stderr

    # Verify outputs created
    created = list(out_dir.glob("test@correo.com_*"))
    assert created, "No output folder created"
    output_folder = created[0]
    assert (output_folder / "feedback_student.txt").exists()
    assert (output_folder / "feedback_instructor.txt").exists()
    assert (output_folder / "gradebook_updates.csv").exists()
