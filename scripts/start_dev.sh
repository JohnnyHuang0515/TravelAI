#!/bin/bash

# TravelAI 開發環境啟動腳本
# 適用於 Linux/WSL，不使用 Docker

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "🚀 TravelAI 開發環境啟動"
echo "======================================"
echo ""

cd "$PROJECT_ROOT"

# 檢查環境
echo "📋 檢查開發環境..."

# 檢查 Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安裝"
    exit 1
fi
echo "✅ Python $(python3 --version)"

# 檢查虛擬環境
if [ ! -d "$PROJECT_ROOT/.venv" ]; then
    echo "⚠️  虛擬環境不存在，正在創建..."
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    echo "✅ 虛擬環境已創建"
else
    echo "✅ 虛擬環境已存在"
fi

# 啟動虛擬環境
source .venv/bin/activate

# 檢查 .env 文件
if [ ! -f "$PROJECT_ROOT/.env" ]; then
    echo "⚠️  .env 文件不存在，請創建並設定環境變數"
    exit 1
fi
echo "✅ .env 文件已存在"

# 載入環境變數
source .env

# 檢查必要的環境變數
if [ -z "$GEMINI_API_KEY" ]; then
    echo "⚠️  GEMINI_API_KEY 未設定"
    echo "請在 .env 文件中設定 GEMINI_API_KEY"
fi

# 檢查 PostgreSQL
echo ""
echo "🗄️  檢查 PostgreSQL..."
if pg_isready -h localhost -p 5432 &> /dev/null; then
    echo "✅ PostgreSQL 運行中"
else
    echo "⚠️  PostgreSQL 未運行"
    echo "請啟動 PostgreSQL: docker-compose up -d postgres"
fi

# 檢查 OSRM
echo ""
echo "🗺️  檢查 OSRM 服務..."
if curl -s "http://localhost:5000/route/v1/driving/121.5,25.0;121.5,25.0" | grep -q "Ok" 2>/dev/null; then
    echo "✅ OSRM 服務運行中"
else
    echo "⚠️  OSRM 服務未運行"
    echo "請啟動 OSRM: bash scripts/start_real_osrm.sh"
fi

# 啟動後端服務
echo ""
echo "🚀 啟動後端服務..."
echo "======================================"
export GEMINI_API_KEY="${GEMINI_API_KEY}"
export DATABASE_URL="${DATABASE_URL:-postgresql://postgres:password@localhost:5432/itinerary_db}"
export OSRM_HOST="${OSRM_HOST:-http://localhost:5000}"

# 背景啟動
nohup python3 -m uvicorn src.itinerary_planner.main:app --host 0.0.0.0 --port 8000 --reload > logs/backend.log 2>&1 &
BACKEND_PID=$!

echo "✅ 後端服務已啟動 (PID: $BACKEND_PID)"
echo "📋 日誌位置: logs/backend.log"

# 等待後端啟動
echo ""
echo "⏳ 等待後端啟動..."
sleep 5

# 檢查後端
if curl -s http://localhost:8000/docs &> /dev/null; then
    echo "✅ 後端 API 已就緒"
else
    echo "⚠️  後端可能還在啟動中..."
fi

# 顯示服務信息
echo ""
echo "🌐 服務地址"
echo "======================================"
echo "📍 後端 API: http://localhost:8000"
echo "📖 API 文檔: http://localhost:8000/docs"
echo "🗺️  OSRM 路由: http://localhost:5000"
echo ""
echo "📋 日誌: tail -f logs/backend.log"
echo "🛑 停止: pkill -f 'uvicorn.*itinerary_planner'"
echo ""
echo "✅ TravelAI 開發環境已啟動！"

