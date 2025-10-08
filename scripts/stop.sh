#!/bin/bash

# TravelAI 停止服務腳本

echo "🛑 停止 TravelAI 服務..."
echo "======================================"
echo ""

# 停止 Docker 服務
echo "🐳 停止 Docker 服務..."
if command -v docker-compose &> /dev/null; then
    docker-compose down
else
    docker compose down
fi

# 停止開發環境後端
echo ""
echo "🔧 停止開發環境後端..."
pkill -f "uvicorn.*itinerary_planner" || echo "沒有運行中的後端服務"

# 停止 OSRM 容器
echo ""
echo "🗺️  停止 OSRM 服務..."
docker stop osrm-taiwan 2>/dev/null && docker rm osrm-taiwan 2>/dev/null || echo "沒有運行中的 OSRM 容器"

echo ""
echo "✅ 所有服務已停止"

