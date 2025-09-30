#!/bin/bash
# 智慧旅遊系統 - 一鍵啟動腳本

set -e

echo "🚀 智慧旅遊系統 - 一鍵啟動"
echo "=================================="

# 檢查 Docker 是否安裝
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安裝，請先安裝 Docker"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose 未安裝，請先安裝 Docker Compose"
    exit 1
fi

# 檢查 OSRM 資料是否存在
if [ ! -f "data/osrm/taiwan-250923.osrm" ]; then
    echo "⚠️ OSRM 資料檔案不存在，正在下載..."
    mkdir -p data/osrm
    
    # 下載台灣 OSRM 資料（簡化版本，實際使用時需要完整資料）
    echo "📥 下載 OSRM 資料..."
    # 這裡可以添加下載 OSRM 資料的邏輯
    echo "⚠️ 請手動下載 OSRM 資料到 data/osrm/ 目錄"
    echo "   或使用 process_osrm.sh 腳本處理"
fi

# 停止現有服務
echo "🛑 停止現有服務..."
docker-compose -p travelai down 2>/dev/null || true

# 清理舊的資料庫資料（可選）
read -p "🗑️ 是否清理舊的資料庫資料？(y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🧹 清理資料庫資料..."
    docker volume rm travelai_postgres_data 2>/dev/null || true
fi

# 啟動服務
echo "🚀 啟動服務..."
docker-compose -p travelai up -d

# 等待服務啟動
echo "⏳ 等待服務啟動..."
sleep 10

# 檢查服務狀態
echo "🔍 檢查服務狀態..."
docker-compose -p travelai ps

# 顯示服務資訊
echo ""
echo "✅ 服務啟動完成！"
echo "=================================="
echo "🌐 服務地址："
echo "   - API 服務: http://localhost:8000"
echo "   - API 文件: http://localhost:8000/docs"
echo "   - 資料庫: localhost:5432"
echo "   - Redis: localhost:6379"
echo "   - OSRM: localhost:5000"
echo ""
echo "📊 查看日誌："
echo "   docker-compose -p travelai logs -f"
echo ""
echo "🛑 停止服務："
echo "   docker-compose -p travelai down"
echo "=================================="
