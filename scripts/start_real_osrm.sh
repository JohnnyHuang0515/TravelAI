#!/bin/bash

# 真實 OSRM 服務啟動腳本
# 使用 Docker 運行真實的 OSRM 路由服務

echo "🚀 啟動真實 OSRM 路由服務..."

# 檢查 Docker 是否安裝
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安裝，請先安裝 Docker"
    exit 1
fi

# 檢查 OSRM 數據是否存在
OSRM_DATA_DIR="/Users/chieh/Documents/github專案/TravelAI/data/osrm"
TAIWAN_OSRM="$OSRM_DATA_DIR/taiwan-250923.osrm"

if [ ! -f "$TAIWAN_OSRM" ]; then
    echo "❌ 找不到台灣 OSRM 數據檔案: $TAIWAN_OSRM"
    echo "請先下載並處理 OSRM 數據"
    exit 1
fi

# 檢查必要的 OSRM 檔案
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

# 停止現有的 OSRM 容器
echo "🛑 停止現有的 OSRM 容器..."
docker rm -f osrm-taiwan 2>/dev/null || true

# 啟動 OSRM 服務
echo "🌐 啟動真實 OSRM HTTP 服務..."
cd "$OSRM_DATA_DIR"

# 使用 Docker 運行 OSRM 5.22.0 版本
docker run -d \
    --name osrm-taiwan \
    -v "$(pwd)":/data \
    -p 5001:5000 \
    --platform linux/amd64 \
    osrm/osrm-backend:v5.22.0 \
    osrm-routed --algorithm mld /data/taiwan-250923.osrm

# 檢查容器是否成功啟動
if [ $? -eq 0 ]; then
    echo "📋 OSRM 容器已啟動"
else
    echo "❌ OSRM 容器啟動失敗"
    exit 1
fi

# 等待服務啟動
echo "⏳ 等待 OSRM 服務啟動..."
sleep 15

# 檢查服務狀態
echo "🔍 檢查 OSRM 服務狀態..."
if docker ps | grep -q osrm-taiwan; then
    echo "✅ OSRM 容器正在運行"
    
    # 測試服務是否響應
    echo "🧪 測試 OSRM 服務響應..."
    if curl -s "http://localhost:5001/route/v1/driving/121.5170,25.0478;121.5170,25.0478" | grep -q '"code":"Ok"'; then
        echo "✅ OSRM 服務已成功啟動！"
        echo "🌐 服務地址: http://localhost:5001"
        echo "🗺️ 路由 API: http://localhost:5001/route/v1/driving/{coordinates}"
        echo "📊 測試命令: curl 'http://localhost:5001/route/v1/driving/121.5170,25.0478;121.7534,24.7548'"
        echo ""
        echo "💡 使用以下命令停止服務:"
        echo "   docker stop osrm-taiwan"
        echo "   docker rm osrm-taiwan"
        echo ""
        echo "📋 查看服務日誌:"
        echo "   docker logs osrm-taiwan"
        echo ""
        echo "🎉 真實 OSRM 服務已準備就緒！"
    else
        echo "⚠️ OSRM 服務啟動中，請稍候再試"
        echo "💡 查看日誌: docker logs osrm-taiwan"
    fi
else
    echo "❌ OSRM 容器啟動失敗"
    echo "💡 查看日誌: docker logs osrm-taiwan"
    exit 1
fi
