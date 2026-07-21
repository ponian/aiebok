# 第五章：CCA 實現細節 — 中央協調 Agent 的設計與實踐

> 「CCA 不只是一個 LLM 調用器，它是一個完整的認知系統 — 感知意圖、規劃行動、協調資源、整合結果、從經驗中學習。」

第二章從宏觀角度定義了 CCA 的七大核心職責。本章將這些職責轉化為可運行的代碼：CCA 的完整生命週期、Prompt 工程的實踐細節、LangGraph 工作流的具體實現，以及狀態管理與錯誤處理機制。

---

## 5.1 CCA 的整體架構

### 5.1.1 CCA 作為一個 Letta Agent

CCA 本身也是一個 Letta Agent，但它與 Specialized Agents 有本質區別：CCA 不直接執行業務操作，而是作為**認知中樞**協調其他 Agent。以下是 CCA 的核心類定義：

```python
# cca/core.py
from letta import Agent, Tool
from opentelemetry import trace, metrics
from typing import Optional
import json

tracer = trace.get_tracer("cca-agent")
meter = metrics.get_meter("cca-agent")

# CCA 特有的工具集 — 不包含任何業務操作
@Tool
def query_agent_registry(capability: str) -> list[dict]:
    """查詢 Agent Registry，找到具備特定能力的 Agent 列表。

    Args:
        capability: 要查詢的能力名稱，如 'create_ad_account'
    Returns:
        具備該能力的 Agent 列表，包含 agent_id、版本、SLA 信息
    """
    # 實際實現會調用 Agent Registry 服務
    pass

@Tool
def send_task_to_agent(
    agent_id: str,
    task_description: str,
    inputs: dict,
    context: dict
) -> dict:
    """通過 MCP Service 向指定 Agent 發送任務。

    Args:
        agent_id: 目標 Agent 的 ID
        task_description: 任務的自然語言描述
        inputs: 結構化的輸入參數
        context: 需要傳遞的上下文信息
    Returns:
        Agent 返回的結構化結果
    """
    pass

@Tool
def request_human_confirmation(
    reason: str,
    proposed_plan: dict
) -> dict:
    """向用戶請求確認（信心度不足或涉及敏感操作時）。

    Args:
        reason: 需要確認的原因
        proposed_plan: 提議的任務計劃
    Returns:
        用戶的確認結果
    """
    pass

@Tool
def query_knowledge_base(query: str, context: dict = None) -> str:
    """查詢企業知識庫，獲取政策、SOP 等信息。

    Args:
        query: 查詢內容
        context: 額外上下文（部門、角色等）
    Returns:
        相關知識片段
    """
    pass

# CCA 的系統提示（結構化 Prompt）
CCA_SYSTEM_PROMPT = """你是一個企業級 AI Native Agent Platform 的中央協調 Agent（CCA）。

## 你的角色
你負責理解用戶的業務請求，將其分解為可執行的子任務，並調度合適的 Specialized Agent 來完成這些任務。
你不直接執行任何業務操作 — 你的價值在於「想清楚」而非「動手做」。

## 你可用的工具
1. `query_agent_registry`: 查詢具備特定能力的 Agent
2. `send_task_to_agent`: 向 Agent 發送任務
3. `request_human_confirmation`: 向用戶請求確認
4. `query_knowledge_base`: 查詢企業知識庫

## 決策流程
1. **理解意圖**：分析用戶請求的核心目的
2. **識別實體**：提取關鍵信息（人名、部門、時間、資源等）
3. **檢查完整性**：如果關鍵信息缺失，使用 `request_human_confirmation` 向用戶澄清
4. **查詢能力**：使用 `query_agent_registry` 確認可用的 Agent
5. **分解任務**：將複雜任務分解為子任務序列
6. **執行計劃**：按依賴順序向 Agent 發送任務
7. **整合結果**：整合所有 Agent 的返回結果，生成統一響應

## 約束條件
- 你不直接執行任何業務操作（不能創建賬號、不能發送郵件等）
- 每個決策都必須輸出推理過程（用於審計）
- 當信心度低於 0.75 時，必須向用戶確認
- 涉及敏感操作（刪除、權限變更、批量操作）時，必須要求用戶明確確認
- 遇到錯誤時，先嘗試替代方案，再向用戶報告

## 輸出格式
始終以結構化格式輸出你的決策，包含：
- intent: 識別到的意圖
- confidence: 信心度（0.0-1.0）
- reasoning: 你的推理過程（用於審計）
- task_plan: 子任務列表（如有）
"""

class CCACore:
    """CCA 的核心實現"""

    def __init__(self, llm_config: dict, agent_registry, mcp_client, knowledge_base):
        self.llm_config = llm_config
        self.registry = agent_registry
        self.mcp = mcp_client
        self.kb = knowledge_base

        # 初始化 Letta Agent
        self.agent = Agent(
            name="Central Coordinator Agent",
            system=CCA_SYSTEM_PROMPT,
            tools=[
                query_agent_registry,
                send_task_to_agent,
                request_human_confirmation,
                query_knowledge_base
            ],
            persistence_config={
                "type": "postgres",
                "host": "postgres-service",
                "port": 5432,
                "database": "letta_agents",
                "table_prefix": "cca_"
            }
        )

    async def process_request(self, user_input: str, user_context: dict) -> dict:
        """處理用戶請求的完整流程"""
        with tracer.start_as_current_span("cca.process_request") as span:
            span.set_attribute("user_id", user_context.get("user_id", "unknown"))
            span.set_attribute("input_length", len(user_input))

            # 1. 調用 LLM 進行意圖識別與任務規劃
            with tracer.start_as_current_span("cca.llm_reasoning"):
                response = await self.agent.step(
                    user_message=user_input,
                    max_steps=15  # CCA 可能需要多步推理
                )

            # 2. 記錄審計日誌
            audit_record = self._create_audit_record(
                user_input, response, user_context
            )
            await self._store_audit(audit_record)

            # 3. 返回結果
            return {
                "response": response.content,
                "task_results": response.tool_results,
                "usage": response.usage,
                "audit_id": audit_record["audit_id"]
            }
```

