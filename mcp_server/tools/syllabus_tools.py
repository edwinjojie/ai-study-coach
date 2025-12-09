# mcp_server/tools/syllabus_tools.py

def parse_syllabus(args):
    text = args.get("text", "")
    
    # Mock parsing for now (we will replace with actual parser)
    topics = ["Introduction", "Module 1", "Module 2"]

    return {
        "topics": topics,
        "raw_text_length": len(text)
    }

SCHEMA = {
    "input": {"text": "string"},
    "output": {"topics": "list", "raw_text_length": "number"}
}
