#!/bin/bash

# ============================================
# TravelAI 智慧旅遊系統 - 一鍵啟動腳本
# ============================================
#
# 使用方式:
#   ./quick-start.sh         # 互動模式
#   ./quick-start.sh 1       # 完整 Docker 模式（非互動）
#   ./quick-start.sh 2       # 混合模式（非互動）
#   ./quick-start.sh 3       # 僅後端服務（非互動）
#   ./quick-start.sh 4       # 僅前端服務（非互動）
#
# ============================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 輔助函數
print_header() {
    echo ""
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# 檢查命令是否存在
check_command() {
    if command -v "$1" &> /dev/null; then
        return 0
    else
        return 1
    fi
}

# ============================================
# 主程序開始
# ============================================

cd "$PROJECT_ROOT"

print_header "🚀 TravelAI 智慧旅遊系統 - 一鍵啟動"

# ============================================
# 步驟 1: 選擇啟動模式
# ============================================

# 支援命令行參數: ./quick-start.sh [1-4]
if [ -n "$1" ]; then
    MODE=$1
else
    echo "請選擇啟動模式："
    echo "  1) 完整 Docker 模式（推薦，包含所有服務）"
    echo "  2) 混合模式（Docker 基礎服務 + 本地開發）"
    echo "  3) 僅後端服務"
    echo "  4) 僅前端服務"
    echo ""
    read -p "請輸入選項 [1-4] (預設: 1): " MODE
    MODE=${MODE:-1}
fi

# ============================================
# 步驟 2: 環境檢查
# ============================================

print_header "📋 檢查系統環境"

# 檢查 Docker
if ! check_command docker; then
    print_error "Docker 未安裝"
    echo "請先安裝 Docker: https://docs.docker.com/get-docker/"
    exit 1
fi
print_success "Docker 已安裝 ($(docker --version | cut -d' ' -f3 | tr -d ','))"

# 檢查 Docker Compose
if docker compose version &> /dev/null; then
    DOCKER_COMPOSE="docker compose"
    print_success "Docker Compose 已安裝 (V2)"
elif check_command docker-compose; then
    DOCKER_COMPOSE="docker-compose"
    print_success "Docker Compose 已安裝 (V1)"
else
    print_error "Docker Compose 未安裝"
    exit 1
fi

# 根據模式檢查其他依賴
if [ "$MODE" = "2" ] || [ "$MODE" = "3" ]; then
    if check_command uv; then
        print_success "uv 已安裝 ($(uv --version))"
        HAS_UV=true
    else
        print_warning "uv 未安裝，將使用 Python 虛擬環境"
        HAS_UV=false
        
        if ! check_command python3; then
            print_error "Python3 未安裝"
            exit 1
        fi
        print_success "Python3 已安裝 ($(python3 --version))"
    fi
fi

if [ "$MODE" = "2" ] || [ "$MODE" = "4" ]; then
    if ! check_command node; then
        print_error "Node.js 未安裝"
        echo "請先安裝 Node.js: https://nodejs.org/"
        exit 1
    fi
    print_success "Node.js 已安裝 ($(node --version))"
    
    if ! check_command npm; then
        print_error "npm 未安裝"
        exit 1
    fi
    print_success "npm 已安裝 ($(npm --version))"
fi

# ============================================
# 步驟 3: 環境變數設定
# ============================================

print_header "🔧 檢查環境變數"

if [ ! -f ".env" ]; then
    print_warning ".env 檔案不存在"
    
    if [ -f "env.example" ]; then
        cp "env.example" ".env"
        print_success ".env 檔案已建立（從 env.example 複製）"
        print_warning "請編輯 .env 檔案並設定以下必要變數："
        echo "  - GEMINI_API_KEY (Google Gemini API 金鑰)"
        echo "  - GOOGLE_CLIENT_ID (Google OAuth 客戶端 ID，可選)"
        echo "  - GOOGLE_CLIENT_SECRET (Google OAuth 客戶端密鑰，可選)"
        echo ""
        read -p "按 Enter 繼續，或 Ctrl+C 取消並先編輯 .env..."
    else
        print_error "env.example 檔案不存在"
        exit 1
    fi
else
    print_success ".env 檔案已存在"
    
    # 檢查必要的環境變數
    source .env
    
    if [ -z "$GEMINI_API_KEY" ] || [ "$GEMINI_API_KEY" = "your_google_gemini_api_key_here" ]; then
        print_warning "GEMINI_API_KEY 未設定或為預設值"
        print_info "AI 功能可能無法正常運作"
    else
        print_success "GEMINI_API_KEY 已設定"
    fi
fi

# ============================================
# 步驟 4: 啟動服務
# ============================================

case $MODE in
    1)
        # 完整 Docker 模式
        print_header "🐳 啟動完整 Docker 服務"
        
        print_info "停止現有容器..."
        $DOCKER_COMPOSE down 2>/dev/null || true
        
        print_info "啟動所有服務（PostgreSQL, Redis, OSRM, API）..."
        $DOCKER_COMPOSE up -d
        
        print_info "等待服務啟動..."
        sleep 15
        
        # 初始化資料庫（建表）
        print_header "🗄️  初始化資料庫"
        $DOCKER_COMPOSE exec -T api python3 scripts/init_database.py || {
            print_warning "資料庫初始化失敗，可能表已存在"
        }
        
        # 檢查資料是否已匯入
        print_header "📊 檢查資料庫"
        
        PLACE_COUNT=$($DOCKER_COMPOSE exec -T postgres psql -U postgres -d itinerary_db -t -c "SELECT COUNT(*) FROM places;" 2>/dev/null | tr -d ' ' || echo "0")
        
        if [ "$PLACE_COUNT" = "0" ] || [ -z "$PLACE_COUNT" ]; then
            print_warning "資料庫為空，建議執行資料匯入"
            
            # 非互動模式下跳過資料匯入
            if [ -n "$1" ]; then
                print_info "非互動模式，跳過資料匯入"
            else
                read -p "是否現在匯入資料？ (y/N): " IMPORT_DATA
                
                if [ "$IMPORT_DATA" = "y" ] || [ "$IMPORT_DATA" = "Y" ]; then
                    print_info "執行資料匯入（這可能需要幾分鐘）..."
                    $DOCKER_COMPOSE exec api python3 scripts/unified_data_importer.py
                    print_success "資料匯入完成"
                fi
            fi
        else
            print_success "資料庫已有 $PLACE_COUNT 筆地點資料"
        fi
        
        # 前端提示
        print_header "💻 啟動前端（可選）"
        
        # 非互動模式下自動啟動前端
        if [ -n "$1" ]; then
            START_FRONTEND="Y"
        else
            read -p "是否啟動前端開發服務器？ (Y/n): " START_FRONTEND
            START_FRONTEND=${START_FRONTEND:-Y}
        fi
        
        if [ "$START_FRONTEND" = "y" ] || [ "$START_FRONTEND" = "Y" ]; then
            cd frontend
            
            if [ ! -d "node_modules" ]; then
                print_info "安裝前端依賴..."
                npm install
            fi
            
            mkdir -p ../logs
            print_info "啟動前端服務（後台運行）..."
            nohup npm run dev > ../logs/frontend.log 2>&1 &
            FRONTEND_PID=$!
            echo $FRONTEND_PID > ../logs/frontend.pid
            
            print_success "前端服務已啟動 (PID: $FRONTEND_PID)"
            print_info "前端日誌: logs/frontend.log"
            
            cd ..
        fi
        ;;
        
    2)
        # 混合模式
        print_header "🔀 啟動混合模式（Docker 基礎服務 + 本地開發）"
        
        # 啟動基礎服務
        print_info "啟動 PostgreSQL, Redis, OSRM..."
        $DOCKER_COMPOSE up -d postgres redis osrm-backend
        
        print_info "等待服務啟動..."
        sleep 10
        
        # 初始化資料庫（建表）
        print_info "初始化資料庫..."
        if [ "$HAS_UV" = true ]; then
            uv run python scripts/init_database.py || print_warning "資料庫初始化失敗，可能表已存在"
        else
            python3 scripts/init_database.py || print_warning "資料庫初始化失敗，可能表已存在"
        fi
        
        # 啟動後端
        print_header "🚀 啟動本地後端服務"
        
        source .env
        
        if [ "$HAS_UV" = true ]; then
            print_info "使用 uv 啟動後端..."
            
            # 確保依賴已同步
            if [ ! -d ".venv" ]; then
                print_info "同步 uv 依賴..."
                uv sync
            fi
            
            mkdir -p logs
            nohup uv run uvicorn src.itinerary_planner.main:app --host 0.0.0.0 --port 8000 --reload > logs/backend.log 2>&1 &
            BACKEND_PID=$!
        else
            print_info "使用 Python venv 啟動後端..."
            
            if [ ! -d ".venv" ]; then
                print_info "建立虛擬環境..."
                python3 -m venv .venv
                source .venv/bin/activate
                pip install -r requirements.txt
            else
                source .venv/bin/activate
            fi
            
            mkdir -p logs
            nohup python3 -m uvicorn src.itinerary_planner.main:app --host 0.0.0.0 --port 8000 --reload > logs/backend.log 2>&1 &
            BACKEND_PID=$!
        fi
        
        echo $BACKEND_PID > logs/backend.pid
        print_success "後端服務已啟動 (PID: $BACKEND_PID)"
        
        sleep 3
        
        # 啟動前端
        print_header "💻 啟動前端服務"
        
        cd frontend
        
        if [ ! -d "node_modules" ]; then
            print_info "安裝前端依賴..."
            npm install
        fi
        
        mkdir -p ../logs
        print_info "啟動前端服務（後台運行）..."
        nohup npm run dev > ../logs/frontend.log 2>&1 &
        FRONTEND_PID=$!
        echo $FRONTEND_PID > ../logs/frontend.pid
        
        print_success "前端服務已啟動 (PID: $FRONTEND_PID)"
        
        cd ..
        ;;
        
    3)
        # 僅後端服務
        print_header "⚙️ 啟動僅後端服務"
        
        # 啟動基礎服務
        print_info "啟動 PostgreSQL, Redis, OSRM..."
        $DOCKER_COMPOSE up -d postgres redis osrm-backend
        
        print_info "等待服務啟動..."
        sleep 10
        
        # 初始化資料庫（建表）
        print_info "初始化資料庫..."
        if [ "$HAS_UV" = true ]; then
            uv run python scripts/init_database.py || print_warning "資料庫初始化失敗，可能表已存在"
        else
            python3 scripts/init_database.py || print_warning "資料庫初始化失敗，可能表已存在"
        fi
        
        source .env
        
        if [ "$HAS_UV" = true ]; then
            print_info "使用 uv 啟動後端..."
            
            if [ ! -d ".venv" ]; then
                print_info "同步 uv 依賴..."
                uv sync
            fi
            
            mkdir -p logs
            uv run uvicorn src.itinerary_planner.main:app --host 0.0.0.0 --port 8000 --reload
        else
            print_info "使用 Python venv 啟動後端..."
            
            if [ ! -d ".venv" ]; then
                print_info "建立虛擬環境..."
                python3 -m venv .venv
                source .venv/bin/activate
                pip install -r requirements.txt
            else
                source .venv/bin/activate
            fi
            
            python3 -m uvicorn src.itinerary_planner.main:app --host 0.0.0.0 --port 8000 --reload
        fi
        ;;
        
    4)
        # 僅前端服務
        print_header "💻 啟動僅前端服務"
        
        cd frontend
        
        if [ ! -d "node_modules" ]; then
            print_info "安裝前端依賴..."
            npm install
        fi
        
        print_info "啟動前端服務..."
        npm run dev
        ;;
        
    *)
        print_error "無效的選項"
        exit 1
        ;;
