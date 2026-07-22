"""Portal Backend — API gateway for the web UI"""
from fastapi import FastAPI
from pydantic import BaseModel
import httpx
import os
import uuid

app = FastAPI(title="Portal Backend")

CCA_URL = os.getenv("CCA_URL", "http://cca-agent:8084")


class ChatRequest(BaseModel):
    message: str
    user_id: str = "portal_user"


# In-memory conversation store
conversations: dict[str, list] = {}


@app.post("/api/chat")
async def chat(request: ChatRequest):
    conversation_id = str(uuid.uuid4())

    # Forward to CCA
    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            f"{CCA_URL}/task",
            json={"content": request.message, "user_id": request.user_id},
        )
        task_data = response.json()

    task_id = task_data.get("task_id")
    status_data: dict = {"status": "submitted", "result": "Task submitted", "steps": []}

    # Poll for completion
    if task_id:
        import asyncio
        async with httpx.AsyncClient(timeout=120.0) as client:
            for _ in range(120):
                status_resp = await client.get(f"{CCA_URL}/task/{task_id}")
                status_data = status_resp.json()
                if status_data.get("status") in ("completed", "failed"):
                    break
                await asyncio.sleep(1)

    return {
        "conversation_id": conversation_id,
        "task_id": task_id,
        "response": status_data.get("result", "Processing..."),
        "steps": status_data.get("steps", []),
    }


@app.get("/api/conversations")
async def list_conversations():
    return {"conversations": []}


@app.get("/healthz")
async def health():
    return {"status": "healthy"}
