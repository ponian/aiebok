# 第十二章：參考實作 MVP — 新員工入職全流程演示

> 「Talk is cheap, show me the code. 本章將前面 11 章的所有概念整合成一個完整的、可運行的 MVP 參考實作。」

本章提供一個完整的、可直接運行的 MVP 參考代碼。讀者可以 clone 這個項目，按照 README 的指示啟動所有服務，並通過 Portal 界面體驗一個完整的新員工入職流程。

---

## 12.1 項目結構

```
ai-agent-platform/
├── docker-compose.yml          # 一鍵啟動所有服務
├── .env.example                # 環境變量模板
├── README.md                   # 快速啟動指南
│
├── agents/
│   ├── cca/
│   │   ├── __init__.py
│   │   ├── main.py             # CCA Agent 入口
│   │   ├── orchestrator.py     # 任務編排器
│   │   ├── llm_client.py       # LLM 客戶端（Ollama）
│   │   ├── memory.py           # 記憶管理
│   │   └── config.yaml         # CCA 配置
│   │
│   ├── it_agent/
│   │   ├── __init__.py
│   │   ├── main.py             # IT Agent 入口
│   │   ├── tools.py            # AD 工具集
│   │   ├── prompt.py           # 系統提示
│   │   └── config.yaml         # IT Agent 配置
│   │
│   └── hr_agent/
│       ├── __init__.py
│       ├── main.py             # HR Agent 入口
│       ├── tools.py            # HR 工具集
│       ├── prompt.py           # 系統提示
│       └── config.yaml         # HR Agent 配置
│
├── mcp_service/
│   ├── __init__.py
│   ├── app.py                  # MCP Service 入口
│   ├── registry.py             # Agent 註冊表
│   ├── tools_list.py           # 工具發現
│   ├── tools_call.py           # 工具調用
│   └── auth.py                 # 認證授權
│
├── knowledge/
│   ├── base_builder.py         # 知識庫構建器
│   ├── hr_policies/            # HR 政策文檔
│   │   ├── onboarding.md
│   │   ├── offboarding.md
│   │   └── leave_policy.md
│   └── it_knowledge/           # IT 知識庫
│       ├── ad_account.md
│       └── permission_templates.yaml
│
├── portal/
│   ├── backend/
│   │   ├── main.py             # FastAPI 後端入口
│   │   ├── routes/
│   │   │   ├── chat.py         # 聊天 API
│   │   │   ├── tasks.py        # 任務 API
│   │   │   └── audit.py        # 審計 API
│   │   └── websocket.py        # WebSocket 處理
│   │
│   └── frontend/
│       ├── package.json
│       ├── app/
│       │   ├── page.tsx         # 首頁
│       │   ├── layout.tsx       # 佈局
│       │   └── tasks/
│       │       └── [id]/
│       │           └── page.tsx # 任務詳情
│       └── components/
│           ├── ChatInterface.tsx
│           ├── MessageBubble.tsx
│           ├── TaskList.tsx
│           └── MonitorPanel.tsx
│
├── infrastructure/
│   ├── nats/
│   │   └── nats.conf            # NATS 配置
│   ├── postgresql/
│   │   └── init.sql             # 數據庫初始化
│   └── chromadb/
│       └── config.yaml          # ChromaDB 配置
│
├── monitoring/
│   ├── otel/
│   │   └── otel-collector.yaml  # OTel Collector 配置
│   ├── prometheus/
│   │   └── prometheus.yml       # Prometheus 配置
│   └── grafana/
│       └── dashboards/
│           └── ai-platform.json # Grafana 儀表板
│
├── tests/
│   ├── test_cca.py
│   ├── test_it_agent.py
│   ├── test_hr_agent.py
│   ├── test_mcp_service.py
│   └── performance/
│       └── test_load.py
│
└── docs/
    ├── architecture.md          # 架構文檔
    ├── api.md                   # API 文檔
    └── deployment.md            # 部署文檔
```

---

## 12.2 Docker Compose 一鍵啟動

### 12.2.1 環境變量配置

```bash
# .env.example
# LLM 配置
OLLAMA_BASE_URL=http://ollama:11434
LLM_MODEL=llama3:70b
LLM_TEMPERATURE=0.2

# MCP Service
MCP_PORT=8080
MCP_AUTH_API_KEY=your-api-key-here

# IT Agent
AD_API_URL=http://mock-ad-api:8080
AD_API_TOKEN=your-ad-token

# HR Agent
HR_API_URL=http://mock-hr-api:8080
HR_API_TOKEN=your-hr-token

# Database
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=ai_platform
POSTGRES_USER=ai_platform
POSTGRES_PASSWORD=change_me_in_production

# NATS
NATS_URL=nats://nats:4222

# Vector Store
CHROMADB_URL=http://chromadb:8000

# Monitoring
OTEL_ENDPOINT=http://otel-collector:4317
PROMETHEUS_PORT=9090
GRAFANA_PORT=3000
```

### 12.2.2 Docker Compose 配置