### 5.1.2 CCA 與 Specialized Agents 的關鍵區別

| 維度 | CCA | Specialized Agents |
|------|-----|-------------------|
| **工具集** | 只包含協調類工具（查詢、發送、確認） | 包含業務操作工具（創建賬號、查詢數據） |
| **Prompt** | 強調推理過程輸出、決策透明性 | 強調領域專業知識、操作準確性 |
| **LLM** | 使用最強模型（Claude 3.5 Sonnet） | 使用本地模型（Llama 3 70B） |
| **步數限制** | 較高（15 步），因為需要多輪推理 | 較低（10 步），任務相對直接 |
| **審計要求** | 每個決策都記錄完整推理過程 | 記錄操作結果即可 |

---

## 5.2 意圖識別與任務分解

### 5.2.1 意圖識別的 Prompt 設計

CCA 的意圖識別不是簡單的分類問題，而是需要理解上下文、識別缺失信息、評估信心度的複雜認知過程：

```python
# cca/intent_parser.py

INTENT_SCHEMA = {
    "type": "object",
    "properties": {
        "intent": {
            "type": "string",
            "enum": [
                "create_it_account",
                "reset_password",
                "modify_permissions",
                "query_employee_info",
                "onboard_new_hire",
                "offboard_employee",
                "unknown"
            ]
        },
        "confidence": {
            "type": "number",
            "minimum": 0.0,
            "maximum": 1.0
        },
        "entities": {
            "type": "object",
            "properties": {
                "employee_name": {"type": "string"},
                "department": {"type": "string"},
                "role": {"type": "string"},
                "action_detail": {"type": "string"}
            }
        },
        "missing_info": {
            "type": "array",
            "items": {"type": "string"}
        },
        "reasoning": {
            "type": "string",
            "description": "CCA 的推理過程（用於審計）"
        }
    },
    "required": ["intent", "confidence", "reasoning"]
}

async def parse_intent(cca_agent, user_input: str, context: dict) -> dict:
    """使用 CCA Agent 解析用戶意圖"""

    prompt = f"""分析以下用戶請求，識別意圖和實體。

用戶請求：「{user_input}」

當前上下文：
- 用戶角色：{context.get('user_role', 'unknown')}
- 部門：{context.get('department', 'unknown')}
- 時間：{context.get('timestamp', 'unknown')}

請輸出 JSON 格式的分析結果，包含：
1. intent: 意圖分類
2. confidence: 信心度
3. entities: 識別到的實體
4. missing_info: 缺失的關鍵信息
5. reasoning: 你的推理過程"""

    response = await cca_agent.step(
        user_message=prompt,
        max_steps=1
    )

    return json.loads(response.content)
```

