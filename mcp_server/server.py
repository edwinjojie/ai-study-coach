# mcp_server/server.py

from fastapi import FastAPI
from pydantic import BaseModel
from mcp_server.tool_registry import ToolRegistry

# Import tools
from mcp_server.tools.syllabus_tools import parse_syllabus, SCHEMA as S_SCHEMA
from mcp_server.tools.mastery_tools import update_mastery, SCHEMA as M_SCHEMA

app = FastAPI()
registry = ToolRegistry()

# Register tools
registry.register("syllabus.parse", parse_syllabus, S_SCHEMA)
registry.register("mastery.update", update_mastery, M_SCHEMA)

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
