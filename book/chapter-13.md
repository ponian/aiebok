# 附錄：核心術語表

> 「理解術語，是理解架構的第一步。本附錄收錄本書涉及的核心技術術語，按主題分類，供讀者快速查閱。」

本附錄收錄本書各章節中出現的技術術語、縮寫與專有名詞。每一個術語均提供英文原名、中文釋義及其在本書中的主要參照章節，方便讀者在閱讀過程中隨時查閱。

---

## AI Agent 核心概念

| 術語 | 英文 | 釋義 | 主要章節 |
|------|------|------|----------|
| AI Agent | AI Agent | 具備自主推理、規劃與執行能力的軟體實體。能理解用戶意圖、分解複雜任務、調用外部工具並整合結果。與傳統聊天機器人的根本區別在於其自主性與目標導向行為。 | 第 1 章 |
| AI Native | AI Native | 指平台的核心業務流程由 AI Agent 驅動，而非由預先硬編碼的業務邏輯驅動。AI 不是外掛或附加功能，而是平台運行的「大腦」。 | 第 1 章 |
| Agent-Driven | Agent-Driven | 與 AI Native 同義，強調 Agent 作為系統核心驅動力的角色。相對於 AI-Assisted（輔助）和 AI-Enhanced（增強），Agent-Driven 代表最高層次的 AI 整合。 | 第 1 章 |
| 自主性 (Autonomy) | Autonomy | Agent 在無需人類逐步指導下，自主規劃並執行任務的能力。是區分 AI Agent 與傳統軟體的關鍵特徵。 | 第 1 章 |
| 目標導向 | Goal-Oriented | Agent 以完成高層次目標為導向，而非執行固定流程。Agent 能根據目標動態調整執行策略。 | 第 1 章 |
| 環境感知 | Context-Aware | Agent 能感知並利用上下文信息（包括對話歷史、業務狀態、知識庫內容）來做出更準確的決策。 | 第 1 章 |
| 工具使用 (Tool Use) | Tool Use | Agent 動態選擇並調用外部工具或 API 來完成具體操作的能力。工具是 Agent 與外部世界交互的橋樑。 | 第 1、3 章 |
| 工具調用 | Tool Calling / Function Calling | LLM 根據用戶意圖自動選擇並調用預定義函數的機制。是 Agent 能夠執行實際操作的核心能力。 | 第 3 章 |
| ReAct 框架 | ReAct (Reasoning + Acting) | 2023 年提出的 Agent 框架，結合推理（Reasoning）與行動（Acting），使 LLM 能在推理和工具調用之間交替進行，完成多步驟任務。 | 第 1 章 |
| 多 Agent 協同 | Multi-Agent Collaboration | 多個 Agent 之間通過通信協議相互協調、共享上下文，共同完成複雜業務流程的工作模式。 | 第 2、3 章 |
| 協同模式 | Collaboration Patterns | Agent 之間交互的結構化模式，包括串行、並行、層級式、對等式等。 | 第 3 章 |
| RPA | Robotic Process Automation | 機器人流程自動化。傳統的「錄製-回放」式流程自動化方案，與 AI Agent 的「理解-規劃-執行」模式形成對比。 | 第 1 章 |

---

## 平台核心組件

| 術語 | 英文 | 釋義 | 主要章節 |
|------|------|------|----------|
| CCA | Central Coordinator Agent | 中央協調 Agent。平台的「大腦」，負責意圖識別、任務分解、Agent 調度與結果整合。七大核心職責包括：意圖識別、任務分解、Agent 調度、結果整合、錯誤處理、審計記錄、降級策略。 | 第 2、5 章 |
| Specialized Agent | Specialized Agent | 專用 Agent。專注於特定領域（如 HR、IT、Finance）的 Agent，由 CCA 調度執行具體任務。每個 Specialized Agent 擁有領域專屬的工具集與知識庫。 | 第 2、6 章 |
| HR Agent | HR Agent | 人力資源專用 Agent。負責處理員工查詢、入職流程、組織架構等 HR 相關業務。 | 第 2、6、12 章 |
| IT Agent | IT Agent | IT 支持專用 Agent。負責 AD 帳號創建、權限管理、設備分配等 IT 相關業務。 | 第 2、6、12 章 |
| Agent Registry | Agent Registry | Agent 註冊中心。管理所有可用 Agent 的能力描述、端點地址與狀態信息，支持動態發現與路由。 | 第 2 章 |
| Portal Platform | Portal Platform | 用戶與 AI Agent 交互的前端界面。提供對話界面、任務管理、審計面板、知識庫管理等功能。 | 第 2、10 章 |
| Agent 生態系統 | Agent Ecosystem | 由 CCA、Specialized Agents、MCP Service、Agent Registry、Portal 等組件構成的完整 Agent 協同體系。 | 第 2 章 |
| Agent 生命周期 | Agent Lifecycle | Agent 從創建、註冊、運行、更新到下線的完整管理過程。 | 第 6 章 |