### 5.2.2 任務分解策略

CCA 使用 LangGraph 的狀態機來管理任務分解與執行：

```python
# cca/workflow.py
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
import operator

class CCAState(TypedDict):
    """CCA 工作流狀態"""
    request: str
    user_context: dict
    intent: dict                    # 意圖識別結果
    task_plan: list[dict]           # 任務計劃
    current_step: int               # 當前執行步驟
    results: Annotated[list, operator.add]  # 累積結果
    errors: list[dict]              # 錯誤列表
    status: str                     # pending / executing / completed / failed
    audit_trail: list[dict]         # 審計軌跡

async def intent_recognition(state: CCAState) -> CCAState:
    """步驟 1：意圖識別"""
    intent = await parse_intent(
        state["cca_agent"],
        state["request"],
        state["user_context"]
    )
    return {
        **state,
        "intent": intent,
        "audit_trail": state["audit_trail"] + [{
            "step": "intent_recognition",
            "result": intent
        }]
    }

async def create_task_plan(state: CCAState) -> CCAState:
    """步驟 2：任務分解"""
    intent = state["intent"]

    # 檢查信心度
    if intent["confidence"] < 0.75:
        return {
            **state,
            "status": "awaiting_confirmation",
            "audit_trail": state["audit_trail"] + [{
                "step": "low_confidence",
                "reason": f"信心度 {intent['confidence']:.2f} 低於門檻",
                "action": "request_human_confirmation"
            }]
        }

    # 檢查缺失信息
    if intent.get("missing_info"):
        return {
            **state,
            "status": "awaiting_info",
            "audit_trail": state["audit_trail"] + [{
                "step": "missing_info",
                "fields": intent["missing_info"]
            }]
        }

    # 使用 LLM 生成任務計劃
    plan = await generate_task_plan(state["cca_agent"], intent)
    return {
        **state,
        "task_plan": plan,
        "current_step": 0,
        "audit_trail": state["audit_trail"] + [{
            "step": "task_planning",
            "plan": plan
        }]
    }

async def execute_current_step(state: CCAState) -> CCAState:
    """步驟 3：執行當前子任務"""
    if state["current_step"] >= len(state["task_plan"]):
        return {**state, "status": "completed"}

    step = state["task_plan"][state["current_step"]]

    # 查詢目標 Agent
    agents = await state["registry"].discover(step["capability"])
    if not agents:
        return {
            **state,
            "errors": state["errors"] + [{
                "step": state["current_step"],
                "error": f"找不到具備 {step['capability']} 能力的 Agent"
            }],
            "status": "error"
        }

    # 選擇最合適的 Agent（基於負載）
    target_agent = select_best_agent(agents)

    # 通過 MCP 發送任務
    result = await state["mcp"].send_task(
        agent_id=target_agent.agent_id,
        task=step,
        context=state.get("context", {})
    )

    return {
        **state,
        "results": [result],
        "current_step": state["current_step"] + 1,
        "audit_trail": state["audit_trail"] + [{
            "step": f"execute_step_{state['current_step']}",
            "agent": target_agent.agent_id,
            "result_status": result.get("status", "unknown")
        }]
    }

def should_continue(state: CCAState) -> str:
    """判斷下一步走向"""
    if state.get("status") in ("awaiting_confirmation", "awaiting_info"):
        return "await_human"
    if state["errors"]:
        return "error"
    if state["current_step"] >= len(state.get("task_plan", [])):
        return "finalize"
    return "execute"

async def finalize_results(state: CCAState) -> CCAState:
    """整合所有結果，生成最終響應"""
    summary = await generate_response_summary(
        state["cca_agent"],
        state["request"],
        state["results"]
    )
    return {
        **state,
        "status": "completed",
        "final_response": summary
    }

# 構建工作流
def build_cca_workflow() -> StateGraph:
    workflow = StateGraph(CCAState)

    workflow.add_node("recognize_intent", intent_recognition)
    workflow.add_node("plan_tasks", create_task_plan)
    workflow.add_node("execute_step", execute_current_step)
    workflow.add_node("finalize", finalize_results)

    workflow.set_entry_point("recognize_intent")
    workflow.add_edge("recognize_intent", "plan_tasks")
    workflow.add_conditional_edges("plan_tasks", should_continue, {
        "execute": "execute_step",
        "await_human": END,
        "error": "finalize",
        "finalize": "finalize"
    })
    workflow.add_conditional_edges("execute_step", should_continue, {
        "execute": "execute_step",
        "await_human": END,
        "error": "finalize",
        "finalize": "finalize"
    })
    workflow.add_edge("finalize", END)

    return workflow.compile()
```

