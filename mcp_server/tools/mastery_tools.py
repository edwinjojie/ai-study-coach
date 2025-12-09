# mcp_server/tools/mastery_tools.py

def update_mastery(args):
    topic = args.get("topic")
    delta = args.get("delta", 0)

    # Mock response (later we connect TinyDB)
    return {
        "topic": topic,
        "new_mastery": max(0, min(100, delta + 50))  # mock mastery
    }

SCHEMA = {
    "input": {"topic": "string", "delta": "number"},
    "output": {"topic": "string", "new_mastery": "number"}
}
