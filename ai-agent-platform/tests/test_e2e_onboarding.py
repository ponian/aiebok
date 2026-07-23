"""E2E tests for the onboarding flow"""
import pytest
import httpx
import asyncio

CCA_URL = "http://localhost:9112"
MCP_URL = "http://localhost:9109"


@pytest.fixture
def client():
    return httpx.AsyncClient(timeout=60.0)


@pytest.mark.asyncio
async def test_agent_health(client):
    """Test all service health endpoints"""
    services = [
        ("MCP Service", f"{MCP_URL}/healthz"),
        ("CCA Agent", f"{CCA_URL}/healthz"),
    ]
    for name, url in services:
        response = await client.get(url)
        assert response.status_code == 200, f"{name} health check failed"
        assert response.json()["status"] == "healthy"


@pytest.mark.asyncio
async def test_tool_discovery(client):
    """Test MCP tool discovery"""
    response = await client.get(f"{MCP_URL}/mcp/tools/list")
    assert response.status_code == 200
    tools = response.json()["tools"]
    tool_names = [t["name"] for t in tools]
    assert "hr_agent_create_employee" in tool_names
    assert "it_agent_create_ad_account" in tool_names


@pytest.mark.asyncio
async def test_tool_call_direct(client):
    """Test direct tool call via MCP"""
    response = await client.post(
        f"{MCP_URL}/mcp/tools/call",
        json={
            "name": "it_agent_check_username",
            "arguments": {"username": "testuser"},
        },
    )
    assert response.status_code == 200
    result = response.json()
    assert result["status"] == "success"
    assert result["data"]["available"] is True


@pytest.mark.asyncio
async def test_task_submission(client):
    """Test task submission to CCA"""
    response = await client.post(
        f"{CCA_URL}/task",
        json={
            "content": "新員工李小華明天入職技術部擔任軟體工程師",
            "user_id": "hr_manager_001",
        },
    )
    assert response.status_code == 200
    result = response.json()
    assert "task_id" in result
    assert result["status"] == "accepted"


@pytest.mark.asyncio
async def test_concurrent_requests(client):
    """Test concurrent task submissions"""

    async def submit_task(i):
        return await client.post(
            f"{CCA_URL}/task",
            json={
                "content": f"測試員工_{i}入職市場部",
                "user_id": f"test_user_{i}",
            },
        )

    tasks = [submit_task(i) for i in range(5)]
    responses = await asyncio.gather(*tasks)

    for resp in responses:
        assert resp.status_code == 200