```yaml
# docker-compose.yml
version: '3.8'

services:
  # ==================== 基礎設施 ====================
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./infrastructure/postgresql/init.sql:/docker-entrypoint-initdb.d/init.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}"]
      interval: 10s
      timeout: 5s
      retries: 5

  chromadb:
    image: chromadb/chroma:latest
    ports:
      - "8000:8000"
    volumes:
      - chroma_data:/chroma/chroma
      - ./infrastructure/chromadb/config.yaml:/chroma/config.yaml
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/v1/heartbeat"]
      interval: 10s
      timeout: 5s
      retries: 5

  nats:
    image: nats:2.10-alpine
    command: ["--jetstream", "--store_dir", "/data"]
    ports:
      - "4222:4222"
      - "8225:8225"
    volumes:
      - nats_data:/data
      - ./infrastructure/nats/nats.conf:/nats.conf

  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]

  # ==================== Mock 服務 ====================
  mock-ad-api:
    build: ./mocks/ad-api
    ports:
      - "8081:8080"

  mock-hr-api:
    build: ./mocks/hr-api
    ports:
      - "8082:8080"

  # ==================== MCP Service ====================
  mcp-service:
    build:
      context: .
      dockerfile: Dockerfile.mcp
    ports:
      - "8083:8080"
    environment:
      - NATS_URL=${NATS_URL}
      - DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}
      - AUTH_API_KEY=${MCP_AUTH_API_KEY}
      - OTEL_ENDPOINT=${OTEL_ENDPOINT}
    depends_on:
      postgres:
        condition: service_healthy
      nats:
        condition: service_started
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/healthz"]
      interval: 10s
      timeout: 5s
      retries: 5

  # ==================== Agents ====================
  hr-agent:
    build:
      context: .
      dockerfile: Dockerfile.agent
    environment:
      - AGENT_ID=hr-agent-v1
      - AGENT_DOMAIN=human_resources
      - NATS_URL=${NATS_URL}
      - CHROMADB_URL=http://chromadb:8000
      - HR_API_URL=${HR_API_URL}
      - HR_API_TOKEN=${HR_API_TOKEN}
      - LLM_PROVIDER=ollama
      - LLM_MODEL=${LLM_MODEL}
      - OLLAMA_BASE_URL=${OLLAMA_BASE_URL}
      - OTEL_ENDPOINT=${OTEL_ENDPOINT}
    depends_on:
      ollama:
        condition: service_started
      chromadb:
        condition: service_healthy
      nats:
        condition: service_started
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/healthz"]
      interval: 10s
      timeout: 5s
      retries: 5

  it-agent:
    build:
      context: .
      dockerfile: Dockerfile.agent
    environment:
      - AGENT_ID=it-agent-v1
      - AGENT_DOMAIN=information_technology
      - NATS_URL=${NATS_URL}
      - CHROMADB_URL=http://chromadb:8000
      - AD_API_URL=${AD_API_URL}
      - AD_API_TOKEN=${AD_API_TOKEN}
      - LLM_PROVIDER=ollama
      - LLM_MODEL=${LLM_MODEL}
      - OLLAMA_BASE_URL=${OLLAMA_BASE_URL}
      - OTEL_ENDPOINT=${OTEL_ENDPOINT}
    depends_on:
      ollama:
        condition: service_started
      chromadb:
        condition: service_healthy
      nats:
        condition: service_started
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/healthz"]
      interval: 10s
      timeout: 5s
      retries: 5

  # ==================== CCA Agent ====================
  cca-agent:
    build:
      context: .
      dockerfile: Dockerfile.cca
    ports:
      - "8084:8080"
    environment:
      - NATS_URL=${NATS_URL}
      - DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}
      - MCP_SERVICE_URL=http://mcp-service:8080
      - LLM_PROVIDER=ollama
      - LLM_MODEL=${LLM_MODEL}
      - OLLAMA_BASE_URL=${OLLAMA_BASE_URL}
      - OTEL_ENDPOINT=${OTEL_ENDPOINT}
    depends_on:
      mcp-service:
        condition: service_healthy
      hr-agent:
        condition: service_healthy
      it-agent:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/healthz"]
      interval: 10s
      timeout: 5s
      retries: 5

  # ==================== Portal ====================
  portal-backend:
    build:
      context: .
      dockerfile: Dockerfile.portal-backend
    ports:
      - "8085:8080"
    environment:
      - CCA_AGENT_URL=http://cca-agent:8080
      - DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}
      - OTEL_ENDPOINT=${OTEL_ENDPOINT}
    depends_on:
      cca-agent:
        condition: service_healthy
      postgres:
        condition: service_healthy

  portal-frontend:
    build:
      context: ./portal/frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8085
      - NEXT_PUBLIC_WS_URL=ws://localhost:8085

  # ==================== 可觀測性 ====================
  otel-collector:
    image: otel/opentelemetry-collector-contrib:latest
    volumes:
      - ./monitoring/otel/otel-collector.yaml:/etc/otelcol-contrib/config.yaml
    ports:
      - "4317:4317"
      - "4318:4318"
      - "8888:8888"

  prometheus:
    image: prom/prometheus:latest
    ports:
      - "${PROMETHEUS_PORT}:9090"
    volumes:
      - ./monitoring/prometheus/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus

  grafana:
    image: grafana/grafana:latest
    ports:
      - "${GRAFANA_PORT}:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/grafana/dashboards:/var/lib/grafana/dashboards

volumes:
  postgres_data:
  chroma_data:
  nats_data:
  ollama_data:
  prometheus_data:
  grafana_data:
```

---

## 12.3 核心代碼實現

### 12.3.1 CCA Agent 入口

