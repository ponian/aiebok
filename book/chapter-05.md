# 第五章：CCA 實現細節 — 中央協調 Agent 的設計與實踐

> 「CCA 不只是一個 LLM 調用器，它是一個完整的認知系統 — 感知意圖、規劃行動、協調資源、整合結果、從經驗中學習。」

第二章從宏觀角度定義了 CCA 的七大核心職責。本章將這些職責轉化為可運行的代碼：CCA 的完整生命週期、Prompt 工程的實踐細節、LangGraph 工作流的具體實現，以及狀態管理與錯誤處理機制。

---

## 5.1 CCA 的整體架構

### 5.1.1 CCA 作為一個 Letta Agent

CCA 本身也是一個 Letta Agent，但它與 Specialized Agents 有本質區別：CCA 不直接執行業務操作，而是作為**認知中樞**協調其他 Agent。這種「只動腦、不動手」的設計確保了 CCA 的通用性 — 它不需要知道每個業務操作的具體細節，只需要知道「誰能做什麼」和「怎麼分配任務」。

以下代碼完整展示了 CCA 的核心組件：**專屬工具集**（4 個協調類工具）、**結構化系統提示**（定義角色、決策流程、約束條件）、以及 **CCACore 主類**（整合 Letta Agent 框架）。

```python
# cca/core.py
from letta import Agent, Tool
from opentelemetry import trace, metrics
from typing import Optional
import json

# === 初始化 OTel 遙測 ===
# tracer 用於分散式追蹤（記錄每個操作的耗時和調用路徑）
# meter 用於指標採集（記錄請求數、延遲等數值型數據）
tracer = trace.get_tracer("cca-agent")
meter = metrics.get_meter("cca-agent")

# === CCA 的專屬工具集 — 只包含協調類操作 ===
# 注意：這裡沒有任何業務工具（如 create_ad_account）
# CCA 的價值在於「決定做什麼」而不是「執行操作」

@Tool
def query_agent_registry(capability: str) -> list[dict]:
    """查詢 Agent Registry，找到具備特定能力的 Agent 列表。

    Args:
        capability: 要查詢的能力名稱，如 'create_ad_account'
    Returns:
        具備該能力的 Agent 列表，包含 agent_id、版本、SLA 信息
    """
    # 實際實現會調用 Agent Registry 服務（通過 gRPC 或 REST）
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
        agent_id: 目標 Agent 的 ID（從 query_agent_registry 獲取）
        task_description: 任務的自然語言描述（CCA 的 LLM 生成）
        inputs: 結構化的輸入參數（從用戶意圖中提取）
        context: 需要傳遞的上下文信息（如用戶 ID、部門、權限）
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
        reason: 需要確認的原因（如「信心度低於 0.75」）
        proposed_plan: 提議的任務計劃（讓用戶看到 CCA 打算做什麼）
    Returns:
        用戶的確認結果（approve / reject / modify）
    """
    pass

@Tool
def query_knowledge_base(query: str, context: dict = None) -> str:
    """查詢企業知識庫，獲取政策、SOP 等信息。

    Args:
        query: 查詢內容（如「新員工 IT 帳號創建流程」）
        context: 額外上下文（部門、角色等，用於過濾相關文檔）
    Returns:
        相關知識片段
    """
    pass

# === CCA 的系統提示（結構化 Prompt）===
# 這份 Prompt 定義了 CCA 的「性格」和「行為準則」
# Prompt 的每一行都影響 CCA 的決策品質 — 版本控制至關重要（見 5.5.2 節）
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
- 你不直接執行任何業務操作（不能創建帳號、不能發送郵件等）
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

# === CCA 核心類 ===
class CCACore:
    """CCA 的核心實現 — 整合 Letta Agent 框架"""

    def __init__(self, llm_config: dict, agent_registry, mcp_client, knowledge_base):
        self.llm_config = llm_config
        self.registry = agent_registry    # Agent Registry 客戶端
        self.mcp = mcp_client            # MCP Service 客戶端（用於向 Agent 發送任務）
        self.kb = knowledge_base         # 知識庫客戶端

        # 初始化 Letta Agent — CCA 本質上是一個 Letta Agent
        # 區別在於：工具集只有協調類操作，system prompt 強調推理而非執行
        self.agent = Agent(
            name="Central Coordinator Agent",
            system=CCA_SYSTEM_PROMPT,    # 系統提示 = CCA 的「行為憲法」
            tools=[
                query_agent_registry,
                send_task_to_agent,
                request_human_confirmation,
                query_knowledge_base
            ],
            persistence_config={
                "type": "postgres",       # Letta 的 Agent 狀態持久化到 PostgreSQL
                "host": "postgres-service",
                "port": 5432,
                "database": "letta_agents",
                "table_prefix": "cca_"    # CCA 專用的表前綴，避免與其他 Agent 衝突
            }
        )

    async def process_request(self, user_input: str, user_context: dict) -> dict:
        """處理用戶請求的完整流程 — CCA 的核心方法"""
        # 外層 Span：追蹤整個請求處理過程
        with tracer.start_as_current_span("cca.process_request") as span:
            span.set_attribute("user_id", user_context.get("user_id", "unknown"))
            span.set_attribute("input_length", len(user_input))

            # 1. 調用 LLM 進行意圖識別與任務規劃
            #    內層 Span：追蹤 LLM 推理的具體耗時（通常是最主要的延遲來源）
            with tracer.start_as_current_span("cca.llm_reasoning"):
                response = await self.agent.step(
                    user_message=user_input,
                    max_steps=15    # CCA 可能需要多步推理（查詢 Registry → 發送任務 → 整合結果）
                )

            # 2. 記錄審計日誌（異步寫入，不阻塞主流程）
            #    審計日誌包含完整的推理過程，用於合規審查和問題排查
            audit_record = self._create_audit_record(
                user_input, response, user_context
            )
            await self._store_audit(audit_record)

            # 3. 返回結果
            return {
                "response": response.content,       # CCA 的自然語言回覆
                "task_results": response.tool_results,  # 工具調用結果（如 Agent 返回的數據）
                "usage": response.usage,            # Token 使用量（用於成本監控）
                "audit_id": audit_record["audit_id"]  # 審計 ID，便於日後追溯
            }
```