---

## AI 與大語言模型

| 術語 | 英文 | 釋義 | 主要章節 |
|------|------|------|----------|
| LLM | Large Language Model | 大語言模型。基於 Transformer 架構的深度學習模型，能理解和生成自然語言。本書涉及的 LLM 包括 GPT-4、Claude、Llama、Qwen 等。 | 第 1、3 章 |
| Prompt Engineering | Prompt Engineering | 提示工程。設計和優化輸入給 LLM 的提示文本，以引導模型產生所需輸出的技術。在 Agent 系統中，系統提示（System Prompt）定義了 Agent 的角色、能力與行為邊界。 | 第 3 章 |
| System Prompt | System Prompt | 系統提示。定義 Agent 角色、行為規則與能力範圍的初始提示文本，在整個對話生命週期中持續生效。 | 第 3、5 章 |
| Few-Shot Learning | Few-Shot Learning | 少樣本學習。在提示中提供少量示例，幫助 LLM 理解所需的輸出格式與模式。 | 第 3 章 |
| Chain of Thought | Chain of Thought (CoT) | 思維鏈。讓 LLM 逐步展示推理過程的提示技術，能顯著提升複雜推理任務的準確性。 | 第 3 章 |
| RAG | Retrieval-Augmented Generation | 檢索增強生成。結合信息檢索與文本生成的技術，讓 LLM 在回答問題時能引用外部知識庫中的最新、最準確信息，減少幻覺（Hallucination）。 | 第 3、6 章 |
| Working Memory | Working Memory | 工作記憶。Agent 在單次對話或任務中可快速訪問的短期記憶，類似人類的工作記憶。 | 第 3 章 |
| Archival Memory | Archival Memory | 長期記憶。Agent 的持久化知識存儲，可跨對話保留歷史經驗、學到的模式與業務知識。 | 第 3 章 |
| Embedding | Embedding | 向量嵌入。將文本轉換為高維度數值向量的過程，使語義相似的文本在向量空間中距離更近，是語義搜索與 RAG 的基礎。 | 第 3 章 |
| 向量數據庫 | Vector Database | 專門用於存儲和檢索向量嵌入的數據庫系統，支持高效的相似度搜索。本書使用 ChromaDB 作為示例。 | 第 3、6 章 |
| 語義搜索 | Semantic Search | 基於文本語義（而非關鍵字精確匹配）的搜索方式，通過向量相似度計算實現。 | 第 3 章 |
| 幻覺 (Hallucination) | Hallucination | LLM 生成看似合理但實際上不準確或完全虛構的信息的現象。RAG 和可觀測性監控是應對幻覺的關鍵手段。 | 第 3、9 章 |
| Temperature | Temperature | LLM 的生成溫度參數。值越低輸出越確定和保守，值越高輸出越多樣和隨機。Agent 系統中通常使用較低的 Temperature 以確保輸出一致性。 | 第 3 章 |
| Top-K / Top-P | Top-K / Top-P | LLM 的採樣參數。Top-K 限制從前 K 個最可能的詞中選擇，Top-P（核採樣）限制從累計概率達到 P 的詞中選擇。 | 第 3 章 |
| Token | Token | LLM 處理文本的基本單位。中文約 1-2 個字為一個 Token，英文約一個詞或子詞為一個 Token。Token 消耗直接影響 API 費用與響應延遲。 | 第 3、9 章 |
| Context Window | Context Window | LLM 一次能處理的最大 Token 數量。限制了 Agent 可利用的歷史對話長度與輸入信息量。 | 第 3 章 |
| Streaming | Streaming | LLM 逐 Token 串流輸出回應的方式，而非等待完整回應後一次性返回。可顯著改善用戶感知延遲。 | 第 3 章 |
| Structured Output | Structured Output | 要求 LLM 以特定結構化格式（如 JSON Schema）輸出結果的技術，確保 Agent 的輸出能被下游系統可靠解析。 | 第 3 章 |
| LangGraph | LangGraph | LangChain 團隊開發的工作流編排框架。支持有向圖結構的 Agent 工作流定義，包含條件分支、循環、人工介入等高級特性。 | 第 3、5 章 |
| LangChain | LangChain | 用於構建 LLM 應用的開源框架，提供模型調用、提示管理、工具整合、記憶管理等基礎組件。 | 第 3 章 |
| Letta | Letta | 開源 Agent 框架（前身為 MemGPT），核心特性包括持久化記憶管理、工具使用、多 Agent 支持。本書以 Letta 作為 Agent 實現的基礎框架。 | 第 2、5、6 章 |
| Ollama | Ollama | 本地 LLM 執行引擎。支持在本地環境中運行開源大語言模型（如 Llama、Qwen），無需依賴外部 API，保護數據隱私。 | 第 4 章 |
| Llama | Llama | Meta 開發的開源大語言模型系列。本書使用 Llama 4 作為推薦的本地方案之一。 | 第 4 章 |
| Qwen | Qwen (通義千問) | 阿里巴巴開發的大語言模型系列。本書使用 Qwen 3 作為推薦的本地方案之一。 | 第 4 章 |
| CMU AIEBoK | CMU AI Engineering Body of Knowledge | CMU AI 工程知識體系。卡內基梅隆大學提出的 AI 工程學科知識框架，涵蓋 AI 系統設計、可信度、擴展性、可觀測性等領域。本書以此作為整體指導原則。 | 第 1 章 |

