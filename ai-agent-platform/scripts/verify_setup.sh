#!/bin/bash
# scripts/verify_setup.sh
set -e

echo "🔍 驗證平台設置..."

# 1. 檢查 Docker 服務
echo ""
echo "1. 檢查 Docker 服務狀態..."
docker compose ps --format json 2>/dev/null | python3 -c "
import sys, json
for line in sys.stdin:
    svc = json.loads(line)
    status = '✅' if svc['State'] == 'running' else '❌'
    print(f'  {status} {svc[\"Service\"]}: {svc[\"State\"]}')
" || echo "  (docker compose ps not available in this environment)"

# 2. 測試 API 端點
echo ""
echo "2. 測試 API 端點..."
endpoints=(
    "MCP Service|http://localhost:9109/healthz"
    "CCA Agent|http://localhost:9112/healthz"
    "IT Agent|http://localhost:9111/healthz"
    "HR Agent|http://localhost:9110/healthz"
    "Mock AD API|http://localhost:9107/healthz"
    "Mock HR API|http://localhost:9108/healthz"
    "Portal Backend|http://localhost:9113/healthz"
)

for endpoint in "${endpoints[@]}"; do
    IFS='|' read -r name url <<< "$endpoint"
    if curl -sf "$url" > /dev/null 2>&1; then
        echo "  ✅ $name: reachable"
    else
        echo "  ❌ $name: unreachable"
    fi
done

# 3. 測試完整流程
echo ""
echo "3. 測試完整入職流程..."
response=$(curl -s -X POST http://localhost:9112/task \
  -H "Content-Type: application/json" \
  -d '{"content": "測試員工入職", "user_id": "test"}')

if echo "$response" | grep -q "task_id"; then
    echo "  ✅ 任務提交成功"
    task_id=$(echo "$response" | python3 -c "import sys, json; print(json.load(sys.stdin)['task_id'])")
    echo "  📋 Task ID: $task_id"
else
    echo "  ❌ 任務提交失敗"
    echo "  Response: $response"
fi

echo ""
echo "✅ 驗證完成！"
