# PROJECT: AIEBOK

**Type**: Technical book (Traditional Chinese)
**Topic**: Cloud-Native AI Native Agent Platform architecture
**Framework**: CMU AI Engineering Body of Knowledge (AIEBoK)

## STRUCTURE

```
aiebok/
├── book/                    # All chapter content (12 chapters, zh-TW)
│   ├── README.md            # Book overview & TOC
│   └── chapter-{01..12}.md  # Chapters
├── ai-agent-platform/       # Reference implementation (MVP code)
│   ├── agents/              # cca/, hr_agent/, it_agent/
│   ├── mcp_service/         # MCP tool registry & routing
│   ├── mocks/               # ad-api/, hr-api/ (simulated backends)
│   ├── portal/              # backend/ (FastAPI) + frontend/ (Next.js 16)
│   ├── knowledge/           # RAG vector store setup
│   ├── scripts/             # seed_knowledge.sh, verify_setup.sh
│   ├── tests/               # test_e2e_onboarding.py, performance/
│   └── docker-compose.yml   # Full stack orchestration (13 services)
└── OpenRouter Chat*.md      # Design discussion transcript
```

## REFERENCE IMPLEMENTATION

`ai-agent-platform/` is the complete working code that Chapter 12 documents. It's a Docker Compose stack with 13 services.

**Run it:**
```bash
cd ai-agent-platform
cp .env.example .env
docker compose up -d
docker compose ps              # verify all healthy
# Test: curl -X POST http://localhost:9112/task \
#   -H "Content-Type: application/json" \
#   -d '{"content": "新員工張小明明天入職市場部擔任產品經理", "user_id": "hr_manager_001"}'
```

**Prereqs:** Docker Compose V2, 16GB+ RAM, NVIDIA GPU recommended (Ollama).

**Key ports:** CCA=9112, MCP=9109, HR Agent=9110, IT Agent=9111, Portal=9114, PostgreSQL=9101, NATS=9103.

## WHERE TO LOOK

| Task | Location | Notes |
|------|----------|-------|
| Book structure/TOC | `book/README.md` | Master index |
| Architecture diagrams | `book/chapter-02.md` | Mermaid diagrams |
| Code examples | `book/chapter-12.md` | MVP reference impl |
| Tech stack decisions | `book/chapter-04.md` | Cloud-native choices |
| Design discussion context | `OpenRouter Chat*.md` | Original requirements |

## WRITING CONVENTIONS

- **Language**: Traditional Chinese (zh-TW) for prose; English for technical terms
- **Code blocks**: Use fenced code blocks with language tags
- **Diagrams**: Mermaid syntax for architecture diagrams
- **Tables**: Markdown tables for comparisons and specifications
- **Citations**: Inline references to open-source projects with GitHub links

## TECHNICAL STACK (from book)

| Layer | Technology | License |
|-------|------------|---------|
| Agent Framework | Letta (letta-ai/letta) | Apache 2.0 |
| Workflow Orchestration | LangGraph | MIT |
| LLM Runtime | Ollama + Llama 4 / Qwen 3 | MIT |
| Communication | gRPC + Protobuf | Apache 2.0 |
| Message Queue | NATS | Apache 2.0 |
| Container Orchestration | Kubernetes | Apache 2.0 |
| Service Mesh | Istio | Apache 2.0 |
| Observability | OpenTelemetry | Apache 2.0 |
| Monitoring | Prometheus + Grafana | Apache 2.0 / AGPL |
| Portal Frontend | Next.js 16 + shadcn/ui | MIT |
| Portal Backend | FastAPI | MIT |

## ANTI-PATTERNS

- Do NOT mix Simplified Chinese (zh-CN) with Traditional Chinese (zh-TW)
- Do NOT add code examples without corresponding explanation in prose
- Do NOT reference proprietary/closed-source tools (prefer MIT/Apache 2.0)
- Do NOT skip the CMU AIEBoK alignment sections

## CMU AIEBoK ALIGNMENT

The book follows CMU AIEBoK as guiding framework, focusing on:
1. AI System Design & Architecture
2. AI System Trustworthiness
3. AI System Scalability & Performance
4. AI System Observability & Monitoring
5. AI Model Development & Deployment Lifecycle Management

## METHODOLOGY

Top-Down → Bottom-Up approach:
1. **Chapters 1-4**: Blueprint (macro architecture)
2. **Chapters 5-10**: Deep Dive (component details)
3. **Chapters 11-12**: Implementation (roadmap + MVP)
