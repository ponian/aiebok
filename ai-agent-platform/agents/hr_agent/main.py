"""HR Agent — Employee Management"""
from fastapi import FastAPI
from pydantic import BaseModel
import httpx
import os

app = FastAPI(title="HR Agent")

HR_API_URL = os.getenv("HR_API_URL", "http://hr-api:8091")


class ToolCallRequest(BaseModel):
    tool: str
    arguments: dict


@app.post("/execute")
async def execute_tool(request: ToolCallRequest):
    tool_map = {
        "hr_agent_create_employee": create_employee,
        "hr_agent_get_employee": get_employee,
    }

    handler = tool_map.get(request.tool)
    if not handler:
        return {"error": f"Unknown tool: {request.tool}"}

    return await handler(request.arguments)


async def create_employee(args: dict) -> dict:
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{HR_API_URL}/v1/employees",
            json={
                "name": args["name"],
                "department": args["department"],
                "role": args["role"],
                "start_date": args["start_date"],
            },
        )
        result = response.json()

    return {
        "status": "success",
        "data": {"employee_id": result["employee_id"]},
        "message": result["message"],
    }


async def get_employee(args: dict) -> dict:
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(
            f"{HR_API_URL}/v1/employees/{args['employee_id']}"
        )
        result = response.json()

    return {
        "status": "success",
        "data": result,
    }


@app.get("/healthz")
async def health():
    return {"status": "healthy"}