---

## 5.3 審計與合規

### 5.3.1 審計日誌的完整結構

每個 CCA 操作都必須生成不可篡改的審計記錄：

```python
# cca/audit.py
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional
import hashlib
import json

@dataclass
class AuditRecord:
    """審計記錄"""
    audit_id: str
    timestamp: str
    request_id: str
    user_id: str
    user_role: str
    action_type: str               # intent_recognition / task_planning / dispatch / result
    decision: dict                 # CCA 的決策內容
    reasoning: str                 # CCA 的推理過程
    confidence: float
    inputs_summary: str            # 輸入摘要（避免存儲敏感完整數據）
    outputs_summary: str           # 輸出摘要
    latency_ms: int
    agent_involved: Optional[str]  # 涉及的 Agent ID
    error: Optional[str]           # 錯誤信息
    checksum: str                  # 記錄完整性校驗

class AuditManager:
    """審計管理器 — 確保審計記錄的完整性與不可篡改性"""

    def __init__(self, storage):
        self.storage = storage  # PostgreSQL 或不可變存儲

    async def record(self, record: AuditRecord):
        """存儲審計記錄"""
        # 計算校驗和（確保記錄未被篡改）
        record_dict = asdict(record)
        record_dict.pop("checksum")
        record.checksum = hashlib.sha256(
            json.dumps(record_dict, sort_keys=True).encode()
        ).hexdigest()

        await self.storage.insert("audit_log", asdict(record))

    async def verify_integrity(self, audit_id: str) -> bool:
        """驗證審計記錄的完整性"""
        record = await self.storage.get("audit_log", audit_id)
        if not record:
            return False

        stored_checksum = record.pop("checksum")
        computed = hashlib.sha256(
            json.dumps(record, sort_keys=True).encode()
        ).hexdigest()
        return stored_checksum == computed

    async def query(self, filters: dict, limit: int = 100) -> list[dict]:
        """查詢審計記錄"""
        return await self.storage.query("audit_log", filters, limit)
```

### 5.3.2 審計與 AIEBoK 的對應

| AIEBoK 領域 | 審計實現 |
|-------------|---------|
| **Trustworthiness** | 完整記錄 CCA 的推理過程、信心度、替代方案 |
| **Observability** | 審計日誌與 Trace 關聯，可按 Trace ID 查詢 |
| **Scalability** | 審計記錄異步寫入，不影響主流程性能 |
| **Lifecycle** | 審計記錄的保留策略、歸檔、清理 |

