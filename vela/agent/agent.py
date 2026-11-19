import json
from vela.providers import llm
from vela.agent.prompt import SYSTEM_PROMPT
from vela.agent.tools import TOOLS, run_tool


def respond(history, user_text, trace):
    """Take what the traveller said, use tools if needed, return the spoken reply."""
    start = len(history)  # remember where this turn begins
    history.append({"role": "user", "content": user_text})
    trace.transcript = user_text

    for _ in range(4):  # the brain may use a tool, look at the result, then answer
        msg = llm.chat([{"role": "system", "content": SYSTEM_PROMPT}] + history, TOOLS)
        calls = msg.get("tool_calls")

        if not calls:
            reply = (msg.get("content") or "").strip()
            # Keep only the spoken words, drop the bulky tool results
            del history[start:]
            history.append({"role": "user", "content": user_text})
            history.append({"role": "assistant", "content": reply})
            trace.reply = reply
            trace.mark("llm_done")
            return reply

        history.append({"role": "assistant", "content": msg.get("content"), "tool_calls": calls})
        for c in calls:
            name = c["function"]["name"]
            args = json.loads(c["function"]["arguments"] or "{}")
            result = run_tool(name, args)
            trace.tool_calls.append({"name": name, "args": args})
            if name == "search_visa_requirements":
                trace.retrieved_ids += [r["id"] for r in result["results"]]
            history.append({"role": "tool", "tool_call_id": c["id"],
                            "content": json.dumps(result)})

    del history[start:]
    trace.reply = "Sorry, I got stuck. Let me connect you to a human."
    return trace.reply