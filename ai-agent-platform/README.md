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
curl -X POST http://localhost:8084/task \
  -H "Content-Type: application/json" \
  -d '{"content": "新員工張小明明天入職市場部擔任產品經理", "user_id": "hr_manager_001"}'

# 5. Open Portal
open http://localhost:3000
```

## Architecture

- **CCA Agent** (8084): Core orchestrator with LLM
- **MCP Service** (8083): Tool registry and routing
- **HR Agent** (8081): Employee management
- **IT Agent** (8082): AD account management
- **Mock APIs** (8090/8091): Simulated enterprise systems
- **Portal** (3000): Web UI

## Prerequisites

- Docker Desktop 4.0+ with Compose V2
- 16GB+ RAM
- NVIDIA GPU recommended (for Ollama)