---

## 通信協議與模式

| 術語 | 英文 | 釋義 | 主要章節 |
|------|------|------|----------|
| MCP | Model Context Protocol | 模型上下文協議。Anthropic 主導的開放標準，定義 LLM/Agent 與外部工具、數據源之間的交互協議。基於 JSON-RPC 2.0，支持工具調用、資源查詢與提示模板。 | 第 2、7 章 |
| A2A | Agent-to-Agent | Agent 對 Agent 通信協議。Google 主導並已捐贈予 Linux Foundation 的開放標準，定義 Agent 之間的通信、發現與協同規範。與 MCP 互補：MCP 管 Agent-工具交互，A2A 管 Agent-Agent 交互。 | 第 2 章 |
| MACP | Multi-Agent Collaboration Protocol | 多 Agent 協同協議。IETF 的 Internet-Draft，定義 Agent 註冊、能力發現與安全交互的規範。 | 第 2 章 |
| JSON-RPC 2.0 | JSON-RPC 2.0 | 一種輕量級的遠程過程調用（RPC）協議，使用 JSON 作為數據格式。MCP 協議的底層傳輸協議。 | 第 7 章 |
| gRPC | gRPC | Google 開發的高性能遠程過程調用框架，基於 HTTP/2 與 Protocol Buffers。支持雙向串流、低延遲通信。 | 第 4、7 章 |
| Protocol Buffers / Protobuf | Protocol Buffers | Google 開發的二進制序列化格式。比 JSON 更緊湊、解析更快，是 gRPC 的默認序列化方案。 | 第 4、7 章 |
| SSE | Server-Sent Events | 伺服器推送事件。一種單向的伺服器到客戶端的串流通信機制，適用於 LLM 回應的即時推送。 | 第 7 章 |
| WebSocket | WebSocket | 全雙工通信協議。支持客戶端與伺服器之間的即時雙向通信，用於 Portal 的即時消息推送。 | 第 10 章 |
| NATS | NATS | 高性能開源消息隊列系統。以極低延遲和高吞吐量著稱，本書用於 Agent 之間的異步消息通信。支持 Pub/Sub（發布/訂閱）模式。 | 第 4、7 章 |
| Pub/Sub | Publish/Subscribe | 發布/訂閱模式。消息的生產者（Publisher）將消息發布到主題（Subject），訂閱者（Subscriber）從訂閱的主題接收消息，實現發送方與接收方的解耦。 | 第 7 章 |
| Subject | Subject | NATS 中的消息主題。消息按 Subject 路由，訂閱者通過訂閱特定 Subject 來接收相關消息。 | 第 7 章 |
| REST API | REST API | 基於 HTTP 協議的 API 設計風格，使用標準 HTTP 方法（GET/POST/PUT/DELETE）進行資源操作。 | 第 7 章 |
| HTTP/HTTPS | HTTP/HTTPS | 超文本傳輸協議（及其安全版本）。Web 應用的基礎通信協議，HTTPS 通過 TLS 加密保障傳輸安全。 | 第 4 章 |
| TLS | Transport Layer Security | 傳輸層安全協議。加密網絡通信以防止竊聽和篡改，HTTPS 即 HTTP over TLS。 | 第 4、8 章 |
| CORS | Cross-Origin Resource Sharing | 跨來源資源共享。瀏覽器的安全機制，控制網頁對不同來源資源的訪問權限。 | 第 10 章 |

