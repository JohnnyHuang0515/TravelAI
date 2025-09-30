#!/bin/bash
# 處理 OSM 資料為 OSRM 格式

set -e

OSM_FILE="/home/johnny/專案/比賽資料/data/osrm/taiwan-250923.osm.pbf"
OSRM_DIR="/home/johnny/專案/比賽資料/data/osrm"

echo "開始處理 OSM 資料為 OSRM 格式..."

# 檢查 OSM 檔案是否存在
if [ ! -f "$OSM_FILE" ]; then
    echo "❌ OSM 檔案不存在: $OSM_FILE"
    exit 1
fi

# 使用 Docker 運行 OSRM 處理
echo "1. 提取道路網路..."
docker run --rm -v "$OSRM_DIR:/data" osrm/osrm-backend:v5.22.0 osrm-extract -p /opt/car.lua /data/taiwan-250923.osm.pbf

echo "2. 分割道路網路..."
docker run --rm -v "$OSRM_DIR:/data" osrm/osrm-backend:v5.22.0 osrm-partition /data/taiwan-250923.osrm

echo "3. 自定義道路網路..."
docker run --rm -v "$OSRM_DIR:/data" osrm/osrm-backend:v5.22.0 osrm-customize /data/taiwan-250923.osrm

echo "✅ OSRM 處理完成！"

# 檢查生成的檔案
echo "生成的檔案:"
ls -la "$OSRM_DIR"/*.osrm*

echo "現在可以啟動 OSRM 服務了！"
