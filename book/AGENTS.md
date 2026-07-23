# BOOK: Cloud-Native AI Native Agent Platform

**Target audience**: Software engineers, AI engineers, system architects
**Language**: Traditional Chinese (zh-TW) with English technical terms

## CHAPTER STRUCTURE

Each chapter follows this pattern:
1. Opening quote (epigraph)
2. Introduction paragraph (1-2 sentences)
3. Numbered sections (1.1, 1.2, ...)
4. Subsections with code examples where applicable
5. Summary/transition to next chapter

## WRITING STYLE

- Professional but accessible technical prose
- Use tables for comparisons (e.g., Traditional ERP vs AI Native)
- Use Mermaid diagrams for architecture visualization
- Code examples should be runnable (Python/TypeScript)
- Include real GitHub project references with links

## CHAPTER MAP

| Chapter | Focus | Key Components |
|---------|-------|----------------|
| 01 | Vision | AI Native definition, Agent characteristics, enterprise trends |
| 02 | Architecture | CCA, Specialized Agents, MCP, Letta, Portal, Cloud-Native |
| 03 | Intelligence | LLM selection, Prompt Engineering, collaboration patterns |
| 04 | Tech Stack | Kubernetes, Istio, OpenTelemetry, open-source tools |
| 05 | CCA | LangGraph, state management, task decomposition |
| 06 | Agents | Letta framework, tool integration, RAG |
| 07 | MCP | Protobuf, gRPC, message queues |
| 08 | Deployment | Helm, Istio traffic management, CI/CD |
| 09 | Observability | OTel instrumentation, traces, metrics, logs |
| 10 | Portal | Next.js 16 frontend, FastAPI backend, user management, RBAC |
| 11 | Roadmap | MVP → Production → Scale phases |
| 12 | Reference Impl | Complete code for IT account creation scenario |

## CODE EXAMPLE STANDARDS

- Python for agent implementations (Letta, LangGraph)
- TypeScript/React for portal frontend
- YAML for Kubernetes/Helm configurations
- Protobuf for MCP service definitions
- All examples should reference actual open-source projects

## MERMAID DIAGRAMS

Use mermaid for:
- Architecture diagrams (graph TD)
- Sequence diagrams (sequenceDiagram)
- Component relationships

Keep diagrams focused - one concept per diagram.

## REFERENCE IMPLEMENTATION (Ch12)

The MVP demonstrates:
- IT account creation workflow
- CCA + IT Agent + HR Agent coordination
- MCP-based communication
- OpenTelemetry observability
- Next.js 16 + FastAPI portal interface
- Docker Compose for local development

Project structure follows `ai-agent-platform/` convention.
