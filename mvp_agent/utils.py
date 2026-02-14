import json
import os
import re
from datetime import datetime


def read_text(path):
    if not path:
        return ""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def read_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def ensure_dir(path):
    os.makedirs(path, exist_ok=True)


def utc_timestamp():
    return datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")


def extract_json_block(text):
    """
    Extract the first JSON object from a text blob.
    Returns a dict or raises ValueError.
    """
    if not text:
        raise ValueError("Empty LLM response")
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError("No JSON object found in response")
    json_str = match.group(0)
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON: {exc}") from exc