**關鍵設計決策**：
- **工具集分離**：CCA 的 4 個工具全部是「協調類」— 查詢、發送、確認、查知識庫。沒有任何業務操作工具。這確保 CCA 永遠不會「越俎代庖」直接執行操作。
- **信心度機制**：Prompt 中明確規定「信心度低於 0.75 時必須向用戶確認」，這是一個安全網 — 防止 CCA 在不確定時「猜測」用戶意圖。
- **max_steps=15**：CCA 的推理鏈比一般 Agent 長（通常 5-10 步），因為它需要多輪工具調用（查詢 Registry → 發送任務 → 整合結果）。
- **OTel 嵌套 Span**：`cca.process_request` 是父 Span，`cca.llm_reasoning` 是子 Span。在 Jaeger 中可以清楚看到 LLM 推理佔了整個處理時間的多少比例。

### 5.1.2 CCA 與 Specialized Agents 的關鍵區別

| 維度 | CCA | Specialized Agents |
|------|-----|-------------------|
| **工具集** | 只包含協調類工具（查詢、發送、確認） | 包含業務操作工具（創建帳號、查詢數據） |
| **Prompt** | 強調推理過程輸出、決策透明性 | 強調領域專業知識、操作準確性 |
| **LLM** | 使用最強模型（Claude Opus 4） | 使用本地模型（Llama 4 Scout / Qwen 3 235B） |
| **步數限制** | 較高（15 步），因為需要多輪推理 | 較低（10 步），任務相對直接 |
| **審計要求** | 每個決策都記錄完整推理過程 | 記錄操作結果即可 |

---

## 5.2 意圖識別與任務分解

### 5.2.1 意圖識別的 Prompt 設計

CCA 的意圖識別不是簡單的分類問題，而是需要理解上下文、識別缺失信息、評估信心度的複雜認知過程。以下代碼定義了結構化的輸出 Schema 和解析函數：

