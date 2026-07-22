# PROJECT: AIEBOK

**Type**: Technical book (Traditional Chinese)
**Topic**: Cloud-Native AI Native Agent Platform architecture
**Framework**: CMU AI Engineering Body of Knowledge (AIEBoK)

## STRUCTURE

```
aiebok/
├── book/                    # All chapter content
│   ├── README.md            # Book overview & TOC
│   ├── chapter-01.md        # Ch1: Vision & Challenges
│   ├── chapter-02.md        # Ch2: Core Architecture Blueprint
│   ├── chapter-03.md        # Ch3: Agent Intelligence & Collaboration
│   ├── chapter-04.md        # Ch4: Cloud-Native Tech Stack
│   ├── chapter-05.md        # Ch5: CCA Implementation Details
│   ├── chapter-06.md        # Ch6: Specialized Agents Construction
│   ├── chapter-07.md        # Ch7: MCP Service Deep Dive
│   ├── chapter-08.md        # Ch8: Kubernetes Deployment
│   ├── chapter-09.md        # Ch9: OpenTelemetry Practice
│   ├── chapter-10.md        # Ch10: Portal Platform
│   ├── chapter-11.md        # Ch11: Implementation Roadmap
│   └── chapter-12.md        # Ch12: Reference Implementation MVP
└── OpenRouter Chat*.md      # Design discussion transcript
```

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
| LLM Runtime | Ollama + Llama 3 / Mistral | MIT |
| Communication | gRPC + Protobuf | Apache 2.0 |
| Message Queue | NATS | Apache 2.0 |
| Container Orchestration | Kubernetes | Apache 2.0 |
| Service Mesh | Istio | Apache 2.0 |
| Observability | OpenTelemetry | Apache 2.0 |
| Monitoring | Prometheus + Grafana | Apache 2.0 / AGPL |
| Portal Frontend | Next.js 14 + shadcn/ui | MIT |
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
