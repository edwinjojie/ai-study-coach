# mcp_server/server.py

from fastapi import FastAPI
from pydantic import BaseModel
from mcp_server.tool_registry import ToolRegistry

# Import tools
from mcp_server.tools.syllabus_tools import parse_syllabus, SCHEMA as S_SCHEMA
from mcp_server.tools.mastery_tools import update_mastery, SCHEMA as M_SCHEMA
from mcp_server.tools.knowledge_tools import (
    load_knowledge,
    update_knowledge,
    get_weak_topics,
    get_graph,
    LOAD_SCHEMA,
    UPDATE_SCHEMA,
    WEAK_SCHEMA,
    GRAPH_SCHEMA,
)
from mcp_server.tools.llm_tools import explain_topic, flashcards_for_topic, generate_mcq, generate_studyplan
from mcp_server.tools.llm_tools import EXPLAIN_SCHEMA, FLAShCARD_SCHEMA, MCQ_SCHEMA, STUDYPLAN_SCHEMA

app = FastAPI()
registry = ToolRegistry()

# Register tools
registry.register("syllabus.parse", parse_syllabus, S_SCHEMA)
registry.register("mastery.update", update_mastery, M_SCHEMA)
registry.register("knowledge.load", load_knowledge, LOAD_SCHEMA)
registry.register("knowledge.update", update_knowledge, UPDATE_SCHEMA)
registry.register("knowledge.get_weak_topics", get_weak_topics, WEAK_SCHEMA)
registry.register("knowledge.get_graph", get_graph, GRAPH_SCHEMA)
registry.register("llm.explain", explain_topic, EXPLAIN_SCHEMA)
registry.register("llm.flashcards", flashcards_for_topic, FLAShCARD_SCHEMA)
registry.register("llm.generate_mcq", generate_mcq, MCQ_SCHEMA)
registry.register("llm.studyplan", generate_studyplan, STUDYPLAN_SCHEMA)

# -------- API MODELS -------- #

class ToolCall(BaseModel):
    name: str
    args: dict

# -------- ENDPOINTS -------- #

@app.get("/tools")
def get_tools():
    return registry.list_tools()

@app.post("/call")
def call_tool(call: ToolCall):
    result = registry.call(call.name, call.args)
    return {"result": result}

# -------- TEMP TEST ENDPOINT -------- #
@app.post("/test/pdf")
def test_pdf(payload: dict):
    from services.syllabus_service import SyllabusService
    service = SyllabusService()
    text = payload.get("text", "")
    cleaned = service.clean_text(text)
    topics = service.extract_topics(cleaned)
    return {"cleaned": cleaned, "topics": topics}