```python
# cca/intent_parser.py

# === 意圖識別的 JSON Schema ===
# 用於約束 LLM 的輸出格式 — 確保每次輸出都包含完整的分析結果
# JSON Schema 不只是文檔，很多 LLM 框架會用它來驗證輸出
INTENT_SCHEMA = {
    "type": "object",
    "properties": {
        "intent": {
            "type": "string",
            "enum": [
                "create_it_account",     # 創建 IT 帳號
                "reset_password",        # 重置密碼
                "modify_permissions",    # 修改權限
                "query_employee_info",   # 查詢員工信息
                "onboard_new_hire",      # 新員工入職（可能涉及多個子任務）
                "offboard_employee",     # 離職處理（可能涉及多個子任務）
                "unknown"                # 無法識別的意圖 — CCA 會請求用戶澄清
            ]
        },
        "confidence": {
            "type": "number",
            "minimum": 0.0,    # 0.0 = 完全不確定
            "maximum": 1.0     # 1.0 = 完全確定
        },
        "entities": {
            "type": "object",
            "properties": {
                "employee_name": {"type": "string"},   # 員工姓名
                "department": {"type": "string"},      # 部門
                "role": {"type": "string"},            # 職位
                "action_detail": {"type": "string"}    # 具體操作描述
            }
        },
        "missing_info": {
            "type": "array",
            "items": {"type": "string"}    # 缺失的關鍵信息列表
        },
        "reasoning": {
            "type": "string",
            "description": "CCA 的推理過程（用於審計）"
        }
    },
    "required": ["intent", "confidence", "reasoning"]
    # 注意：entities 和 missing_info 不是 required
    # 因為某些意圖（如 reset_password）可能不需要實體信息
}

async def parse_intent(cca_agent, user_input: str, context: dict) -> dict:
    """使用 CCA Agent 解析用戶意圖 — 意圖識別的核心函數"""

    # 構建 Prompt：將用戶輸入和上下文組合為 LLM 的輸入
    # 上下文（角色、部門）幫助 LCA 做更準確的判斷
    # 例如：HR 用戶詢問「創建帳號」可能是 HR 系統帳號，IT 用戶則是 IT 帳號
    prompt = f"""分析以下用戶請求，識別意圖和實體。

用戶請求：「{user_input}」

當前上下文：
- 用戶角色：{context.get('user_role', 'unknown')}
- 部門：{context.get('department', 'unknown')}
- 時間：{context.get('timestamp', 'unknown')}

請輸出 JSON 格式的分析結果，包含：
1. intent: 意圖分類（參考 INTENT_SCHEMA 中的 enum 值）
2. confidence: 信心度（0.0-1.0）
3. entities: 識別到的實體（員工姓名、部門等）
4. missing_info: 缺失的關鍵信息（需要向用戶追問的信息）
5. reasoning: 你的推理過程（為什麼選擇這個意圖分類）"""

    # max_steps=1: 意圖識別是一步完成的推理，不需要多步工具調用
    response = await cca_agent.step(
        user_message=prompt,
        max_steps=1
    )

    # LLM 輸出應為 JSON 字符串，解析為 dict
    # 在生產環境中，這裡應該添加 JSON 解析的錯誤處理
    return json.loads(response.content)
```

**關鍵設計決策**：
- **Schema 約束**：使用 `enum` 限定意圖類型，避免 LLM 輸出無效的意圖分類。如果用戶的請求不在 enum 中，LLM 應選擇 `unknown`。
- **上下文注入**：將用戶角色和部門注入 Prompt，讓 CCA 能區分「HR 問 HR 系統的問題」和「IT 問 HR 系統的問題」。
- **missing_info 字段**：這是一個關鍵設計 — CCA 不只是識別意圖，還要識別「缺少什麼信息」。如果用戶說「幫張小明創建帳號」但沒說部門，`missing_info` 會包含 `["department"]`，觸發 CCA 向用戶追問。

### 5.2.2 任務分解策略

CCA 使用 LangGraph 的狀態機來管理任務分解與執行。LangGraph 將工作流建模為**有向圖** — 節點是處理步驟，邊是狀態轉移條件。這種模式天然支持條件分支、循環（重試）和並行，非常適合 CCA 的複雜決策邏輯。