---

## 雲原生基礎設施

| 術語 | 英文 | 釋義 | 主要章節 |
|------|------|------|----------|
| Docker | Docker | 容器化平台。將應用及其依賴打包為標準化的容器鏡像，確保在任何環境中一致運行。 | 第 4 章 |
| Container | Container | 容器。輕量級的作業系統級虛擬化技術，共享宿主機內核但隔離文件系統、網絡與進程。 | 第 4 章 |
| Kubernetes (K8s) | Kubernetes | Google 開源的容器編排系統。自動化容器的部署、擴縮容、網絡管理與自我修復。本書的生產環境部署平台。 | 第 4、8 章 |
| Pod | Pod | Kubernetes 中最小的部署單位。一個 Pod 包含一個或多個緊密關聯的容器，共享網絡命名空間與存儲卷。 | 第 8 章 |
| Deployment | Deployment | Kubernetes 的無狀態應用部署控制器。管理 Pod 的副本數、滾動更新與回滾。 | 第 8 章 |
| StatefulSet | StatefulSet | Kubernetes 的有狀態應用部署控制器。為 Pod 提供穩定的網絡標識與持久化存儲，適用於數據庫、消息隊列等有狀態服務。 | 第 8 章 |
| DaemonSet | DaemonSet | Kubernetes 控制器。確保在所有（或指定）節點上運行一個 Pod 副本，適用於日誌收集、監控代理等。 | 第 8 章 |
| Service | Service | Kubernetes 的網絡抽象。為一組 Pod 提供穩定的網絡端點（IP 地址和 DNS 名稱），實現負載均衡與服務發現。 | 第 8 章 |
| Ingress | Ingress | Kubernetes 的 HTTP 路由規則。管理外部 HTTP/HTTPS 流量如何到達集群內的 Service，支持基於路徑和域名的路由。 | 第 8 章 |
| Egress | Egress | 出站流量控制。定義 Pod 向外部網絡發送流量的規則，是零信任網絡的重要組成部分。 | 第 8 章 |
| Namespace | Namespace | Kubernetes 的邏輯隔離機制。將集群資源劃分為多個虛擬集群，用於環境隔離（如 dev/staging/prod）和資源配額管理。 | 第 8 章 |
| ConfigMap | ConfigMap | Kubernetes 的配置管理對象。存儲非機密的鍵值對配置數據，可在 Pod 啟動時注入為環境變量或文件。 | 第 8 章 |
| Secret | Secret | Kubernetes 的敏感信息管理對象。存儲密碼、API Key、證書等敏感數據，Base64 編碼存儲（非加密），可掛載為文件或環境變量。 | 第 8 章 |
| ServiceAccount | ServiceAccount | Kubernetes 的 Pod 身份認證對象。為 Pod 提供集群內的身分標識和 API 訪問權限。 | 第 8 章 |
| RBAC | Role-Based Access Control | 基於角色的訪問控制。通過角色（Role）綁定（Binding）來管理用戶或服務帳號對集群資源的訪問權限。 | 第 8、10 章 |
| NetworkPolicy | NetworkPolicy | Kubernetes 的網絡策略。定義 Pod 之間以及 Pod 與外部網絡之間的通信規則，實現微分段（Microsegmentation）。 | 第 8 章 |
| PVC | Persistent Volume Claim | 持久化存儲卷聲明。Pod 向集群申請存儲空間的方式，與實際的物理存儲（PV）解耦。 | 第 8 章 |
| PV | Persistent Volume | 持久化存儲卷。集群級別的存儲資源，由管理員預先配置或通過 StorageClass 動態創建。 | 第 8 章 |
| HPA | Horizontal Pod Autoscaler | 水平 Pod 自動擴縮器。根據 CPU 使用率、內存使用率或自定義指標自動調整 Pod 的副本數。 | 第 8 章 |
| PDB | Pod Disruption Budget | Pod 干擾預算。限制自願干擾（如節點維護、升級）同時中斷的 Pod 數量，保障應用可用性。 | 第 8 章 |
| GPU | Graphics Processing Unit | 圖形處理單元。用於加速 LLM 推理的並行計算硬件。本書的 Ollama 推薦配置。 | 第 8 章 |
| Helm | Helm | Kubernetes 的應用打包與管理工具。通過 Charts（圖表）定義、安裝和升級 Kubernetes 應用。 | 第 4、8 章 |
| CI/CD | Continuous Integration / Continuous Delivery | 持續整合 / 持續交付。自動化構建、測試、部署的實踐與工具鏈，確保代碼變更快速、可靠地交付到生產環境。 | 第 4 章 |
| Zero Downtime Update | Zero Downtime Update | 零停機更新。在不中斷服務的情況下部署新版本的策略，通過滾動更新（Rolling Update）和健康檢查實現。 | 第 8 章 |
| Rolling Update | Rolling Update | 滾動更新。逐步替換舊版本 Pod 為新版本 Pod 的部署策略，結合 PDB 確保更新過程中始終有足夠的可用 Pod。 | 第 8 章 |
| Graceful Shutdown | Graceful Shutdown | 優雅關閉。Pod 收到終止信號後，完成當前正在處理的請求再退出的機制，避免請求丟失。 | 第 8 章 |
| Health Check | Health Check | 健康檢查。Kubernetes 通過 Liveness（存活探針）、Readiness（就緒探針）和 Startup（啟動探針）來判斷 Pod 狀態。 | 第 8 章 |

