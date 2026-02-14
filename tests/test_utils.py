import pytest

from mvp_agent.utils import extract_json_block


def test_extract_json_block_ok():
    text = "respuesta: {\"a\": 1, \"b\": \"x\"} fin"
    data = extract_json_block(text)
    assert data["a"] == 1
    assert data["b"] == "x"


def test_extract_json_block_missing():
    with pytest.raises(ValueError):
        extract_json_block("no json here")
