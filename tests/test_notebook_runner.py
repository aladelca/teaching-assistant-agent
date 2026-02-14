import pytest


def test_execute_notebook(tmp_path):
    pytest.importorskip("nbclient")
    from mvp_agent.notebook_runner import execute_notebook

    out_path = tmp_path / "executed.ipynb"
    report = execute_notebook(
        "examples/sample.ipynb",
        str(out_path),
        timeout_sec=60,
        allow_errors=True,
    )
    assert report["output_path"].endswith("executed.ipynb")
