import re
import time
import httpx
from vela import config

URL = "https://api.groq.com/openai/v1/chat/completions"


def _to_groq_tools(tools):
    """Our tool menu uses 'input_schema'. Groq calls the same thing 'parameters'."""
    return [{"type": "function",
             "function": {"name": t["name"], "description": t["description"],
                          "parameters": t["input_schema"]}} for t in tools]


def chat(messages, tools):
    """Send the conversation to the brain. If Groq says 'too fast', wait and retry."""
    payload = {"model": config.LLM_MODEL, "messages": messages,
               "tools": _to_groq_tools(tools), "temperature": 0.2, "max_tokens": 300}
    headers = {"Authorization": f"Bearer {config.GROQ_API_KEY}"}

    for attempt in range(4):
        r = httpx.post(URL, json=payload, timeout=30, headers=headers)
        if r.status_code == 200:
            return r.json()["choices"][0]["message"]
        if r.status_code == 429 and attempt < 3:
            # Groq says things like "Please try again in 3.77s"
            found = re.search(r"try again in ([\d.]+)s", r.text)
            wait = float(found.group(1)) + 1 if found else 5
            print(f"      (Groq says slow down. Waiting {wait:.0f} seconds...)")
            time.sleep(wait)
            continue
        raise RuntimeError(f"Groq error {r.status_code}: {r.text[:300]}")