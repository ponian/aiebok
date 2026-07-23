# 雲原生 AI Native Agent Platform：構建企業級智能協同系統

**副標題：** 基於 CMU AIEBoK 與開源技術棧的實踐指南

**目標讀者：** 軟體工程師、AI 工程師、系統架構師、對構建智能企業級平台感興趣的技術領導者。

**核心理念：** 將 AI Agent 定位為平台運行的核心驅動力，結合雲原生技術的彈性與自動化，構建一個具備自主決策、協同工作、任務自動化和數據分析能力的企業級智能平台。

---

## 書籍結構

### 階段一：藍圖構建 (Top-Down) - 理論與架構設計

| 章節 | 標題 | 內容概要 |
|------|------|----------|
| [第 1 章](chapter-01.md) | 智能平台的黎明 — AI Native Agent Platform 的願景與挑戰 | AI Native 與 Agent-Driven 定義、Agent 核心特徵、企業級智能平台趨勢、超越傳統 ERP/CRM、CMU AIEBoK 框架指引、架構方法論、目標讀者與前置知識、ROI 分析與商業論證、市場定位與競爭分析 |
| [第 2 章](chapter-02.md) | 核心架構藍圖 — 一個 Agent 生態系統 | 平台頂層視圖與設計哲學、CCA 七大核心職責、Specialized Agents 設計、MCP Service 標準化通信、A2A Agent-to-Agent 通信模式、Letta Agent Framework 集成、Portal Platform 人機交互、Cloud-Native 基礎、組件交互全景（完整請求旅程） |
| [第 3 章](chapter-03.md) | AI Native 的基石 — Agent 的智能與協同 | LLM 選型五維度權衡、Prompt Engineering for Agents、Agent 協同模式與 LangGraph 工作流編排、記憶與知識獲取（Working/Archival/RAG）、可信度、安全與倫理考量 |
| [第 4 章](chapter-04.md) | 雲原生技術棧的選擇與理由 | Docker 容器化最佳實踐、Kubernetes 核心概念、Istio 服務網格、OpenTelemetry 統一遙測、開源工具棧總覽、NATS 高性能消息隊列、Helm Charts 應用打包、CI/CD Pipeline 基礎 |

### 階段二：細節深耕 (Deep Dive) - 組件設計與技術選型

| 章節 | 標題 | 內容概要 |
|------|------|----------|
| [第 5 章](chapter-05.md) | CCA 實現細節 — 中央協調 Agent 的設計與實踐 | CCA 整體架構（Letta Agent 實現）、專屬工具集設計、結構化系統提示、意圖識別與任務分解、審計與合規機制、錯誤處理與降級策略、配置管理 |
| [第 6 章](chapter-06.md) | Specialized Agents 構建 — 領域專家的實現 | Agent 生命週期管理、IT Agent 完整實現（AD 帳號/權限/通知）、HR Agent 完整實現（員工查詢/創建）、RAG 知識庫集成、Agent 測試與驗證、版本管理 |
| [第 7 章](chapter-07.md) | MCP Service 詳解 — 多 Agent 協同的核心引擎 | MCP 協議深度解析（JSON-RPC 2.0）、MCP Service 核心實現、CCA 與 MCP 協同流程、NATS 消息隊列集成、可觀測性集成、安全設計、SSE 串流即時回應、熔斷器模式（Circuit Breaker）、工具版本管理 |
| [第 8 章](chapter-08.md) | Kubernetes 雲原生部署 — 生產環境的基石 | 集群架構設計與 Namespace 隔離、CCA Agent K8s 部署、Specialized Agents 部署、密鑰管理（Secrets）、網絡策略（NetworkPolicy）、Helm Charts 封裝、零停機更新、PodDisruptionBudget、GPU 調度（Ollama）、PVC 存儲、ServiceAccount 與 RBAC |
| [第 9 章](chapter-09.md) | OpenTelemetry 實踐 — 多 Agent 系統的可觀測性 | AI Agent 可觀測性挑戰、分佈式追蹤（Traces）Span 設計、結構化指標收集（Metrics）、結構化日誌（Logs）、Grafana 儀表板、告警規則、端到端可觀測性實戰、LLM 專屬可觀測性模式（Token 成本/幻覺偵測）、OTel Collector Pipeline 配置、日誌跨 Agent 關聯 |
| [第 10 章](chapter-10.md) | Portal Platform — 用戶與 AI Agent 的交互界面 | Portal 功能架構、對話界面與消息流設計、任務管理面板、審計面板、知識庫管理、實時監控面板、OAuth2/OIDC 認證集成、RBAC 中間件、錯誤處理 UX、對話線程管理 |

### 階段三：實作路線圖 (Roadmap) 與參考實作

| 章節 | 標題 | 內容概要 |
|------|------|----------|
| [第 11 章](chapter-11.md) | 實作路線圖 — 從 MVP 到生產環境 | 四階段實施路線（MVP → 功能完善 → 生產加固 → 擴展）、各階段任務清單與技術架構、風險管理、團隊組建與技能矩陣、成本估算、關鍵績效指標（KPI）、詳細里程碑、漸進式遷移策略、變革管理、質量保證策略 |
| [第 12 章](chapter-12.md) | 參考實作 MVP — 新員工入職全流程演示 | 項目結構總覽、Docker Compose 一鍵啟動、核心代碼實現（CCA/HR Agent/IT Agent/MCP Service）、Mock 服務（AD API/HR API）、快速啟動指南、進階擴展方向、Agent 系統提示設計、LLM 客戶端實現、知識庫初始化腳本、端對端測試腳本 |

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

初始場景聚焦於 **人力資源 (HR)** 與 **IT 支持** 部門，以 IT 帳號創建作為 MVP 驗證場景，逐步擴展至完整的企業級 AI Native Agent Platform。