esac

# ============================================
# 步驟 5: 顯示服務狀態和資訊
# ============================================

sleep 3

print_header "🎉 啟動完成！"

echo ""
echo -e "${GREEN}🌐 服務地址${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 檢查服務狀態並顯示
if [ "$MODE" = "1" ] || [ "$MODE" = "2" ] || [ "$MODE" = "3" ]; then
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ 後端 API:${NC}       http://localhost:8000"
        echo -e "${GREEN}✅ API 文檔:${NC}       http://localhost:8000/docs"
    else
        echo -e "${YELLOW}⏳ 後端 API:${NC}       http://localhost:8000 (啟動中...)"
        echo -e "${YELLOW}⏳ API 文檔:${NC}       http://localhost:8000/docs"
    fi
fi

if [ "$MODE" = "1" ] || [ "$MODE" = "2" ] || [ "$MODE" = "4" ]; then
    if curl -s http://localhost:3000 > /dev/null 2>&1; then
        echo -e "${GREEN}✅ 前端應用:${NC}       http://localhost:3000"
    else
        echo -e "${YELLOW}⏳ 前端應用:${NC}       http://localhost:3000 (啟動中...)"
    fi
fi

if [ "$MODE" = "1" ] || [ "$MODE" = "2" ] || [ "$MODE" = "3" ]; then
    if docker ps | grep -q postgres; then
        echo -e "${GREEN}✅ PostgreSQL:${NC}     localhost:5432"
    fi
    
    if docker ps | grep -q redis; then
        echo -e "${GREEN}✅ Redis:${NC}          localhost:6379"
    fi
    
    if docker ps | grep -q osrm; then
        echo -e "${GREEN}✅ OSRM 路由:${NC}      http://localhost:5000"
    fi
