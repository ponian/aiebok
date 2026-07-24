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
        try:
            response = await client.post(
                f"{HR_API_URL}/v1/employees",
                json={
                    "name": args["name"],
                    "department": args["department"],
                    "role": args["role"],
                    "start_date": args["start_date"],
                },
            )
            response.raise_for_status()
            result = response.json()
        except httpx.HTTPStatusError as e:
            return {"status": "error", "message": f"HR API returned HTTP {e.response.status_code}", "detail": e.response.text[:500]}
        except (httpx.RequestError, ValueError) as e:
            return {"status": "error", "message": f"HR API communication failed: {e}"}

    return {
        "status": "success",
        "data": {"employee_id": result.get("employee_id", "unknown")},
        "message": result.get("message", "員工已創建"),
    }


async def get_employee(args: dict) -> dict:
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(
                f"{HR_API_URL}/v1/employees/{args['employee_id']}"
            )
            response.raise_for_status()
            result = response.json()
        except httpx.HTTPStatusError as e:
            return {"status": "error", "message": f"HR API returned HTTP {e.response.status_code}", "detail": e.response.text[:500]}
        except (httpx.RequestError, ValueError) as e:
            return {"status": "error", "message": f"HR API communication failed: {e}"}

    return {
        "status": "success",
        "data": result,
    }


@app.get("/healthz")
async def health():
    return {"status": "healthy"}
