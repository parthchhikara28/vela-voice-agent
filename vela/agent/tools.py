from vela.agent import retriever, db

TOOLS = [
    {"name": "get_application_status",
     "description": "Look up a visa application by its reference ID (format VL-XXXXXX).",
     "input_schema": {"type": "object",
                      "properties": {"application_id": {"type": "string"}},
                      "required": ["application_id"]}},
    {"name": "search_visa_requirements",
     "description": "Search the visa knowledge base. Use for any question about documents, fees, or processing times.",
     "input_schema": {"type": "object",
                      "properties": {"query": {"type": "string"}, "country": {"type": "string"}},
                      "required": ["query"]}},
    {"name": "escalate_to_human",
     "description": ("Transfer to a human agent. Use when the traveller is distressed, asks for a refund "
                     "or legal advice, has an urgent departure within 48 hours, or after two failed "
                     "attempts to resolve."),
     "input_schema": {"type": "object",
                      "properties": {"reason": {"type": "string"},
                                     "urgency": {"type": "string", "enum": ["low", "high"]}},
                      "required": ["reason"]}},
]


def run_tool(name, args):
    """Do the thing the brain asked for and return the result."""
    if name == "get_application_status":
        return db.get_application(args.get("application_id", ""))
    if name == "search_visa_requirements":
        pieces = retriever.search(args["query"], args.get("country"))
        return {"results": [{"id": p["id"], "title": p["title"], "text": p["text"]} for p in pieces]}
    if name == "escalate_to_human":
        return {"transferred": True, "reason": args.get("reason", ""),
                "urgency": args.get("urgency", "low")}
    return {"error": f"Unknown tool: {name}"}