```python
# agents/cca/main.py
import asyncio
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .orchestrator import TaskOrchestrator
from .llm_client import OllamaClient
from .memory import PostgresMemory

app = FastAPI(title="CCA Agent", version="1.0.0")
logger = logging.getLogger("cca")

# 初始化組件
llm = OllamaClient(base_url="http://ollama:11434", model="llama3:70b")
memory = PostgresMemory(database_url="postgresql://...")
orchestrator = TaskOrchestrator(llm=llm, memory=memory)


class TaskRequest(BaseModel):
    content: str
    user_id: str
    session_id: str = None

class TaskResponse(BaseModel):
    task_id: str
    status: str
    result: str = None
    trace_id: str = None


@app.post("/task", response_model=TaskResponse)
async def create_task(request: TaskRequest):
    """接收用戶任務"""
    try:
        result = await orchestrator.execute(
            content=request.content,
            user_id=request.user_id,
            session_id=request.session_id
        )
        return TaskResponse(
            task_id=result.task_id,
            status=result.status,
            result=result.output,
            trace_id=result.trace_id
        )
    except Exception as e:
        logger.error(f"任務執行失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/healthz")
async def health_check():
    return {"status": "healthy"}
```

### 12.3.2 CCA 任務編排器

```python
# agents/cca/orchestrator.py
import uuid
import time
from opentelemetry import trace

tracer = trace.get_tracer("cca.orchestrator")

class TaskOrchestrator:
    """CCA 的任務編排器"""

    def __init__(self, llm, memory):
        self.llm = llm
        self.memory = memory

    async def execute(self, content: str, user_id: str, session_id: str = None):
        """執行一個用戶任務"""
        task_id = str(uuid.uuid4())

        with tracer.start_as_current_span(f"task.{task_id}") as span:
            span.set_attribute("task.id", task_id)
            span.set_attribute("user.id", user_id)

            # 1. 理解用戶意圖
            intent = await self._parse_intent(content, user_id)
            span.set_attribute("task.intent", intent.type)

            # 2. 制定執行計劃
            plan = await self._create_plan(intent)
            span.set_attribute("task.steps", len(plan.steps))

            # 3. 執行計劃
            results = []
            for step in plan.steps:
                with tracer.start_as_current_span(f"step.{step.name}") as step_span:
                    result = await self._execute_step(step)
                    results.append(result)
                    step_span.set_attribute("step.success", result.success)

            # 4. 返回結果
            output = self._format_results(results)
            span.set_attribute("task.status", "completed")

            return TaskResult(
                task_id=task_id,
                status="completed",
                output=output,
                trace_id=span.get_span_context().trace_id
            )

    async def _parse_intent(self, content: str, user_id: str):
        """解析用戶意圖"""
        prompt = f"""分析以下用戶請求，提取關鍵信息：

用戶請求：{content}

請返回 JSON 格式的意圖分析：
{{
  "type": "task_type",
  "employee_name": "員工姓名",
  "department": "部門",
  "role": "職位",
  "urgency": "high/medium/low"
}}
"""
        response = await self.llm.generate(prompt)
        return self._parse_json_response(response)

    async def _create_plan(self, intent):
        """創建執行計劃"""
        if intent.type == "new_employee_onboarding":
            return Plan(steps=[
                Step(name="hr_query", tool="hr_agent_query_employee",
                     args={"employee_name": intent.employee_name}),
                Step(name="hr_create", tool="hr_agent_create_employee",
                     args={"employee_name": intent.employee_name,
                           "department": intent.department,
                           "role": intent.role}),
                Step(name="it_create_ad", tool="it_agent_create_ad_account",
                     args={"username": self._generate_username(intent.employee_name),
                           "display_name": intent.employee_name,
                           "department": intent.department,
                           "role": intent.role}),
                Step(name="it_configure", tool="it_agent_configure_permissions",
                     args={"department": intent.department, "role": intent.role}),
                Step(name="it_notify", tool="it_agent_send_notification",
                     args={"recipient": f"{self._generate_username(intent.employee_name)}@company.com",
                           "template": "welcome_email"}),
            ])
        raise ValueError(f"不支持的任務類型: {intent.type}")

    async def _execute_step(self, step):
        """執行單個步驟"""
        # 調用 MCP Service 執行工具
        result = await mcp_client.call_tool(
            name=step.tool,
            arguments=step.args
        )
        return StepResult(
            name=step.name,
            success=result.is_error,
            output=result.content
        )
```

### 12.3.3 IT Agent 實現

```python
# agents/it_agent/main.py
import asyncio
import logging
from fastapi import FastAPI
from .tools import ITAgentTools
from .prompt import IT_AGENT_SYSTEM_PROMPT

app = FastAPI(title="IT Agent", version="1.0.0")
logger = logging.getLogger("it_agent")

tools = ITAgentTools()


@app.post("/tool/{tool_name}")
async def call_tool(tool_name: str, arguments: dict):
    """調用 IT Agent 的工具"""
    try:
        if tool_name == "create_ad_account":
            result = await tools.create_ad_account(arguments)
        elif tool_name == "configure_permissions":
            result = await tools.configure_permissions(arguments)
        elif tool_name == "send_notification":
            result = await tools.send_notification(arguments)
        else:
            return {"error": f"未知工具: {tool_name}"}

        return {"result": result, "success": True}
    except Exception as e:
        logger.error(f"工具調用失敗: {tool_name}: {e}")
        return {"error": str(e), "success": False}


@app.get("/healthz")
async def health_check():
    return {"status": "healthy", "agent_id": "it-agent-v1"}
```