```python
# cca/workflow.py
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
import operator

# === 狀態定義 ===
# CCAState 是整個工作流的「共享狀態」— 每個節點讀取和更新這個狀態
class CCAState(TypedDict):
    request: str                     # 用戶的原始請求
    user_context: dict               # 用戶上下文（角色、部門等）
    intent: dict                     # 意圖識別結果（由 recognize_intent 節點填充）
    task_plan: list[dict]            # 任務計劃（由 plan_tasks 節點填充）
    current_step: int                # 當前執行步驟索引
    results: Annotated[list, operator.add]  # 累積結果（Annotated + operator.add 表示每次更新時追加而非替換）
    errors: list[dict]               # 錯誤列表
    status: str                      # pending / executing / completed / failed
    audit_trail: list[dict]          # 審計軌跡（每個步驟的記錄）

# === 節點 1：意圖識別 ===
async def intent_recognition(state: CCAState) -> CCAState:
    """步驟 1：解析用戶意圖，提取實體，評估信心度"""
    intent = await parse_intent(
        state["cca_agent"],
        state["request"],
        state["user_context"]
    )
    return {
        **state,    # 保留原有狀態
        "intent": intent,
        # 審計軌跡：記錄這一步的輸入和輸出
        "audit_trail": state["audit_trail"] + [{
            "step": "intent_recognition",
            "result": intent
        }]
    }

# === 節點 2：任務計劃 ===
async def create_task_plan(state: CCAState) -> CCAState:
    """步驟 2：根據意圖生成子任務計劃"""
    intent = state["intent"]

    # 安全檢查 1：信心度不足 → 暫停，等待用戶確認
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

    # 安全檢查 2：缺失關鍵信息 → 暫停，向用戶追問
    if intent.get("missing_info"):
        return {
            **state,
            "status": "awaiting_info",
            "audit_trail": state["audit_trail"] + [{
                "step": "missing_info",
                "fields": intent["missing_info"]
            }]
        }

    # 使用 LLM 生成具體的子任務計劃
    # 例如：「新員工入職」→ [創建 AD 帳號, 創建郵箱, 分配設備]
    plan = await generate_task_plan(state["cca_agent"], intent)
    return {
        **state,
        "task_plan": plan,
        "current_step": 0,  # 從第一步開始執行
        "audit_trail": state["audit_trail"] + [{
            "step": "task_planning",
            "plan": plan
        }]
    }

# === 節點 3：執行當前子任務 ===
async def execute_current_step(state: CCAState) -> CCAState:
    """步驟 3：向 Agent 發送當前子任務"""
    # 所有步驟已完成 → 進入整合階段
    if state["current_step"] >= len(state["task_plan"]):
        return {**state, "status": "completed"}

    step = state["task_plan"][state["current_step"]]

    # 查詢具備所需能力的 Agent
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

    # 選擇最合適的 Agent（基於負載均衡）
    target_agent = select_best_agent(agents)

    # 通過 MCP Service 發送任務（同步等待結果）
    result = await state["mcp"].send_task(
        agent_id=target_agent.agent_id,
        task=step,
        context=state.get("context", {})
    )

    # 更新狀態：累積結果、推進步驟、記錄審計
    return {
        **state,
        "results": [result],    # Annotated[list, operator.add] 確保追加而非替換
        "current_step": state["current_step"] + 1,
        "audit_trail": state["audit_trail"] + [{
            "step": f"execute_step_{state['current_step']}",
            "agent": target_agent.agent_id,
            "result_status": result.get("status", "unknown")
        }]
    }

# === 路由函數：決定下一步走向 ===
def should_continue(state: CCAState) -> str:
    """根據當前狀態決定走向 — 這是條件邊的核心邏輯"""
    if state.get("status") in ("awaiting_confirmation", "awaiting_info"):
        return "await_human"    # 需要用戶介入，暫停工作流
    if state["errors"]:
        return "error"          # 發生錯誤，跳到整合階段（帶錯誤信息）
    if state["current_step"] >= len(state.get("task_plan", [])):
        return "finalize"       # 所有步驟完成，進入整合階段
    return "execute"            # 繼續執行下一步

# === 節點 4：整合結果 ===
async def finalize_results(state: CCAState) -> CCAState:
    """整合所有 Agent 的結果，生成最終回覆"""
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

# === 構建工作流圖 ===
def build_cca_workflow() -> StateGraph:
    workflow = StateGraph(CCAState)

    # 添加節點（處理步驟）
    workflow.add_node("recognize_intent", intent_recognition)
    workflow.add_node("plan_tasks", create_task_plan)
    workflow.add_node("execute_step", execute_current_step)
    workflow.add_node("finalize", finalize_results)

    # 定義流程
    workflow.set_entry_point("recognize_intent")   # 入口點
    workflow.add_edge("recognize_intent", "plan_tasks")  # 固定邊：意圖識別 → 任務計劃

    # 條件邊：任務計劃根據狀態分支
    # "execute":  → 繼續執行下一步
    # "await_human": → 結束（等待用戶回覆後重新觸發）
    # "error": → 跳到整合（帶錯誤信息）
    # "finalize": → 跳到整合
    workflow.add_conditional_edges("plan_tasks", should_continue, {
        "execute": "execute_step",
        "await_human": END,
        "error": "finalize",
        "finalize": "finalize"
    })

    # 條件邊：執行後根據狀態決定下一步
    # 注意：execute_step 可能回到自身（循環執行多個子任務）
    workflow.add_conditional_edges("execute_step", should_continue, {
        "execute": "execute_step",   # 還有下一步 → 循環
        "await_human": END,
        "error": "finalize",
        "finalize": "finalize"
    })

    workflow.add_edge("finalize", END)

    return workflow.compile()
```

