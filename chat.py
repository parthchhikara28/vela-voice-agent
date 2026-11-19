import uuid
from vela.telemetry import TurnTrace
from vela.agent.agent import respond

call_id = uuid.uuid4().hex[:8]
history = []
print("Vela is listening. Type your question (type 'quit' to stop).\n")

while True:
    text = input("You: ").strip()
    if text.lower() in ("quit", "exit"):
        break
    if not text:
        continue
    trace = TurnTrace(call_id=call_id)
    reply = respond(history, text, trace)
    trace.emit()
    print(f"Vela: {reply}")
    print(f"      [tools: {[t['name'] for t in trace.tool_calls]}  time: {trace.marks.get('llm_done')}s]\n")