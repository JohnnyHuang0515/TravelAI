#!/bin/bash

# OSRM 服務啟動腳本
# 用於啟動 OSRM 路由服務

echo "🚀 啟動 OSRM 路由服務..."

# 檢查 OSRM 數據是否存在
OSRM_DATA_DIR="/Users/chieh/Documents/github專案/TravelAI/data/osrm"
TAIWAN_PBF="$OSRM_DATA_DIR/taiwan-250923.osm.pbf"

if [ ! -f "$TAIWAN_PBF" ]; then
    echo "❌ 找不到台灣 OSM 數據檔案: $TAIWAN_PBF"
    echo "請先下載並處理 OSRM 數據"
    exit 1
fi

# 檢查處理後的 OSRM 檔案
OSRM_FILES=(
    "$OSRM_DATA_DIR/taiwan-250923.osrm"
    "$OSRM_DATA_DIR/taiwan-250923.osrm.edges"
    "$OSRM_DATA_DIR/taiwan-250923.osrm.geometry"
    "$OSRM_DATA_DIR/taiwan-250923.osrm.mldgr"
    "$OSRM_DATA_DIR/taiwan-250923.osrm.partition"
)

echo "🔍 檢查 OSRM 處理檔案..."
for file in "${OSRM_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file 存在"
    else
        echo "❌ $file 不存在"
        echo "請先完成 OSRM 數據處理"
        exit 1
    fi
done

# 啟動 OSRM 服務
echo "🌐 啟動 OSRM HTTP 服務..."
cd "$OSRM_DATA_DIR"

# 使用 MLD 算法啟動服務（較快）
osrm-routed --algorithm mld taiwan-250923.osrm &

# 獲取進程 ID
OSRM_PID=$!
echo "📋 OSRM 服務進程 ID: $OSRM_PID"

# 等待服務啟動
echo "⏳ 等待 OSRM 服務啟動..."
sleep 5

# 檢查服務狀態
if curl -s http://localhost:5000/health > /dev/null; then
    echo "✅ OSRM 服務已成功啟動！"
    echo "🌐 服務地址: http://localhost:5000"
    echo "📊 健康檢查: http://localhost:5000/health"
    echo "🗺️ 路由 API: http://localhost:5000/route/v1/driving/{coordinates}"
    echo ""
    echo "💡 使用 Ctrl+C 停止服務"
    
    # 保存進程 ID
    echo $OSRM_PID > /tmp/osrm.pid
    
    # 等待用戶中斷
    wait $OSRM_PID
else
    echo "❌ OSRM 服務啟動失敗"
    kill $OSRM_PID 2>/dev/null
    exit 1
fi