**關鍵設計決策**：
- **Annotated[list, operator.add]**：LangGraph 的特殊類型標註。普通 `list` 在狀態更新時會被替換為新值，但 `Annotated[list, operator.add]` 告訴 LangGraph 用 `operator.add`（即 list 拼接）來更新。這確保多個步驟的結果被累積而不是覆蓋。
- **循環結構**：`execute_step` → `should_continue` → `execute_step` 形成循環，直到所有子任務完成。這比硬編碼的 for 迴圈更靈活 — 每次循環都可以根據狀態決定是繼續、暫停還是中止。
- **await_human → END**：當需要用戶介入時，工作流終止。用戶回覆後，系統會用新的輸入重新觸發工作流（從 intent_recognition 開始），而不是從中間恢復。這是簡化設計 — 用戶介入通常意味著需求可能有變化，從頭開始更安全。

---

## 5.3 審計與合規

### 5.3.1 審計日誌的完整結構

每個 CCA 操作都必須生成不可篡改的審計記錄。審計日誌是合規的基礎 — 當監管機構或內部審計團隊追問「為什麼 AI 做了這個決定」時，審計日誌是最有力的回應。它記錄了 CCA 的完整推理過程，而不只是最終結果。

```python
# cca/audit.py
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional
import hashlib
import json

@dataclass
class AuditRecord:
    """審計記錄 — 記錄 CCA 每次決策的完整上下文"""
    audit_id: str                     # 唯一審計 ID（UUID）
    timestamp: str                    # ISO 格式時間戳
    request_id: str                   # 關聯的用戶請求 ID
    user_id: str                      # 發起請求的用戶
    user_role: str                    # 用戶角色（用於權限審查）
    action_type: str                  # 操作類型：intent_recognition / task_planning / dispatch / result
    decision: dict                    # CCA 的決策內容（結構化數據）
    reasoning: str                    # CCA 的推理過程（自然語言，用於人工審查）
    confidence: float                 # 信心度（0.0-1.0）
    inputs_summary: str               # 輸入摘要（避免存儲敏感完整數據）
    outputs_summary: str              # 輸出摘要
    latency_ms: int                   # 處理延遲（毫秒）
    agent_involved: Optional[str]     # 涉及的 Agent ID（如 "hr-agent-v1"）
    error: Optional[str]              # 錯誤信息（無錯誤則為 None）
    checksum: str                     # 記錄完整性校驗（SHA-256 哈希）

class AuditManager:
    """審計管理器 — 確保審計記錄的完整性與不可篡改性"""

    def __init__(self, storage):
        self.storage = storage    # PostgreSQL 或不可變存儲（如 AWS S3 + Object Lock）

    async def record(self, record: AuditRecord):
        """存儲審計記錄 — 計算校驗和後寫入"""
        record_dict = asdict(record)
        record_dict.pop("checksum")    # 移除 checksum 字段，用其餘內容計算哈希

        # SHA-256 校驗和：確保記錄存儲後未被篡改
        # sort_keys=True 確保 JSON 序列化順序一致（否則相同內容可能產生不同哈希）
        record.checksum = hashlib.sha256(
            json.dumps(record_dict, sort_keys=True).encode()
        ).hexdigest()

        await self.storage.insert("audit_log", asdict(record))

    async def verify_integrity(self, audit_id: str) -> bool:
        """驗證審計記錄的完整性 — 重新計算哈希並與存儲的哈希比對"""
        record = await self.storage.get("audit_log", audit_id)
        if not record:
            return False

        # 取出存儲的校驗和
        stored_checksum = record.pop("checksum")
        # 用其餘內容重新計算哈希
        computed = hashlib.sha256(
            json.dumps(record, sort_keys=True).encode()
        ).hexdigest()
        # 比對：如果一致則記錄未被篡改
        return stored_checksum == computed

    async def query(self, filters: dict, limit: int = 100) -> list[dict]:
        """查詢審計記錄 — 支持按 user_id、action_type、時間範圍等過濾"""
        return await self.storage.query("audit_log", filters, limit)
```

