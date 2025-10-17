#!/bin/bash

# 公車資料整合快速設定腳本
# 自動執行完整的公車資料整合流程

set -e  # 遇到錯誤立即退出

echo "=== TravelAI 公車資料整合設定 ==="
echo "開始時間: $(date)"
echo

# 取得腳本所在目錄
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "專案根目錄: $PROJECT_ROOT"
cd "$PROJECT_ROOT"

# 檢查 Python 環境
echo "=== 檢查 Python 環境 ==="
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安裝"
    exit 1
fi

python3 --version

# 檢查虛擬環境
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "⚠️  建議在虛擬環境中執行"
    echo "執行: source venv/bin/activate"
    read -p "是否繼續？ (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# 安裝依賴項
echo "=== 安裝依賴項 ==="
pip install pandas requests

# 檢查資料庫連接
echo "=== 檢查資料庫連接 ==="
if ! python3 -c "from src.itinerary_planner.infrastructure.persistence.database import get_database_url; print('資料庫連接測試:', get_database_url())" 2>/dev/null; then
    echo "❌ 資料庫連接失敗，請檢查資料庫設定"
    echo "確認環境變數 DATABASE_URL 已設定"
    exit 1
fi

# 執行資料庫遷移
echo "=== 執行資料庫遷移 ==="
if [ -f "migrations/008_add_bus_transport_tables.sql" ]; then
    if psql "$DATABASE_URL" -f migrations/008_add_bus_transport_tables.sql; then
        echo "✅ 資料庫遷移成功"
    else
        echo "❌ 資料庫遷移失敗"
        exit 1
    fi
else
    echo "❌ 找不到遷移檔案"
    exit 1
fi

# 檢查資料檔案
echo "=== 檢查資料檔案 ==="
DATA_DIR="data/osrm/data"
REQUIRED_FILES=("routes.csv" "stations.csv" "trips.csv" "stop_times.csv")

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$DATA_DIR/$file" ]; then
        echo "✅ $file"
    else
        echo "❌ 找不到 $file"
        exit 1
    fi
done

# 匯入資料
echo "=== 匯入公車資料 ==="
if python3 scripts/import_bus_data.py; then
    echo "✅ 資料匯入成功"
else
    echo "❌ 資料匯入失敗"
    exit 1
fi

# 檢查 OSRM 資料檔案
echo "=== 檢查 OSRM 資料檔案 ==="
OSRM_DATA_DIR="data/osrm"
if [ -f "$OSRM_DATA_DIR/taiwan-250923.osrm" ]; then
    echo "✅ OSRM 資料檔案存在"
else
    echo "⚠️  OSRM 資料檔案不存在，路由功能可能無法使用"
fi

# 測試整合
echo "=== 測試整合結果 ==="
if python3 scripts/bus_routing_example.py > /dev/null 2>&1; then
    echo "✅ 整合測試成功"
else
    echo "⚠️  整合測試失敗，但基本功能可能正常"
fi

echo
echo "=== 設定完成 ==="
echo "完成時間: $(date)"
echo
echo "✅ 公車資料整合已完成！"
echo
echo "後續步驟:"
echo "1. 啟動 OSRM 服務:"
echo "   python scripts/start_osrm_service.py"
echo
echo "2. 啟動應用程式:"
echo "   python -m uvicorn src.main:app --reload"
echo
echo "3. 測試公車路線規劃功能:"
echo "   python scripts/bus_routing_example.py"
echo
echo "4. 查看整合文件:"
echo "   docs/bus_data_integration.md"
echo
echo "如有問題，請查看日誌檔案或聯繫開發團隊。"