---

## 5.4 錯誤處理與降級策略

### 5.4.1 錯誤分類

CCA 需要處理多種類型的錯誤，並採用相應的策略：

```python
# cca/error_handling.py
from enum import Enum

class ErrorSeverity(Enum):
    TRANSIENT = "transient"      # 臨時性錯誤，可重試
    PERMANENT = "permanent"      # 永久性錯誤，需替代方案
    CRITICAL = "critical"        # 嚴重錯誤，需立即通知

class ErrorCategory(Enum):
    AGENT_UNAVAILABLE = "agent_unavailable"
    AGENT_TIMEOUT = "agent_timeout"
    AGENT_ERROR = "agent_error"
    MCP_FAILURE = "mcp_failure"
    LLM_ERROR = "llm_error"
    VALIDATION_ERROR = "validation_error"

ERROR_STRATEGIES = {
    ErrorCategory.AGENT_UNAVAILABLE: {
        "severity": ErrorSeverity.TRANSIENT,
        "strategy": "retry_with_alternative",
        "max_retries": 2,
        "fallback": "queue_for_later"
    },
    ErrorCategory.AGENT_TIMEOUT: {
        "severity": ErrorSeverity.TRANSIENT,
        "strategy": "retry_with_timeout",
        "max_retries": 1,
        "timeout_multiplier": 1.5
    },
    ErrorCategory.AGENT_ERROR: {
        "severity": ErrorSeverity.PERMANENT,
        "strategy": "report_to_user",
        "include_suggestion": True
    },
    ErrorCategory.MCP_FAILURE: {
        "severity": ErrorSeverity.CRITICAL,
        "strategy": "notify_admin_and_degrade",
        "degrade_mode": "direct_agent_call"
    },
    ErrorCategory.LLM_ERROR: {
        "severity": ErrorSeverity.CRITICAL,
        "strategy": "fallback_model",
        "fallback_model": "gpt-4o-mini"
    }
}

async def handle_error(
    cca: "CCACore",
    error: Exception,
    category: ErrorCategory,
    context: dict
) -> dict:
    """CCA 的錯誤處理邏輯"""
    strategy = ERROR_STRATEGIES[category]

    if strategy["strategy"] == "retry_with_alternative":
        # 嘗試查找替代 Agent
        alternative = await find_alternative_agent(
            cca.registry,
            context["required_capability"],
            exclude=[context["failed_agent_id"]]
        )
        if alternative:
            return await cca.mcp.send_task(
                agent_id=alternative.agent_id,
                task=context["task"]
            )

    elif strategy["strategy"] == "report_to_user":
        return {
            "action": "notify_user",
            "message": f"操作失敗：{str(error)}",
            "suggestion": "建議稍後重試或聯繫 IT 支持"
        }

    elif strategy["strategy"] == "notify_admin_and_degrade":
        await notify_admin(error, context)
        # 降級：直接調用 Agent（繞過 MCP）
        return await direct_agent_call(context)

    # 重試
    if strategy.get("max_retries", 0) > 0:
        for attempt in range(strategy["max_retries"]):
            try:
                return await retry_operation(context, attempt)
            except Exception:
                continue

    return {
        "action": "report_failure",
        "error": str(error),
        "category": category.value
    }
```

### 5.4.2 部分完成的處理

當多步驟任務中部分子任務成功、部分失敗時，CCA 需要智慧地處理：