**關鍵設計決策**：
- **校驗和防篡改**：每條記錄存儲時計算 SHA-256 哈希。任何對記錄內容的修改都會導致哈希不匹配。這不是加密（記錄是明文），而是完整性驗證 — 確保沒有被悄悄改過。
- **inputs_summary 而非 inputs**：審計記錄存儲的是「摘要」而非完整數據，避免在審計日誌中暴露敏感信息（如員工薪資、密碼）。
- **異步寫入**：`audit()` 方法不阻塞主流程。在高吞吐場景下，可以使用消息隊列（如 NATS）異步寫入審計日誌，確保不影響 Agent 的響應時間。

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

CCA 需要處理多種類型的錯誤，並採用相應的策略。關鍵設計是將錯誤**分類、分級、對應策略** — 不是所有錯誤都值得重試，也不是所有錯誤都需要通知管理員。以下代碼定義了錯誤分類體系和對應的處理策略：

```python
# cca/error_handling.py
from enum import Enum

# === 錯誤嚴重程度 ===
class ErrorSeverity(Enum):
    TRANSIENT = "transient"    # 臨時性錯誤（如網絡抖動），可重試
    PERMANENT = "permanent"    # 永久性錯誤（如權限不足），需替代方案
    CRITICAL = "critical"      # 嚴重錯誤（如 MCP 服務宕機），需立即通知

# === 錯誤類別 ===
class ErrorCategory(Enum):
    AGENT_UNAVAILABLE = "agent_unavailable"  # Agent 不可用（宕機或過載）
    AGENT_TIMEOUT = "agent_timeout"          # Agent 超時（處理時間過長）
    AGENT_ERROR = "agent_error"              # Agent 內部錯誤（業務邏輯異常）
    MCP_FAILURE = "mcp_failure"              # MCP Service 故障（通信中斷）
    LLM_ERROR = "llm_error"                  # LLM 調用失敗（API 限流或服務不可用）
    VALIDATION_ERROR = "validation_error"    # 數據驗證失敗（輸入不合法）

# === 錯誤策略映射表 ===
# 每種錯誤類別對應一個策略配置 — 這是 CCA 錯誤處理的「大腦」
ERROR_STRATEGIES = {
    ErrorCategory.AGENT_UNAVAILABLE: {
        "severity": ErrorSeverity.TRANSIENT,
        "strategy": "retry_with_alternative",   # 先找替代 Agent，找不到再重試
        "max_retries": 2,                        # 最多重試 2 次
        "fallback": "queue_for_later"            # 全部失敗 → 加入延遲隊列
    },
    ErrorCategory.AGENT_TIMEOUT: {
        "severity": ErrorSeverity.TRANSIENT,
        "strategy": "retry_with_timeout",        # 重試，但增加超時時間
        "max_retries": 1,                        # 只重試 1 次（超時通常是永久性的）
        "timeout_multiplier": 1.5                # 超時時間乘以 1.5（如從 30s 增加到 45s）
    },
    ErrorCategory.AGENT_ERROR: {
        "severity": ErrorSeverity.PERMANENT,
        "strategy": "report_to_user",            # 直接告知用戶失敗原因
        "include_suggestion": True               # 附帶解決建議
    },
    ErrorCategory.MCP_FAILURE: {
        "severity": ErrorSeverity.CRITICAL,
        "strategy": "notify_admin_and_degrade",  # 通知管理員 + 啟用降級模式
        "degrade_mode": "direct_agent_call"      # 降級：繞過 MCP，直接調用 Agent
    },
    ErrorCategory.LLM_ERROR: {
        "severity": ErrorSeverity.CRITICAL,
        "strategy": "fallback_model",            # 切換到備用模型
        "fallback_model": "gpt-4.1-mini"          # 降級到較小但更穩定的模型
    }
}

async def handle_error(
    cca: "CCACore",
    error: Exception,
    category: ErrorCategory,
    context: dict
) -> dict:
    """CCA 的錯誤處理主邏輯 — 根據錯誤類別執行對應策略"""
    strategy = ERROR_STRATEGIES[category]

    # 策略 1：尋找替代 Agent
    if strategy["strategy"] == "retry_with_alternative":
        alternative = await find_alternative_agent(
            cca.registry,
            context["required_capability"],
            exclude=[context["failed_agent_id"]]  # 排除已失敗的 Agent，避免重蹈覆轍
        )
        if alternative:
            return await cca.mcp.send_task(
                agent_id=alternative.agent_id,
                task=context["task"]
            )

    # 策略 2：通知用戶失敗
    elif strategy["strategy"] == "report_to_user":
        return {
            "action": "notify_user",
            "message": f"操作失敗：{str(error)}",
            "suggestion": "建議稍後重試或聯繫 IT 支持"
        }

    # 策略 3：通知管理員 + 降級（繞過 MCP 直接調用 Agent）
    elif strategy["strategy"] == "notify_admin_and_degrade":
        await notify_admin(error, context)
        return await direct_agent_call(context)

    # 重試邏輯（適用於 TRANSIENT 錯誤）
    if strategy.get("max_retries", 0) > 0:
        for attempt in range(strategy["max_retries"]):
            try:
                return await retry_operation(context, attempt)
            except Exception:
                continue    # 重試失敗 → 繼續下一次

    # 所有策略都失敗 → 報告最終失敗
    return {
        "action": "report_failure",
        "error": str(error),
        "category": category.value
    }
```