```python
# agents/it_agent/tools.py
import httpx
import logging

logger = logging.getLogger("it_agent.tools")


class ITAgentTools:
    """IT Agent 的工具集"""

    def __init__(self):
        self.ad_api_url = "http://mock-ad-api:8080"
        self.hr_api_url = "http://mock-hr-api:8080"

    async def create_ad_account(self, args: dict) -> dict:
        """創建 AD 賬戶"""
        username = args.get("username")
        display_name = args.get("display_name")
        department = args.get("department")
        role = args.get("role")

        # 生成臨時密碼
        import secrets
        temp_password = f"Temp@{secrets.token_hex(4)}"

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.ad_api_url}/v1/accounts",
                json={
                    "username": username,
                    "display_name": display_name,
                    "department": department,
                    "role": role,
                    "temp_password": temp_password
                },
                timeout=30.0
            )
            response.raise_for_status()
            result = response.json()

            return {
                "account_id": result["account_id"],
                "email": result["email"],
                "temp_password": temp_password,
                "message": f"已成功為 {display_name} 創建 AD 賬戶"
            }

    async def configure_permissions(self, args: dict) -> dict:
        """配置權限"""
        department = args.get("department")
        role = args.get("role")

        # 根據部門和角色配置權限組
        groups = self._get_default_groups(department, role)

        return {
            "groups_assigned": groups,
            "message": f"已配置 {len(groups)} 個權限組"
        }

    async def send_notification(self, args: dict) -> dict:
        """發送通知"""
        recipient = args.get("recipient")
        template = args.get("template")

        # 發送歡迎郵件
        return {
            "message": f"已向 {recipient} 發送 {template} 郵件",
            "success": True
        }

    def _get_default_groups(self, department: str, role: str) -> list:
        """獲取默認權限組"""
        base_groups = ["General Users", "Domain Users"]

        dept_groups = {
            "市場部": ["Marketing Team", "Marketing Content"],
            "技術部": ["Engineering Team", "Dev Access"],
            "產品部": ["Product Team", "Analytics Access"],
            "行政部": ["Admin Team", "Office Access"]
        }

        return base_groups + dept_groups.get(department, [])
```

---

## 12.4 Mock 服務

### 12.4.1 Mock AD API

```python
# mocks/ad-api/main.py
from fastapi import FastAPI
from pydantic import BaseModel
import uuid

app = FastAPI(title="Mock AD API")

# 模擬存儲
accounts_db = {}


class CreateAccountRequest(BaseModel):
    username: str
    display_name: str
    department: str
    role: str
    temp_password: str


@app.post("/v1/accounts")
async def create_account(request: CreateAccountRequest):
    """模擬創建 AD 賬戶"""
    account_id = str(uuid.uuid4())
    email = f"{request.username}@company.com"

    accounts_db[account_id] = {
        "account_id": account_id,
        "username": request.username,
        "display_name": request.display_name,
        "department": request.department,
        "role": request.role,
        "email": email,
        "temp_password": request.temp_password
    }

    return {
        "account_id": account_id,
        "email": email,
        "message": f"賬戶 {request.username} 已創建"
    }


@app.get("/v1/check-username/{username}")
async def check_username(username: str):
    """檢查用戶名是否可用"""
    taken = any(a["username"] == username for a in accounts_db.values())
    return {"available": not taken}


@app.get("/v1/accounts/{account_id}")
async def get_account(account_id: str):
    """獲取賬戶信息"""
    if account_id not in accounts_db:
        return {"error": "Account not found"}
    return accounts_db[account_id]


@app.get("/healthz")
async def health():
    return {"status": "healthy"}
```

---

## 12.5 快速啟動指南

### 12.5.1 前置條件

```bash
# 系統要求
- Docker Desktop 4.0+
- Docker Compose V2
- NVIDIA Container Toolkit（如需 GPU 加速）
- 至少 16GB RAM
- 至少 50GB 磁盤空間

# 安裝 Ollama 模型
docker compose exec ollama ollama pull llama3:70b
```

### 12.5.2 啟動步驟

```bash
# 1. Clone 項目
git clone https://github.com/your-org/ai-agent-platform.git
cd ai-agent-platform

# 2. 複製環境變量
cp .env.example .env

# 3. 啟動所有服務
docker compose up -d

# 4. 等待服務就緒
docker compose ps  # 確認所有服務 healthy

# 5. 訪問 Portal
open http://localhost:3000

# 6. 測試 API
curl -X POST http://localhost:8084/task \
  -H "Content-Type: application/json" \
  -d '{
    "content": "新員工張小明明天入職市場部擔任產品經理",
    "user_id": "hr_manager_001"
  }'
```

### 12.5.3 驗證服務

```bash
# 檢查各服務健康狀態
curl http://localhost:8080/healthz   # MCP Service
curl http://localhost:8083/healthz   # HR Agent
curl http://localhost:8084/healthz   # IT Agent
curl http://localhost:8085/healthz   # CCA Agent
curl http://localhost:8086/healthz   # Portal Backend

# 查看服務日誌
docker compose logs -f cca-agent
docker compose logs -f it-agent
docker compose logs -f hr-agent
```

