#!/bin/bash

# TravelAI 一鍵啟動腳本
# 適用於 Linux/WSL 環境

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "🚀 TravelAI 智慧旅遊系統啟動腳本"
echo "======================================"
echo ""

cd "$PROJECT_ROOT"

# 檢查環境
echo "📋 檢查系統環境..."

# 檢查 Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安裝"
    echo "請先安裝 Docker: https://docs.docker.com/get-docker/"
    exit 1
fi
echo "✅ Docker 已安裝"

# 檢查 Docker Compose
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose 未安裝"
    echo "請先安裝 Docker Compose"
    exit 1
fi
echo "✅ Docker Compose 已安裝"

# 檢查 .env 文件
if [ ! -f "$PROJECT_ROOT/.env" ]; then
    echo "⚠️  .env 文件不存在，從 env.example 複製..."
    if [ -f "$PROJECT_ROOT/env.example" ]; then
        cp "$PROJECT_ROOT/env.example" "$PROJECT_ROOT/.env"
        echo "✅ .env 文件已創建"
        echo "⚠️  請編輯 .env 文件並設定必要的環境變數"
    else
        echo "❌ env.example 文件不存在"
        exit 1
    fi
fi

# 啟動服務
echo ""
echo "🚀 啟動所有服務..."
echo "======================================"

# 使用 docker-compose
if command -v docker-compose &> /dev/null; then
    docker-compose up -d
else
    docker compose up -d
fi

# 等待服務啟動
echo ""
echo "⏳ 等待服務啟動..."
sleep 10

# 檢查服務狀態
echo ""
echo "📊 檢查服務狀態..."
echo "======================================"

# 檢查 PostgreSQL
if docker ps | grep -q postgres; then
    echo "✅ PostgreSQL 資料庫運行中"
else
    echo "❌ PostgreSQL 資料庫未運行"
fi

# 檢查 Redis
if docker ps | grep -q redis; then
    echo "✅ Redis 快取運行中"
else
    echo "❌ Redis 快取未運行"
fi

# 檢查 OSRM
if docker ps | grep -q osrm; then
    echo "✅ OSRM 路由服務運行中"
else
    echo "⚠️  OSRM 路由服務未運行"
fi

# 檢查 FastAPI
if docker ps | grep -q api; then
    echo "✅ FastAPI 後端運行中"
else
    echo "❌ FastAPI 後端未運行"
fi

# 顯示服務地址
echo ""
echo "🌐 服務地址"
echo "======================================"
echo "📍 後端 API: http://localhost:8000"
echo "📖 API 文檔: http://localhost:8000/docs"
echo "🗺️  OSRM 路由: http://localhost:5000"
echo "🗄️  PostgreSQL: localhost:5432"
echo "⚡ Redis: localhost:6379"
echo ""

# 顯示有用的命令
echo "💡 有用的命令"
echo "======================================"
echo "查看日誌:"
echo "  docker-compose logs -f"
echo ""
echo "查看特定服務日誌:"
echo "  docker-compose logs -f api"
echo "  docker-compose logs -f postgres"
echo "  docker-compose logs -f osrm-backend"
echo ""
echo "停止所有服務:"
echo "  docker-compose down"
echo ""
echo "重啟服務:"
echo "  docker-compose restart"
echo ""
echo "✅ TravelAI 系統啟動完成！"