**關鍵設計決策**：
- **策略表驅動**：所有錯誤策略集中在 `ERROR_STRATEGIES` 字典中，新增錯誤類型只需添加一個條目，不需要修改處理邏輯。這比 `if/elif` 鏈更易維護。
- **降級模式**：MCP 故障時，CCA 可以繞過 MCP Service 直接調用 Agent。這是一個重要的容錯機制 — MCP 是通信中轉站，但不是唯一的通信路徑。
- **LLM 備用模型**：當主力 LLM（如 Claude）不可用時，自動切換到備用模型（如 gpt-4.1-mini）。雖然備用模型能力較弱，但「能用」比「不能用」好。

### 5.4.2 部分完成的處理

在多步驟任務中，有時部分子任務成功、部分失敗（例如「新員工入職」場景中，AD 帳號創建成功但郵箱分配失敗）。CCA 不能簡單地報錯或全部重試，而是需要智慧地分析哪些步驟已完成，哪些需要補償。

```python
async def handle_partial_completion(
    results: list[dict],
    task_plan: list[dict]
) -> dict:
    """處理部分完成的場景 — CCA 的補償決策邏輯"""

    # 分離成功和失敗的結果
    successful = [r for r in results if r.get("status") == "success"]
    failed = [r for r in results if r.get("status") != "success"]

    # 場景 1：全部成功 → 直接返回
    if not failed:
        return {"status": "completed", "results": results}

    # 場景 2：全部失敗 → 報告失敗
    if not successful:
        return {"status": "failed", "errors": failed}

    # 場景 3：部分成功 → 最複雜的場景
    # 需要分析哪些步驟已完成、哪些需要補償
    completed_steps = [
        task_plan[i] for i, r in enumerate(results)
        if r.get("status") == "success"
    ]
    remaining_steps = [
        task_plan[i] for i, r in enumerate(results)
        if r.get("status") != "success"
    ]

    return {
        "status": "partial",                               # 部分完成的狀態標識
        "completed": completed_steps,                       # 已完成的步驟（需要保留，不能重複執行）
        "failed": remaining_steps,                          # 失敗的步驟（需要重試或補償）
        "compensation_options": generate_compensation_options(remaining_steps),
        # 補償選項：如「重試失敗步驟」、「跳過並通知用戶」、「回滾已完成步驟」
        "message": f"已完成 {len(successful)}/{len(results)} 個步驟"
    }
```

**關鍵設計決策**：
- **三種結果狀態**：`completed`（全部成功）、`failed`（全部失敗）、`partial`（部分成功）。`partial` 是最複雜的，需要 CCA 決定如何處理已完成的部分。
- **補償選項生成**：`generate_compensation_options()` 是一個策略函數，根據失敗步驟的性質生成補償方案。例如：AD 帳號創建成功但郵箱失敗 → 補償選項是「保留 AD 帳號，手動創建郵箱」或「回滾 AD 帳號」。
- **不自動回滾**：CCA 不會自動回滾已完成的步驟，而是將選擇權交給用戶。因為自動回滾可能導致更大的問題（如「已發送的通知郵件無法撤回」）。

