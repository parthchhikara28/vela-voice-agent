import httpx
from vela import config

URL = "https://api.groq.com/openai/v1/chat/completions"


def _to_groq_tools(tools):
    """Our tool menu uses 'input_schema'. Groq calls the same thing 'parameters'."""
    return [{"type": "function",
             "function": {"name": t["name"], "description": t["description"],
                          "parameters": t["input_schema"]}} for t in tools]


def chat(messages, tools):
    """Send the conversation to the brain and return its next message."""
    payload = {"model": config.LLM_MODEL, "messages": messages,
               "tools": _to_groq_tools(tools), "temperature": 0.2, "max_tokens": 200}
    r = httpx.post(URL, json=payload, timeout=30,
                   headers={"Authorization": f"Bearer {config.GROQ_API_KEY}"})
    if r.status_code != 200:
        raise RuntimeError(f"Groq error {r.status_code}: {r.text[:300]}")
    return r.json()["choices"][0]["message"]