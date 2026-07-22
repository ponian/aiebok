"""CCA Agent — Core Control Agent for Orchestration"""
from fastapi import FastAPI
from pydantic import BaseModel
import httpx
import json
import os
import uuid

from llm_client import OllamaClient
from prompt import CCA_SYSTEM_PROMPT

app = FastAPI(title="CCA Agent")

MCP_SERVICE_URL = os.getenv("MCP_SERVICE_URL", "http://mcp-service:8083")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434")
LLM_MODEL = os.getenv("LLM_MODEL", "llama3:8b")

llm = OllamaClient(base_url=OLLAMA_URL, model=LLM_MODEL)

# In-memory task store
tasks: dict = {}


class TaskRequest(BaseModel):
    content: str
    user_id: str


class TaskStatus(BaseModel):
    task_id: str
    status: str
    result: str | None = None
    steps: list = []


@app.post("/task")
async def submit_task(request: TaskRequest):
    task_id = str(uuid.uuid4())
    tasks[task_id] = {
        "task_id": task_id,
        "status": "processing",
        "content": request.content,
        "user_id": request.user_id,
        "steps": [],
        "result": None,
    }

    # Process asynchronously (in production, use background task)
    try:
        await process_task(task_id, request.content)
    except Exception as e:
        tasks[task_id]["status"] = "failed"
        tasks[task_id]["result"] = str(e)

    return {"task_id": task_id, "status": "accepted"}


@app.get("/task/{task_id}")
async def get_task(task_id: str):
    if task_id not in tasks:
        return {"error": "Task not found"}
    return tasks[task_id]


async def process_task(task_id: str, content: str):
    """Process a task through the LLM orchestration loop"""
    task = tasks[task_id]
    max_iterations = 10

    for i in range(max_iterations):
        # Build prompt with conversation history
        prompt = f"用戶請求：{content}\n\n"
        if task["steps"]:
            prompt += "已執行的步驟：\n"
            for step in task["steps"]:
                prompt += f"- {step['tool']}: {json.dumps(step['result'], ensure_ascii=False)}\n"
            prompt += "\n請根據以上結果決定下一步操作。如果所有步驟已完成，請提供最終回應。"

        # Call LLM
        response_text = await llm.generate(prompt, CCA_SYSTEM_PROMPT)

        # Parse LLM response
        try:
            # Try to extract JSON from response
            if "```json" in response_text:
                json_str = response_text.split("```json")[1].split("```")[0]
            elif "{" in response_text:
                json_str = response_text[response_text.index("{") : response_text.rindex("}") + 1]
            else:
                json_str = response_text

            response_data = json.loads(json_str)
        except json.JSONDecodeError:
            # If LLM doesn't return valid JSON, treat as final response
            task["status"] = "completed"
            task["result"] = response_text
            return

        # Check for tool calls
        tool_calls = response_data.get("tool_calls", [])
        final_response = response_data.get("final_response")

        if final_response and not tool_calls:
            task["status"] = "completed"
            task["result"] = final_response
            return

        if tool_calls:
            # Execute tool calls via MCP Service
            for tc in tool_calls:
                tool_name = tc["tool"]
                arguments = tc["arguments"]

                result = await call_mcp_tool(tool_name, arguments)
                task["steps"].append({"tool": tool_name, "arguments": arguments, "result": result})

        # If LLM provided final response, we're done
        if final_response:
            task["status"] = "completed"
            task["result"] = final_response
            return

    # Max iterations reached
    task["status"] = "completed"
    task["result"] = "任務已處理完成（達到最大迭代次數）"


async def call_mcp_tool(tool_name: str, arguments: dict) -> dict:
    """Call a tool via MCP Service"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{MCP_SERVICE_URL}/mcp/tools/call",
            json={"name": tool_name, "arguments": arguments},
        )
        return response.json()


@app.get("/healthz")
async def health():
    return {"status": "healthy", "model": LLM_MODEL, "tasks_count": len(tasks)}
