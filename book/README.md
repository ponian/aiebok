# 雲原生 AI Native Agent Platform：構建企業級智能協同系統

**副標題：** 基於 CMU AIEBoK 與開源技術棧的實踐指南

**目標讀者：** 軟體工程師、AI 工程師、系統架構師、對構建智能企業級平台感興趣的技術領導者。

**核心理念：** 將 AI Agent 定位為平台運行的核心驅動力，結合雲原生技術的彈性與自動化，構建一個具備自主決策、協同工作、任務自動化和數據分析能力的企業級智能平台。

---

## 書籍結構

### 階段一：藍圖構建 (Top-Down) - 理論與架構設計

| 章節 | 標題 | 內容概要 |
|------|------|----------|
| [第 1 章](chapter-01.md) | 智能平台的黎明 | AI Native 與 Agent-Driven 定義、企業級智能平台趨勢、CMU AIEBoK 框架指引 |
| [第 2 章](chapter-02.md) | 核心架構藍圖 | Agent 生態系統宏觀架構、CCA、Specialized Agents、MCP、Letta、Portal、Cloud-Native |
| [第 3 章](chapter-03.md) | Agent 的智能與協同 | LLM 選型、Prompt Engineering、協同模式、記憶機制、可信度與安全 |
| [第 4 章](chapter-04.md) | 雲原生技術棧 | Kubernetes、Istio、OpenTelemetry、開源工具棧選型 |

### 階段二：細節深耕 (Deep Dive) - 組件設計與技術選型

| 章節 | 標題 | 內容概要 |
|------|------|----------|
| [第 5 章](chapter-05.md) | CCA 實現細節 | LLM Prompt 設計、LangGraph 實踐、Agent 調度、狀態管理 |
| [第 6 章](chapter-06.md) | Specialized Agents 構建 | Letta 定義 Agent、工具集成、RAG 應用 |
| [第 7 章](chapter-07.md) | MCP Service 詳解 | Protobuf Schema、gRPC 服務、消息隊列集成 |
| [第 8 章](chapter-08.md) | Kubernetes 雲原生部署 | Helm Charts、Istio 流量管理、CI/CD Pipeline |
| [第 9 章](chapter-09.md) | OpenTelemetry 實踐 | OTel instrumentation、Trace/Metrics/Logs 整合 |
| [第 10 章](chapter-10.md) | Portal Platform | Next.js 16 前端、FastAPI 後端、用戶管理、RBAC |

### 階段三：實作路線圖 (Roadmap) 與參考實作

| 章節 | 標題 | 內容概要 |
|------|------|----------|
| [第 11 章](chapter-11.md) | 實作路線圖 | MVP → 功能完善 → 生產加固 → 擴展 四階段路線圖 |
| [第 12 章](chapter-12.md) | 參考實作 MVP | IT 賬戶創建場景、完整專案結構、程式碼範例 |

---

## 技術棧概覽

| 層級 | 技術 | 授權 |
|------|------|------|
| Agent Framework | Letta (letta-ai/letta) | Apache 2.0 |
| 工作流編排 | LangGraph (langchain-ai/langgraph) | MIT |
| LLM 執行 | Ollama + Llama 4 / Qwen 3 | MIT |
| 通信協議 | gRPC + Protobuf | Apache 2.0 |
| 消息隊列 | NATS | Apache 2.0 |
| 容器編排 | Kubernetes | Apache 2.0 |
| 服務網格 | Istio | Apache 2.0 |
| 遙測 | OpenTelemetry | Apache 2.0 |
| 監控 | Prometheus + Grafana | Apache 2.0 / AGPL |
| 日誌 | Loki | AGPL |
| Portal Frontend | Next.js 16 + shadcn/ui | MIT |
| Portal Backend | FastAPI | MIT |

---

## CMU AIEBoK 對齊

本書內容遵循 CMU AI Engineering Body of Knowledge (AIEBoK) 框架作為整體指導原則，重點體現以下領域：

1. **AI System Design & Architecture** — 平台級架構模式
2. **AI System Trustworthiness** — 可信度、公平性、魯棒性
3. **AI System Scalability & Performance** — 雲原生架構下的擴展性
4. **AI System Observability & Monitoring** — 實時監控與可觀察性
5. **AI Model Development & Deployment Lifecycle Management** — Agent 的生命週期

---

## 架構方法論

本書採用 **Top-Down → Bottom-Up** 的方法：

1. **Top-Down (第 1-4 章):** 從宏觀架構藍圖出發，建立整體願景與技術方向
2. **Deep Dive (第 5-10 章):** 逐一深入每個關鍵組件的實現細節
3. **Bottom-Up (第 11-12 章):** 以可落地的實作路線圖和參考實現為基礎，漸進式建構

---

## 企業場景聚焦

初始場景聚焦於 **人力資源 (HR)** 與 **IT 支持** 部門，以 IT 賬戶創建作為 MVP 驗證場景，逐步擴展至完整的企業級 AI Native Agent Platform。