---

## 服務網格

| 術語 | 英文 | 釋義 | 主要章節 |
|------|------|------|----------|
| Service Mesh | Service Mesh | 服務網格。處理服務間通信的基礎設施層，提供流量管理、安全（mTLS）、可觀測性等功能，對應用透明。 | 第 4 章 |
| Istio | Istio | CNCF 開源的服務網格實現。本書使用 Istio 管理 Agent 之間的流量路由、安全通信與可觀測性。 | 第 4 章 |
| Envoy | Envoy | 高性能的 L7 代理與服務網格數據平面。Istio 使用 Envoy 作為 Sidecar 代理，攔截和管理所有網絡流量。 | 第 4、8 章 |
| Sidecar | Sidecar | 側車模式。與應用 Pod 共存的輔助容器（如 Envoy 代理），處理網絡通信、安全、監控等橫切關注點。 | 第 4、8 章 |
| VirtualService | VirtualService | Istio 的虛擬服務。定義流量路由規則，控制流量如何到達服務。支持金絲雀發布、A/B 測試等。 | 第 8 章 |
| DestinationRule | DestinationRule | Istio 的目標規則。定義到達特定服務的流量策略，如負載均衡、連接池、熔斷器。 | 第 8 章 |
| mTLS | Mutual TLS | 雙向 TLS 認證。服務網格中的服務間通信加密方式，雙方互相驗證證書，實現零信任網絡。 | 第 8 章 |

---

## 可觀測性與監控