fi

echo ""
echo -e "${BLUE}💡 有用的命令${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ "$MODE" = "1" ]; then
    echo "查看所有服務日誌:"
    echo "  $DOCKER_COMPOSE logs -f"
    echo ""
    echo "查看特定服務日誌:"
    echo "  $DOCKER_COMPOSE logs -f api"
    echo "  $DOCKER_COMPOSE logs -f postgres"
    echo ""
    echo "停止所有服務:"
    echo "  $DOCKER_COMPOSE down"
    echo ""
    echo "重啟服務:"
    echo "  $DOCKER_COMPOSE restart"
fi

if [ "$MODE" = "2" ]; then
    echo "查看後端日誌:"
    echo "  tail -f logs/backend.log"
    echo ""
    echo "查看前端日誌:"
    echo "  tail -f logs/frontend.log"
    echo ""
    echo "停止所有服務:"
    echo "  bash scripts/stop.sh"
    echo ""
    echo "停止後端:"
    echo "  kill \$(cat logs/backend.pid)"
    echo ""
    echo "停止前端:"
    echo "  kill \$(cat logs/frontend.pid)"
fi

if [ "$MODE" = "3" ] && [ -f "logs/backend.pid" ]; then
    echo "查看後端日誌:"
    echo "  tail -f logs/backend.log"
    echo ""
    echo "停止後端:"
    echo "  kill \$(cat logs/backend.pid)"
fi

echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}🎊 TravelAI 系統已就緒！${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

