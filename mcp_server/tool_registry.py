# mcp_server/tool_registry.py

class ToolRegistry:
    def __init__(self):
        self.tools = {}

    def register(self, name, func, schema=None):
        self.tools[name] = {
            "func": func,
            "schema": schema or {}
        }

    def list_tools(self):
        return [
            {"name": name, "schema": info["schema"]}
            for name, info in self.tools.items()
        ]

    def call(self, name, args):
        if name not in self.tools:
            raise ValueError(f"Tool '{name}' not found")
        return self.tools[name]["func"](args)
