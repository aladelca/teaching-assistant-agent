import pytest

from mvp_agent.utils import extract_json_block, read_text


def test_extract_json_block_ok():
    text = 'respuesta: {"a": 1, "b": "x"} fin'
    data = extract_json_block(text)
    assert data["a"] == 1
    assert data["b"] == "x"


def test_extract_json_block_missing():
    with pytest.raises(ValueError):
        extract_json_block("no json here")


def test_read_text_packaged_prompt_alias():
    text = read_text("mvp_agent/prompts/evaluator_prompt.txt")
    assert "STUDENT_ID" in text
