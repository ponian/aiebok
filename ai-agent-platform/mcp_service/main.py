"""MCP Service — Tool Registry & Call Routing"""
from fastapi import FastAPI
from pydantic import BaseModel
import httpx
import os

app = FastAPI(title="MCP Service")

NATS_URL = os.getenv("NATS_URL", "nats://nats:4222")

# Tool registry: name → {description, agent_url, schema}
tools_registry: dict = {}


class ToolCallRequest(BaseModel):
    name: str
    arguments: dict


@app.on_event("startup")
async def register_tools():
    """Register tools from agents on startup"""
    # In production, agents would self-register via NATS
    # For MVP, we hardcode the known tools
    global tools_registry
    tools_registry = {
        "hr_agent_create_employee": {
            "description": "創建新員工記錄",
            "agent_url": "http://hr-agent:8081",
            "schema": {
                "name": {"type": "string"},
                "department": {"type": "string"},
                "role": {"type": "string"},
                "start_date": {"type": "string"},
            },
        },
        "hr_agent_get_employee": {
            "description": "查詢員工信息",
            "agent_url": "http://hr-agent:8081",
            "schema": {"employee_id": {"type": "string"}},
        },
        "it_agent_create_ad_account": {
            "description": "創建 AD 賬戶",
            "agent_url": "http://it-agent:8082",
            "schema": {
                "username": {"type": "string"},
                "display_name": {"type": "string"},
                "department": {"type": "string"},
                "role": {"type": "string"},
            },
        },
        "it_agent_check_username": {
            "description": "檢查用戶名是否可用",
            "agent_url": "http://it-agent:8082",
            "schema": {"username": {"type": "string"}},
        },
        "it_agent_configure_permissions": {
            "description": "配置用戶權限",
            "agent_url": "http://it-agent:8082",
            "schema": {
                "account_id": {"type": "string"},
                "department": {"type": "string"},
                "role": {"type": "string"},
            },
        },
        "it_agent_send_notification": {
            "description": "發送通知郵件",
            "agent_url": "http://it-agent:8082",
            "schema": {
                "recipient": {"type": "string"},
                "template": {"type": "string"},
            },
        },
    }
    print(f"✅ Registered {len(tools_registry)} tools")


@app.get("/mcp/tools/list")
async def list_tools():
    return {
        "tools": [
            {"name": name, "description": info["description"], "schema": info["schema"]}
            for name, info in tools_registry.items()
        ]
    }


@app.post("/mcp/tools/call")
async def call_tool(request: ToolCallRequest):
    if request.name not in tools_registry:
        return {"error": f"Tool '{request.name}' not found"}

    tool = tools_registry[request.name]
    agent_url = tool["agent_url"]

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{agent_url}/execute",
            json={"tool": request.name, "arguments": request.arguments},
        )
        return response.json()


@app.get("/healthz")
async def health():
    return {"status": "healthy", "tools_count": len(tools_registry)}
