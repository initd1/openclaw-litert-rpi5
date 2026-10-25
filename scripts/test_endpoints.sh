#!/bin/bash
echo "=========================================="
echo "🧪 Test 1: Testing /v1/chat/completions"
echo "=========================================="
curl -X POST http://127.0.0.1:4000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Hello!"}
    ]
  }'

echo -e "\n=========================================="
echo "🧪 Test 2: Testing /v1/embeddings"
echo "=========================================="
curl -X POST http://127.0.0.1:4000/v1/embeddings \
  -H "Content-Type: application/json" \
  -d '{
    "input": "Test string for OpenClaw memory sync."
  }'
echo -e "\n"
