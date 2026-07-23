# AI Agent Platform MVP

Enterprise AI Agent collaboration platform for automating IT workflows.

## Quick Start

```bash
# 1. Clone and configure
cp .env.example .env

# 2. Start all services
docker compose up -d

# 3. Wait for services (check health)
docker compose ps

# 4. Test the flow
curl -X POST http://localhost:9112/task \
  -H "Content-Type: application/json" \
  -d '{"content": "新員工張小明明天入職市場部擔任產品經理", "user_id": "hr_manager_001"}'

# 5. Open Portal
open http://localhost:9114
```

## Viewing Logs

```bash
# All services (real-time, like tail -f)
docker compose logs -f

# Specific service
docker compose logs -f cca-agent

# Multiple services
docker compose logs -f cca-agent mcp-service hr-agent it-agent

# Last N lines (e.g., 50)
docker compose logs --tail 50 cca-agent

# Since a time ago
docker compose logs --since 10m cca-agent
```

## Architecture

| Service | Host Port | Container Port | Description |
|---------|-----------|----------------|-------------|
| CCA Agent | 9112 | 8084 | Core orchestrator with LLM |
| MCP Service | 9109 | 8083 | Tool registry and routing |
| HR Agent | 9110 | 8081 | Employee management |
| IT Agent | 9111 | 8082 | AD account management |
| Mock AD API | 9107 | 8090 | Simulated Active Directory |
| Mock HR API | 9108 | 8091 | Simulated HR system |
| Portal Backend | 9113 | 8085 | API gateway |
| Portal Frontend | 9114 | 3000 | Web UI (Next.js) |
| PostgreSQL | 9101 | 5432 | Database |
| Redis | 9102 | 6379 | Cache/session |
| NATS | 9103 | 4222 | Message queue |
| ChromaDB | 9105 | 8000 | Vector DB |
| Ollama | 9106 | 11434 | Local LLM |

## Prerequisites

- Docker Desktop 4.0+ with Compose V2
- 16GB+ RAM
- NVIDIA GPU recommended (for Ollama)