```python
async def handle_partial_completion(
    results: list[dict],
    task_plan: list[dict]
) -> dict:
    """處理部分完成的場景"""
    successful = [r for r in results if r.get("status") == "success"]
    failed = [r for r in results if r.get("status") != "success"]

    if not failed:
        return {"status": "completed", "results": results}

    if not successful:
        return {"status": "failed", "errors": failed}

    # 部分完成：生成補償建議
    completed_steps = [task_plan[i] for i, r in enumerate(results) if r.get("status") == "success"]
    remaining_steps = [task_plan[i] for i, r in enumerate(results) if r.get("status") != "success"]

    return {
        "status": "partial",
        "completed": completed_steps,
        "failed": remaining_steps,
        "compensation_options": generate_compensation_options(remaining_steps),
        "message": f"已完成 {len(successful)}/{len(results)} 個步驟"
    }
```

---

## 5.5 CCA 的配置管理

### 5.5.1 多環境配置

```yaml
# config/cca-config.yaml
defaults:
  llm:
    provider: anthropic
    model: claude-3-5-sonnet-20241022
    temperature: 0.1
    max_tokens: 4096
  confidence_threshold: 0.75
  max_task_steps: 10
  timeout_seconds: 300

environments:
  development:
    llm:
      provider: ollama
      model: llama3:8b
      base_url: http://localhost:11434
    confidence_threshold: 0.5  # 開發時降低門檻
    max_task_steps: 5

  staging:
    llm:
      provider: anthropic
      model: claude-3-5-sonnet-20241022
    confidence_threshold: 0.7

  production:
    llm:
      provider: anthropic
      model: claude-3-5-sonnet-20241022
    confidence_threshold: 0.75
    max_task_steps: 15
    audit_level: full  # 完整審計
```

### 5.5.2 Prompt 版本管理

CCA 的 Prompt 變更需要版本控制，因為 Prompt 的修改直接影響 Agent 行為：

```python
# cca/prompt_manager.py
class PromptManager:
    """Prompt 版本管理器"""

    def __init__(self, storage):
        self.storage = storage
        self.current_version = None

    async def get_prompt(self, version: str = "latest") -> str:
        """獲取指定版本的 Prompt"""
        if version == "latest":
            version = self.current_version or await self._get_latest_version()
        return await self.storage.get(f"prompts/{version}")

    async def update_prompt(
        self,
        new_prompt: str,
        author: str,
        change_reason: str,
        test_results: dict = None
    ) -> str:
        """更新 Prompt，記錄版本與原因"""
        version = f"v{datetime.now().strftime('%Y%m%d%H%M%S')}"
        await self.storage.put(f"prompts/{version}", {
            "content": new_prompt,
            "author": author,
            "change_reason": change_reason,
            "test_results": test_results,
            "created_at": datetime.now().isoformat()
        })
        self.current_version = version
        return version
```

---

## 本章小結

本章將 CCA 從架構概念轉化為可運行的代碼：

- **CCA 的核心實現**：基於 Letta Agent 的 CCA 類，工具集只包含協調類操作
- **意圖識別**：結構化 Prompt + JSON Schema 輸出，支持信心度評估
- **任務分解**：LangGraph 狀態機，支持條件分支、重試、部分完成
- **審計與合規**：完整的審計軌跡，帶校驗和的不可篡改記錄
- **錯誤處理**：五種錯誤類別，分級處理策略，部分完成的補償機制
- **配置管理**：多環境配置、Prompt 版本控制

CCA 是平台最複雜的組件，其設計品質直接決定平台的智能水平。在下一章中，我們將轉向 Specialized Agents 的構建 — 如何用 Letta 定義領域專家 Agent，如何設計工具集，如何集成 RAG 知識庫。

---

## 延伸閱讀

1. **《Building LLM Apps for Production》** — Chip Huyen, O'Reilly Media. LLM 應用的生產級實踐。
2. **LangGraph Documentation** — https://langchain-ai.github.io/langgraph/ — 狀態機工作流編排。
3. **《Site Reliability Engineering》** — Google SRE Team. 錯誤處理、降級策略的工程實踐。
4. **Letta Documentation** — https://docs.letta.com/ — Agent 定義與持久化配置。
5. **《Designing Data-Intensive Applications》** — Martin Kleppmann. 審計日誌、分佈式系統錯誤處理的設計原則。
