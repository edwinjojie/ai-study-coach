from services.syllabus_service import SyllabusService

service = SyllabusService()

def parse_syllabus(args):
    pdf_text = args.get("text", "")
    cleaned = service.clean_text(pdf_text)
    topics = service.extract_topics(cleaned)
    return {"topics": topics}

SCHEMA = {
    "input": {"text": "string"},
    "output": {"topics": "list"}
}