---

## 5.5 CCA 的配置管理

### 5.5.1 多環境配置

CCA 的行為由配置參數控制 — 不同環境（開發、測試、生產）需要不同的配置。例如：開發環境使用本地 LLM（Ollama）降低成本，生產環境使用雲端 LLM（Anthropic）確保品質。

```yaml
# config/cca-config.yaml
defaults:
  llm:
    provider: anthropic
    model: claude-opus-4-20250514
    temperature: 0.1            # 低溫度 = 確定性更高的輸出（適合生產）
    max_tokens: 4096            # 最大 token 數（影響回覆長度和成本）
  confidence_threshold: 0.75    # 信心度門檻（低於此值時要求用戶確認）
  max_task_steps: 10            # 最大任務步驟數（防止無限循環）
  timeout_seconds: 300          # 請求超時時間（秒）

environments:
  development:
    llm:
      provider: ollama              # 本地 LLM — 免費，但能力較弱
      model: qwen3:8b               # 8B 參數模型，適合本地運行
      base_url: http://localhost:11434  # Ollama 本地端點
    confidence_threshold: 0.5       # 開發時降低門檻（減少確認彈窗，提升開發效率）
    max_task_steps: 5               # 減少步驟數（本地 LLM 推理速度較慢）

  staging:
    llm:
      provider: anthropic
      model: claude-opus-4-20250514  # 與生產環境相同，測試真實行為
    confidence_threshold: 0.7       # 接近生產門檻（測試確認觸發頻率）

  production:
    llm:
      provider: anthropic
      model: claude-opus-4-20250514
    confidence_threshold: 0.75      # 生產門檻（平衡效率與安全）
    max_task_steps: 15              # 允許更長的推理鏈（複雜場景）
    audit_level: full               # 完整審計（記錄所有決策的推理過程）
```

**關鍵設計決策**：
- **分層配置**：`defaults` 定義基線，各環境只覆蓋差異參數。避免三個環境的完整配置大量重複。
- **confidence_threshold 分級**：開發 0.5 → 測試 0.7 → 生產 0.75。低門檻在開發時減少打擾，高門檻在生產時提高安全性。
- **LLM 切換**：開發用 Ollama（本地、免費、快速迭代），生產用 Anthropic（高品質、穩定 SLA）。配置驅動，不需要改代碼。

### 5.5.2 Prompt 版本管理

CCA 的 Prompt 變更需要版本控制，因為 Prompt 的修改直接影響 Agent 行為。一個詞的改動可能導致 CCA 的決策品質大幅變化。Prompt 版本管理確保每次變更都有記錄、可追溯、可回滾。

```python
# cca/prompt_manager.py
class PromptManager:
    """Prompt 版本管理器 — 追蹤每次 Prompt 變更"""

    def __init__(self, storage):
        self.storage = storage            # 存儲後端（如 PostgreSQL 或 S3）
        self.current_version = None       # 當前使用的 Prompt 版本

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
        """更新 Prompt，記錄版本與原因 — 每次變更都有完整記錄"""
        # 版本號基於時間戳：精確到秒，確保唯一性
        version = f"v{datetime.now().strftime('%Y%m%d%H%M%S')}"
        await self.storage.put(f"prompts/{version}", {
            "content": new_prompt,
            "author": author,                    # 誰修改的
            "change_reason": change_reason,      # 為什麼修改（CRITICAL：沒有原因不允許修改）
            "test_results": test_results,        # 修改前的測試結果（可選但強烈建議）
            "created_at": datetime.now().isoformat()
        })
        self.current_version = version          # 切換到新版本
        return version
```

**關鍵設計決策**：
- **時間戳版本號**：使用 `YYYYMMDDHHMMSS` 格式，比語義版本號（v1.2.3）更直觀 — 一看就知道是什麼時候改的。
- **change_reason 必填**：Prompt 變更必須記錄原因（如「優化了意圖識別的準確率」）。這在事後追溯時至關重要 — 「為什麼 7 月 15 日的意圖識別變差了？」→ 查 Prompt 版本歷史 → 找到 7 月 14 日的修改 → 原因是「簡化了 Prompt」。
- **test_results 記錄**：強烈建議在修改 Prompt 前後運行基準測試，並將結果記錄在版本元數據中。這樣可以直接比較不同版本的品質差異。

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
