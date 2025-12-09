import requests


class MCPClient:
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url.rstrip("/")

    def call_tool(self, name: str, args: dict) -> dict:
        payload = {"name": name, "args": args}
        url = f"{self.base_url}/call"
        r = requests.post(url, json=payload, timeout=30)
        r.raise_for_status()
        data = r.json()
        return data.get("result", {})

