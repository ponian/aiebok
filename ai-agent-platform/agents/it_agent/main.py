"""IT Agent — AD Account Management"""
from fastapi import FastAPI
from pydantic import BaseModel
import httpx
import os
import uuid

app = FastAPI(title="IT Agent")

AD_API_URL = os.getenv("AD_API_URL", "http://ad-api:8090")


class ToolCallRequest(BaseModel):
    tool: str
    arguments: dict


@app.post("/execute")
async def execute_tool(request: ToolCallRequest):
    tool_map = {
        "it_agent_create_ad_account": create_ad_account,
        "it_agent_check_username": check_username,
        "it_agent_configure_permissions": configure_permissions,
        "it_agent_send_notification": send_notification,
    }

    handler = tool_map.get(request.tool)
    if not handler:
        return {"error": f"Unknown tool: {request.tool}"}

    return await handler(request.arguments)


async def create_ad_account(args: dict) -> dict:
    temp_password = f"Temp{uuid.uuid4().hex[:8]}!"

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(
                f"{AD_API_URL}/v1/accounts",
                json={
                    "username": args["username"],
                    "display_name": args["display_name"],
                    "department": args["department"],
                    "role": args["role"],
                    "temp_password": temp_password,
                },
            )
            response.raise_for_status()
            result = response.json()
        except httpx.HTTPStatusError as e:
            return {"status": "error", "message": f"AD API returned HTTP {e.response.status_code}", "detail": e.response.text[:500]}
        except (httpx.RequestError, ValueError) as e:
            return {"status": "error", "message": f"AD API communication failed: {e}"}

    return {
        "status": "success",
        "data": {
            "account_id": result.get("account_id", "unknown"),
            "email": result.get("email", "unknown"),
            "temp_password": temp_password,
        },
        "message": f"已成功為 {args['display_name']} 創建 AD 賬戶",
    }


async def check_username(args: dict) -> dict:
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(
                f"{AD_API_URL}/v1/check-username/{args['username']}"
            )
            response.raise_for_status()
            result = response.json()
        except httpx.HTTPStatusError as e:
            return {"status": "error", "message": f"AD API returned HTTP {e.response.status_code}", "detail": e.response.text[:500]}
        except (httpx.RequestError, ValueError) as e:
            return {"status": "error", "message": f"AD API communication failed: {e}"}

    return {
        "status": "success",
        "data": {"available": result.get("available", False)},
    }


async def configure_permissions(args: dict) -> dict:
    department = args.get("department", "")
    role = args.get("role", "")

    base_groups = ["General Users", "Domain Users"]
    dept_groups = {
        "市場部": ["Marketing Team", "Marketing Content"],
        "技術部": ["Engineering Team", "Dev Access"],
        "產品部": ["Product Team", "Analytics Access"],
        "行政部": ["Admin Team", "Office Access"],
    }
    groups = base_groups + dept_groups.get(department, [])

    return {
        "status": "success",
        "data": {"groups_assigned": groups},
        "message": f"已配置 {len(groups)} 個權限組",
    }


async def send_notification(args: dict) -> dict:
    return {
        "status": "success",
        "data": {"sent": True},
        "message": f"已向 {args['recipient']} 發送 {args['template']} 郵件",
    }


@app.get("/healthz")
async def health():
    return {"status": "healthy"}
