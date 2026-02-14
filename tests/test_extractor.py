from mvp_agent.extractor import build_notebook_text, extract_notebook_cells, load_notebook


def test_extract_notebook_cells():
    nb = load_notebook("examples/sample.ipynb")
    cells = extract_notebook_cells(nb)
    assert len(cells) == 3
    assert cells[0]["ref"] == "C001"
    assert cells[1]["type"] == "code"
    assert "mean" in cells[1]["outputs"]


def test_build_notebook_text():
    nb = load_notebook("examples/sample.ipynb")
    cells = extract_notebook_cells(nb)
    text = build_notebook_text(cells)
    assert "[CELL C001]" in text
    assert "[OUTPUT C002]" in text
