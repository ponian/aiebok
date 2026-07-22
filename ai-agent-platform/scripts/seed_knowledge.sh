#!/bin/bash
# scripts/seed_knowledge.sh
set -e

echo "等待 ChromaDB 啟動..."
until curl -s http://localhost:8000/api/v1/heartbeat > /dev/null 2>&1; do
  sleep 2
done

echo "初始化知識庫..."
python -m knowledge.base_builder

echo "驗證知識庫..."
curl -s http://localhost:8000/api/v1/collections | python3 -m json.tool

echo "✅ 知識庫準備就緒"
