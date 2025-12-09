# mcp_server/dummy_server.py
from fastapi import FastAPI
app = FastAPI()

@app.get("/health")
def health():
    return {"status":"ok"}