---

## 12.6 進階擴展

### 12.6.1 從 MVP 到生產

完成 MVP 體驗後，可以按照以下路徑逐步擴展：

| 階段 | 變更 | 說明 |
|------|------|------|
| **添加 HR Agent** | 啟用 hr-agent 服務 | 完整的入職流程 |
| **添加 RAG** | 上傳政策文檔到 ChromaDB | Agent 能查詢知識庫 |
| **添加審計** | 啟用 PostgreSQL | 操作日誌持久化 |
| **添加監控** | 啟用 OTel + Grafana | 可觀測性 |
| **K8s 部署** | 遷移到 K8s | 生產級部署 |

### 12.6.2 自定義 Agent

```python
# 添加一個新的自定義 Agent
# 1. 創建 Agent 目錄
# 2. 實現工具集
# 3. 設計系統提示
# 4. 在 MCP Service 註冊
# 5. 更新 Docker Compose

# 示例：財務 Agent
class FinanceAgentTools:
    async def submit_expense_report(self, args: dict) -> dict:
        """提交報銷單"""
        # 實現報銷邏輯
        return {"report_id": "EXP-001", "status": "submitted"}

    async def query_budget(self, args: dict) -> dict:
        """查詢預算"""
        return {"budget_remaining": 50000, "currency": "TWD"}
```

---

## 12.7 Agent 系統提示（Prompt.py）

### 12.7.1 IT Agent 系統提示

```python
# agents/it_agent/prompt.py

IT_AGENT_SYSTEM_PROMPT = """你是 IT 部門的 AI Agent，專門負責 IT 資源管理。

## 身份與職責
- 你的名字是 IT Bot，隸屬於 IT 部門
- 你負責管理 AD（Active Directory）賬戶、配置權限、發送通知
- 你只能執行 IT 相關的操作，不處理 HR 業務

## 工具使用規範
1. 創建 AD 賬戶前，必須先檢查用戶名是否可用
2. 創建賬戶後，立即返回臨時密碼（用戶需要第一次登入時修改）
3. 配置權限時，遵循最小權限原則
4. 每次操作完成後，都要記錄操作結果

## 安全約束
- 不得刪除或修改非請求的賬戶
- 臨時密碼不能出現在日誌中
- 不得將用戶密碼透過不安全的通道傳輸
- 發現異常操作時，立即通知管理員

## 回應格式
所有回應都使用 JSON 格式：
{
  "status": "success" | "error",
  "data": { ... },
  "message": "操作說明",
  "warnings": ["可選的警告信息"]
}

## 常見場景
1. 新員工入職：創建 AD 賬戶 → 配置權限 → 發送歡迎郵件
2. 員工轉部門：更新權限組 → 通知相關人員
3. 員工離職：禁用賬戶 → 備份數據 → 回收資源
"""

HR_AGENT_SYSTEM_PROMPT = """你是 HR 部門的 AI Agent，專門負責人力資源管理。

## 身份與職責
- 你的名字是 HR Bot，隸屬於 HR 部門
- 你負責管理員工信息、處理入職/離職流程、回答政策問題
- 你只能執行 HR 相關的操作，不處理 IT 業務

## 工具使用規範
1. 查詢員工信息時，先驗證請求者權限
2. 創建員工記錄時，確保信息完整且準確
3. 處理入職流程時，按照標準步驟執行
4. 所有操作都要記錄審計日誌

## 數據隱私
- 員工薪資信息僅限授權人員訪問
- 不得在回應中暴露敏感個人信息
- 遵守 GDPR 和本地數據保護法規
- 定期清理過期的臨時數據

## 回應格式
所有回應都使用 JSON 格式：
{
  "status": "success" | "error",
  "data": { ... },
  "message": "操作說明",
  "audit_log": { "action": "...", "timestamp": "..." }
}

## 入職流程步驟
1. 創建員工記錄（姓名、部門、職位、入職日期）
2. 分配員工編號
3. 設置薪資方案
4. 安排入職培訓
5. 通知相關部門
"""
```

### 12.7.2 CCA 提示模板

```python
# agents/cca/prompt.py

CCA_SYSTEM_PROMPT = """你是企業級 AI Agent 協同平台的核心控制 Agent（CCA）。

## 核心職責
1. 理解用戶意圖，將複雜任務分解為多個子任務
2. 協調 HR Agent 和 IT Agent 完成具體操作
3. 確保任務按正確順序執行，處理異常情況
4. 匯總所有子任務結果，提供統一的用戶體驗

## 協作規範
- HR 相關操作：調用 hr_agent_* 系列工具
- IT 相關操作：調用 it_agent_* 系列工具
- 跨部門任務：先執行 HR 操作（如果涉及員工創建），再執行 IT 操作

## 任務編排邏輯
對於新員工入職任務，標準流程為：
1. 查詢 HR 系統確認員工信息
2. 在 HR 系統創建員工記錄
3. 在 AD 中創建賬戶
4. 配置 IT 權限
5. 發送歡迎通知

## 異常處理
- 如果某個步驟失敗，記錄錯誤並繼續執行後續不依賴該步驟的操作
- 如果關鍵步驟（如員工創建）失敗，終止整個流程並返回錯誤
- 所有異常都要記錄到 OpenTelemetry Trace

## 回應格式
最終回應必須包含：
- 任務執行狀態（成功/部分成功/失敗）
- 每個子步驟的執行結果
- 需要用戶關注的項目（如臨時密碼）
"""
```

