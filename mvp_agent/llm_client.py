import json
import os
import urllib.request


def _get_by_path(data, path):
    if not path:
        return None
    cur = data
    for part in path.split("."):
        if part.isdigit():
            part = int(part)
        if isinstance(cur, list) and isinstance(part, int):
            cur = cur[part]
        elif isinstance(cur, dict):
            cur = cur.get(part)
        else:
            return None
    return cur


def http_complete(prompt, system, model, temperature=0.2, max_tokens=1200):
    api_url = os.getenv("LLM_API_URL")
    if not api_url:
        raise ValueError("LLM_API_URL is not set")

    payload_mode = os.getenv("LLM_PAYLOAD_MODE", "messages").lower()
    if payload_mode == "input":
        payload = {
            "model": model,
            "input": [
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
            "temperature": temperature,
            "max_output_tokens": max_tokens,
        }
        default_path = "output.0.content.0.text"
    else:
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        default_path = "choices.0.message.content"

    response_path = os.getenv("LLM_RESPONSE_PATH", default_path)

    headers = {"Content-Type": "application/json"}
    api_key = os.getenv("LLM_API_KEY")
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    req = urllib.request.Request(
        api_url, data=json.dumps(payload).encode("utf-8"), headers=headers
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        body = resp.read().decode("utf-8")
    data = json.loads(body)
    text = _get_by_path(data, response_path)
    if text is None:
        raise ValueError("LLM response path not found. Set LLM_RESPONSE_PATH.")
    return text

