import httpx
from vela import config

r = httpx.get("https://api.groq.com/openai/v1/models",
              headers={"Authorization": f"Bearer {config.GROQ_API_KEY}"}, timeout=30)
print("status:", r.status_code)
for m in sorted(x["id"] for x in r.json().get("data", [])):
    print(m)