---

## 12.8 LLM 客戶端實現

### 12.8.1 Ollama 客戶端

```python
# agents/cca/llm_client.py
import httpx
import json
import logging
from opentelemetry import trace

tracer = trace.get_tracer("cca.llm")
logger = logging.getLogger("cca.llm")


class OllamaClient:
    """Ollama LLM 客戶端"""

    def __init__(self, base_url: str = "http://ollama:11434", model: str = "llama3:70b"):
        self.base_url = base_url
        self.model = model
        self.client = httpx.AsyncClient(base_url=base_url, timeout=120.0)

    async def generate(self, prompt: str, system_prompt: str = None) -> str:
        """生成文本回應"""
        with tracer.start_as_current_span("llm.generate") as span:
            span.set_attribute("llm.model", self.model)
            span.set_attribute("llm.prompt_length", len(prompt))

            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            try:
                response = await self.client.post(
                    "/api/chat",
                    json={
                        "model": self.model,
                        "messages": messages,
                        "stream": False,
                        "options": {
                            "temperature": 0.2,
                            "num_predict": 2048,
                            "top_p": 0.9
                        }
                    }
                )
                response.raise_for_status()
                result = response.json()

                content = result["message"]["content"]
                span.set_attribute("llm.response_length", len(content))
                span.set_attribute("llm.total_duration_ms", result.get("total_duration", 0) / 1_000_000)

                return content

            except httpx.HTTPStatusError as e:
                span.set_status(trace.StatusCode.ERROR, str(e))
                logger.error(f"LLM 請求失敗: {e}")
                raise

    async def generate_stream(self, prompt: str, system_prompt: str = None):
        """流式生成文本"""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        async with self.client.stream(
            "POST",
            "/api/chat",
            json={
                "model": self.model,
                "messages": messages,
                "stream": True
            }
        ) as response:
            async for line in response.aiter_lines():
                if line:
                    chunk = json.loads(line)
                    if "message" in chunk:
                        yield chunk["message"]["content"]

    async def close(self):
        await self.client.aclose()
```

---

## 12.9 知識庫初始化腳本

### 12.9.1 知識庫構建器

```python
# knowledge/base_builder.py
import chromadb
import os
import yaml
from pathlib import Path

class KnowledgeBaseBuilder:
    """知識庫構建器"""

    def __init__(self, chromadb_url: str = "http://chromadb:8000"):
        self.client = chromadb.HttpClient(host=chromadb_url)

    def seed_hr_policies(self):
        """初始化 HR 政策文檔"""
        collection = self.client.get_or_create_collection(
            name="hr_policies",
            metadata={"hnsw:space": "cosine"}
        )

        hr_docs = [
            {
                "id": "onboarding_v1",
                "document": """# 新員工入職流程

## 流程步驟
1. HR 創建員工記錄（姓名、部門、職位、入職日期）
2. 分配員工編號（格式：EMP-YYYYMMDD-XXX）
3. 設置薪資方案（根據職位和部門）
4. IT 部門創建 AD 賬戶
5. 配置相關權限組
6. 發送歡迎郵件（包含臨時密碼和入職指南）
7. 安排入職培訓

## 所需文件
- 身份證复印件
- 學歷證明
- 離職證明（如適用）
- 銀行賬戶信息

## 注意事項
- 入職日期前 3 天完成所有系統配置
- 臨時密碼有效期為 7 天
- 新員工必須在 30 天內完成安全培訓""",
                "metadata": {"category": "hr", "topic": "onboarding", "version": "1.0"}
            },
            {
                "id": "leave_policy_v1",
                "document": """# 請假政策

## 假期類型
1. 年假：15 天/年（入职滿一年後）
2. 病假：帶薪病假 30 天/年
3. 事假：無薪，需提前 3 天申請
4. 婚假：10 天
5. 產假/陪產假：依當地法規

## 申請流程
1. 透過 HR 系統提交請假申請
2. 直屬主管審批
3. HR 確認並記錄
4. 超過 3 天需部門經理審批

## 注意事項
- 年假可跨年使用，但不得超過 2 天
- 病假需提供醫療證明
- 連續請假超過 5 天需提前 1 週申請""",
                "metadata": {"category": "hr", "topic": "leave", "version": "1.0"}
            }
        ]

        for doc in hr_docs:
            collection.upsert(
                ids=[doc["id"]],
                documents=[doc["document"]],
                metadatas=[doc["metadata"]]
            )
        print(f"✅ 已初始化 {len(hr_docs)} 個 HR 政策文檔")

    def seed_it_knowledge(self):
        """初始化 IT 知識庫"""
        collection = self.client.get_or_create_collection(
            name="it_knowledge",
            metadata={"hnsw:space": "cosine"}
        )

        it_docs = [
            {
                "id": "ad_account_guide",
                "document": """# AD 賬戶管理指南

## 賬戶創建流程
1. 檢查用戶名是否可用（格式：姓氏+名字首字母，如 zhangxm）
2. 創建 AD 賬戶（ OU 根據部門自動分配）
3. 設置臨時密碼（必須包含大小寫字母和數字）
4. 配置密碼策略（90 天過期，歷史 12 次不重複）
5. 啟用 MFA（多因素認證）

## 權限組分配
- 通用用戶組：Domain Users, General Access
- 部門特定組：根據部門自動分配
- 角色特定組：根據職位分配（如經理組、主管組）

## 常見問題
1. 用戶名衝突：使用 中間名首字母 或 數字後綴
2. 密碼重置：透過 IT Service Desk 申請
3. 賬戶鎖定：連續 5 次密碼錯誤後鎖定 30 分鐘""",
                "metadata": {"category": "it", "topic": "ad_account", "version": "1.0"}
            }
        ]

        for doc in it_docs:
            collection.upsert(
                ids=[doc["id"]],
                documents=[doc["document"]],
                metadatas=[doc["metadata"]]
            )
        print(f"✅ 已初始化 {len(it_docs)} 個 IT 知識文檔")

    def seed_all(self):
        """初始化所有知識庫"""
        print("🚀 開始初始化知識庫...")
        self.seed_hr_policies()
        self.seed_it_knowledge()
        print("✅ 知識庫初始化完成")


if __name__ == "__main__":
    builder = KnowledgeBaseBuilder()
    builder.seed_all()
```