| 術語 | 英文 | 釋義 | 主要章節 |
|------|------|------|----------|
| OpenTelemetry (OTel) | OpenTelemetry | CNCF 的開源可觀測性框架。統一 Traces（追蹤）、Metrics（指標）、Logs（日誌）三大信號的採集、傳輸與處理。本書的核心可觀測性方案。 | 第 4、9 章 |
| OTel SDK | OTel SDK | OpenTelemetry 的軟體開發套件。應用程序通過 SDK 嵌入遙測數據的採集邏輯。 | 第 9 章 |
| OTel Collector | OTel Collector | OpenTelemetry 的數據收集代理。接收、處理並轉發遙測數據到不同的後端存儲系統。 | 第 9 章 |
| OTLP | OpenTelemetry Protocol | OpenTelemetry 的傳輸協議。用於在 SDK、Collector 與後端之間傳輸遙測數據，支持 gRPC 和 HTTP。 | 第 9 章 |
| Trace / Tracing | Trace / Distributed Tracing | 分佈式追蹤。追蹤一個請求在多個服務之間的完整旅程。每個服務處理步驟生成一個 Span，所有 Span 組成一棵 Trace 樹。 | 第 9 章 |
| Span | Span | 追蹤的基本單位。表示系統中一次具體的操作（如 API 調用、LLM 推理），包含開始時間、持續時間、元數據與狀態。 | 第 9 章 |
| Metrics | Metrics | 結構化數值指標。用於量化系統行為（如請求數、延遲分佈、錯誤率），支持即時告警與趨勢分析。 | 第 9 章 |
| Logs | Logs | 結構化日誌。時間序列的離散事件記錄，用於事後分析和問題排查。本書推薦使用結構化 JSON 格式。 | 第 9 章 |
| Prometheus | Prometheus | CNCF 開源的時序數據庫與監控系統。採集和存儲指標數據，支持強大的查詢語言 PromQL 與告警規則。 | 第 4、9 章 |
| Grafana | Grafana | 開源的可觀測性儀表板平台。整合 Prometheus、Loki 等數據源，提供可視化的監控面板與告警。 | 第 4、9 章 |
| Jaeger | Jaeger | CNCF 開源的分佈式追蹤系統。收集、存儲和可視化分佈式追蹤數據，本書用於 Agent 之間的請求追蹤。 | 第 9 章 |
| Loki | Loki | Grafana 實驗室開發的日誌聚合系統。專為容器化環境設計，與 Grafana 深度整合，使用 LogQL 查詢。 | 第 4、9 章 |
| LogQL | LogQL | Loki 的查詢語言。類似 Prometheus 的 PromQL，用於過濾和查詢日誌數據。 | 第 9 章 |
| AlertManager | AlertManager | Prometheus 的告警管理組件。接收 Prometheus 發送的告警，進行去重、分組、路由與通知（郵件、Slack 等）。 | 第 9 章 |
| SLA | Service Level Agreement | 服務水平協議。服務提供者與使用者之間的正式協議，定義可接受的服務質量指標（如可用性 99.9%）。 | 第 9 章 |
| SLO | Service Level Objective | 服務水平目標。團隊內部設定的可衡量目標（如 P95 延遲 < 2 秒），用於指導工程決策。 | 第 9 章 |
| SLI | Service Level Indicator | 服務水平指標。實際測量的服務質量數據（如實際 P95 延遲），用於判斷是否達成 SLO。 | 第 9 章 |
| P50 / P95 / P99 | Percentile | 百分位數。P50（中位數）、P95（第 95 百分位）、P99（第 99 百分位）用於衡量延遲分佈，比平均值更能反映用戶體驗。 | 第 9 章 |
| LLM 可觀測性 | LLM Observability | 針對 LLM 特有的監控模式，包括 Token 消耗追蹤、推理延遲分析、幻覺偵測、提示版本管理等。 | 第 9 章 |

---

## 數據存儲

| 術語 | 英文 | 釋義 | 主要章節 |
|------|------|------|----------|
| PostgreSQL | PostgreSQL | 開源的物件關聯式數據庫。本書用於存儲 Agent 狀態、任務記錄、審計日誌等結構化數據。 | 第 4 章 |
| ChromaDB | ChromaDB | 開源的向量數據庫。專為 AI 應用設計，用於存儲和檢索文本嵌入向量，支持 RAG 知識庫。 | 第 3、6 章 |
| Redis | Redis | 高性能內存數據存儲。用於緩存、會話管理與即時數據處理。 | 第 4 章 |
| etcd | etcd | 分佈式鍵值存儲系統。Kubernetes 使用 etcd 存儲集群狀態數據，本書也用於 Agent 的服務發現。 | 第 4 章 |
| Elasticsearch | Elasticsearch | 分佈式搜索與分析引擎。用於全文搜索、日誌分析與結構化數據查詢。 | 第 4 章 |

