from vela.agent.tools import run_tool

print("1. Application lookup:")
print(run_tool("get_application_status", {"application_id": "VL-100007"}))

print("\n2. Messy ID (should still work):")
print(run_tool("get_application_status", {"application_id": "vl 100007"}))

print("\n3. ID that doesn't exist:")
print(run_tool("get_application_status", {"application_id": "VL-999999"}))

print("\n4. Notebook search:")
for r in run_tool("search_visa_requirements", {"query": "singapore visa fee"})["results"]:
    print("  ", r["id"], r["title"])

print("\n5. Escalation:")
print(run_tool("escalate_to_human", {"reason": "flying tomorrow", "urgency": "high"}))