### 12.9.2 Docker 啟動腳本

```bash
#!/bin/bash
# scripts/seed_knowledge.sh

echo "等待 ChromaDB 啟動..."
until curl -s http://chromadb:8000/api/v1/heartbeat > /dev/null 2>&1; do
  sleep 2
done

echo "初始化知識庫..."
python -m knowledge.base_builder

echo "驗證知識庫..."
curl -s http://chromadb:8000/api/v1/collections | python -m json.tool

echo "✅ 知識庫準備就緒"
```

---

## 12.10 測試腳本

### 12.10.1 端對端測試

```python
# tests/test_e2e_onboarding.py
import pytest
import httpx
import asyncio
import time

MCP_URL = "http://localhost:8083"
CCA_URL = "http://localhost:8084"
API_KEY = "your-api-key"


@pytest.fixture
def client():
    return httpx.AsyncClient(timeout=60.0)


@pytest.mark.asyncio
async def test_complete_onboarding_flow(client):
    """測試完整的新員工入職流程"""
    # 1. 發送入職請求
    response = await client.post(
        f"{CCA_URL}/task",
        json={
            "content": "新員工李小華明天入職技術部擔任軟體工程師",
            "user_id": "hr_manager_001"
        },
        headers={"Authorization": f"Bearer {API_KEY}"}
    )
    assert response.status_code == 200
    result = response.json()
    task_id = result["task_id"]

    # 2. 等待任務完成（最多 60 秒）
    for _ in range(60):
        status_resp = await client.get(
            f"{CCA_URL}/task/{task_id}",
            headers={"Authorization": f"Bearer {API_KEY}"}
        )
        status = status_resp.json()["status"]
        if status in ["completed", "failed"]:
            break
        await asyncio.sleep(1)

    # 3. 驗證結果
    assert status == "completed"
    assert "AD 賬戶已創建" in result.get("result", "") or "已成功" in result.get("result", "")


@pytest.mark.asyncio
async def test_tool_discovery(client):
    """測試工具發現功能"""
    response = await client.get(
        f"{MCP_URL}/mcp/tools/list",
        headers={"Authorization": f"Bearer {API_KEY}"}
    )
    assert response.status_code == 200
    tools = response.json()["tools"]
    tool_names = [t["name"] for t in tools]
    assert "hr_agent_create_employee" in tool_names
    assert "it_agent_create_ad_account" in tool_names


@pytest.mark.asyncio
async def test_agent_health(client):
    """測試所有 Agent 健康狀態"""
    services = [
        ("MCP Service", f"{MCP_URL}/healthz"),
        ("CCA Agent", f"{CCA_URL}/healthz"),
    ]
    for name, url in services:
        response = await client.get(url)
        assert response.status_code == 200, f"{name} 健康檢查失敗"
        assert response.json()["status"] == "healthy"


@pytest.mark.asyncio
async def test_concurrent_requests(client):
    """測試併發處理能力"""
    async def submit_task(i):
        return await client.post(
            f"{CCA_URL}/task",
            json={
                "content": f"測試員工_{i}入職市場部",
                "user_id": f"test_user_{i}"
            },
            headers={"Authorization": f"Bearer {API_KEY}"}
        )

    # 併發發送 5 個請求
    tasks = [submit_task(i) for i in range(5)]
    responses = await asyncio.gather(*tasks)

    # 驗證所有請求都被接受
    for resp in responses:
        assert resp.status_code == 200
```

### 12.10.2 性能測試