---

## 安全與認證

| 術語 | 英文 | 釋義 | 主要章節 |
|------|------|------|----------|
| OAuth 2.0 | OAuth 2.0 | 開放授權框架。允許第三方應用在不暴露用戶密碼的情況下，獲得對資源的有限訪問權限。 | 第 10 章 |
| OIDC | OpenID Connect | 基於 OAuth 2.0 的身分認證層。在 OAuth 2.0 之上添加了用戶身分信息的標準化協議。 | 第 10 章 |
| JWT | JSON Web Token | JSON 網路令牌。用於在各方之間安全傳遞聲明（Claims）的緊湊型令牌格式。通常用於 API 認證與授權。 | 第 10 章 |
| API Key | API Key | API 金鑰。用於識別和驗證 API 調用者身分的字符串。簡單但安全性較低，通常用於伺服器對伺服器通信。 | 第 7 章 |
| Zero Trust | Zero Trust | 零信任安全模型。不信任任何網絡內外的實體，所有訪問請求都需要驗證。本書通過 mTLS、RBAC 與 NetworkPolicy 實現零信任。 | 第 8 章 |
| CSRF | Cross-Site Request Forgery | 跨站請求偽造。一種攻擊方式，誘騙已認證用戶執行非預期操作。本書的 Portal 通過 Origin 驗證與 CSRF Token 防護。 | 第 10 章 |

---

## 架構模式與設計概念

| 術語 | 英文 | 釋義 | 主要章節 |
|------|------|------|----------|
| Circuit Breaker | Circuit Breaker | 熔斷器模式。當下游服務失敗率超過閾值時自動「熔斷」（停止調用），避免級聯故障。一段時間後自動進入「半開」狀態嘗試恢復。 | 第 7 章 |
| 降級策略 | Graceful Degradation | 當部分服務不可用時，系統仍能提供有限但可用功能的策略。例如 LLM 不可用時退回到規則引擎。 | 第 5 章 |
| 微服務 | Microservices | 將大型應用拆分為一組小型、獨立部署的服務的架構風格。每個服務專注於單一業務能力。 | 第 2 章 |
| Domain-Driven Design (DDD) | Domain-Driven Design | 領域驅動設計。以業務領域為核心的軟體設計方法论，通過限界上下文（Bounded Context）劃分系統邊界。 | 第 2 章 |
| Sidecar Pattern | Sidecar Pattern | 側車設計模式。在主應用旁邊部署輔助容器，處理日誌、監控、網絡代理等橫切關注點。 | 第 4 章 |
| Event-Driven Architecture | Event-Driven Architecture | 事件驅動架構。組件通過發布和訂閱事件來通信，實現高度解耦。本書的 NATS 消息隊列即為事件驅動的核心。 | 第 7 章 |
| API Gateway | API Gateway | API 網關。統一的 API 入口點，處理認證、限流、路由、協議轉換等橫切關注點。 | 第 7 章 |
| Data Plane / Control Plane | Data Plane / Control Plane | 數據平面 / 控制平面。數據平面處理實際的業務流量（如 Envoy 代理），控制平面管理配置與策略（如 Istiod）。 | 第 4、8 章 |
| Canopy / Canary | Canary Deployment | 金絲雀發布。先將新版本部署到一小部分流量上，觀察無異常後再逐步擴大到全部流量。 | 第 8 章 |
| Mock Service | Mock Service | 模擬服務。在測試或開發環境中模擬外部系統（如 AD API、HR API）的行為，用於端到端測試。 | 第 12 章 |
| MCP Tool | MCP Tool | MCP 工具。遵循 MCP 協議規範的可調用工具，每個工具定義了名稱、描述、輸入參數 schema 與執行邏輯。 | 第 7 章 |
| 知識庫 | Knowledge Base | 結構化的領域知識存儲。通過 RAG 技術與 Agent 整合，使 Agent 能查詢最新的業務知識與文檔。 | 第 6 章 |

---

> **使用建議：** 本術語表按照主題分類組織。若需查找特定術語，建議先判斷其所屬主題（如「這是一個雲原生概念」→ 查閱「雲原生基礎設施」一節），再在對應分類中查找。各術語的「主要章節」欄位指向本書中該術語首次出現或深入講解的章節，方便進一步閱讀。