```python
# tests/performance/test_load.py
import asyncio
import httpx
import time
from statistics import mean, median

CCA_URL = "http://localhost:8084"
API_KEY = "your-api-key"


async def measure_task_latency(client, task_id: int) -> dict:
    """測量單個任務的延遲"""
    start = time.time()

    response = await client.post(
        f"{CCA_URL}/task",
        json={
            "content": f"性能測試員工_{task_id}入職技術部",
            "user_id": f"perf_user_{task_id}"
        },
        headers={"Authorization": f"Bearer {API_KEY}"}
    )

    latency = time.time() - start
    return {
        "task_id": task_id,
        "status_code": response.status_code,
        "latency_ms": latency * 1000
    }


async def run_load_test(num_concurrent: int = 10, num_total: int = 50):
    """執行負載測試"""
    print(f"🚀 開始負載測試: {num_total} 個任務, {num_concurrent} 併發")

    async with httpx.AsyncClient(timeout=120.0) as client:
        semaphore = asyncio.Semaphore(num_concurrent)

        async def limited_task(task_id):
            async with semaphore:
                return await measure_task_latency(client, task_id)

        start_time = time.time()
        results = await asyncio.gather(*[limited_task(i) for i in range(num_total)])
        total_time = time.time() - start_time

    # 統計分析
    latencies = [r["latency_ms"] for r in results]
    success_count = sum(1 for r in results if r["status_code"] == 200)

    print("\n📊 負載測試結果:")
    print(f"  總任務數: {num_total}")
    print(f"  成功率: {success_count}/{num_total} ({success_count/num_total*100:.1f}%)")
    print(f"  總耗時: {total_time:.2f}s")
    print(f"  平均延遲: {mean(latencies):.0f}ms")
    print(f"  中位數延遲: {median(latencies):.0f}ms")
    print(f"  最大延遲: {max(latencies):.0f}ms")
    print(f" 吞吐量: {num_total/total_time:.2f} tasks/sec")

    return results


if __name__ == "__main__":
    asyncio.run(run_load_test())
```

### 12.10.3 快速驗證腳本

```bash
#!/bin/bash
# scripts/verify_setup.sh

echo "🔍 驗證平台設置..."

# 1. 檢查 Docker 服務
echo "1. 檢查 Docker 服務狀態..."
docker compose ps --format json | python -c "
import sys, json
for line in sys.stdin:
    svc = json.loads(line)
    status = '✅' if svc['State'] == 'running' else '❌'
    print(f'  {status} {svc[\"Service\"]}: {svc[\"State\"]}')
"

# 2. 測試 API 端點
echo ""
echo "2. 測試 API 端點..."
endpoints=(
    "MCP Service|http://localhost:8083/healthz"
    "CCA Agent|http://localhost:8084/healthz"
    "Portal|http://localhost:3000"
)

for endpoint in "${endpoints[@]}"; do
    IFS='|' read -r name url <<< "$endpoint"
    if curl -sf "$url" > /dev/null 2>&1; then
        echo "  ✅ $name: reachable"
    else
        echo "  ❌ $name: unreachable"
    fi
done

# 3. 測試完整流程
echo ""
echo "3. 測試完整入職流程..."
response=$(curl -s -X POST http://localhost:8084/task \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-api-key" \
  -d '{"content": "測試員工入職", "user_id": "test"}')

if echo "$response" | grep -q "task_id"; then
    echo "  ✅ 任務提交成功"
    task_id=$(echo "$response" | python -c "import sys, json; print(json.load(sys.stdin)['task_id'])")
    echo "  📋 Task ID: $task_id"
else
    echo "  ❌ 任務提交失敗"
fi

# 4. 查看 Grafana
echo ""
echo "4. 可觀測性端點:"
echo "  📊 Grafana: http://localhost:3000 (admin/admin)"
echo "  📈 Prometheus: http://localhost:9090"
echo "  🔍 OTel Collector: http://localhost:8888"

echo ""
echo "✅ 驗證完成！"
```

---

## 本章小結

本章提供了一個完整的、可運行的 MVP 參考實作：

- **項目結構**：清晰的模塊化設計，每個組件獨立可測試
- **Docker Compose**：一鍵啟動所有服務，包含 Mock 服務
- **核心代碼**：CCA、IT Agent、HR Agent、MCP Service 的完整實現
- **Agent 提示**：IT 和 HR Agent 的完整系統提示模板
- **LLM 客戶端**：Ollama 客戶端實現，支持同步和流式生成
- **知識庫**：HR 政策和 IT 知識文檔的初始化腳本
- **Mock 服務**：模擬 AD API 和 HR API，無需真實企業系統
- **測試腳本**：端對端測試、性能測試、快速驗證腳本
- **快速啟動**：5 分鐘內跑通整個流程
- **擴展路徑**：從 MVP 到生產環境的清晰路徑

---

## 延伸閱讀

1. **GitHub: ai-agent-platform** — 本章的完整參考代碼。
2. **Letta Documentation** — https://docs.letta.com/ — Agent 框架文檔。
3. **LangGraph Documentation** — https://langchain-ai.github.io/langgraph/ — 工作流編排。
4. **《Building Microservices》** — Sam Newman, O'Reilly. 微服務架構經典。
5. **《Docker Deep Dive》** — Nigel Poulton. Docker 實戰指南。

---

# 全書結語

恭喜你讀完了這本書！

從第一章的「為什麼需要 AI Agent 平台」，到第十二章的「完整 MVP 參考實作」，我們一起走過了一段完整的旅程：

- **設計思維**：CCA + Specialized Agents 的雙層架構
- **核心組件**：MCP Service、RAG 知識庫、OpenTelemetry
- **雲原生部署**：Kubernetes、Istio、Helm Charts
- **實踐指南**：四階段實施路線圖，從 MVP 到生產

記住：**好的架構是演進出來的**。不要試圖一步到位，先跑通，再優化，最後擴展。

祝你在 AI Agent 平台的構建之路上一切順利！

—— 作者
