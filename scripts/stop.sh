#!/bin/bash

# ============================================
# TravelAI 智慧旅遊系統 - 停止腳本
# ============================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

cd "$PROJECT_ROOT"

print_header "🛑 TravelAI 系統停止腳本"

# 停止 Docker 服務
print_info "停止 Docker 容器..."
if docker-compose ps -q 2>/dev/null | grep -q .; then
    docker-compose down
    print_success "Docker 服務已停止"
else
    print_info "沒有運行中的 Docker 服務"
fi

# 停止本地後端服務
if [ -f "$PROJECT_ROOT/logs/backend.pid" ]; then
    BACKEND_PID=$(cat "$PROJECT_ROOT/logs/backend.pid")
    if ps -p $BACKEND_PID > /dev/null 2>&1; then
        print_info "停止後端服務 (PID: $BACKEND_PID)..."
        kill $BACKEND_PID 2>/dev/null || true
        sleep 2
        
        # 強制停止如果還在運行
        if ps -p $BACKEND_PID > /dev/null 2>&1; then
            kill -9 $BACKEND_PID 2>/dev/null || true
        fi
        
        rm "$PROJECT_ROOT/logs/backend.pid"
        print_success "後端服務已停止"
    else
        print_info "後端服務未運行"
        rm "$PROJECT_ROOT/logs/backend.pid"
    fi
fi

# 停止本地前端服務
if [ -f "$PROJECT_ROOT/logs/frontend.pid" ]; then
    FRONTEND_PID=$(cat "$PROJECT_ROOT/logs/frontend.pid")
    if ps -p $FRONTEND_PID > /dev/null 2>&1; then
        print_info "停止前端服務 (PID: $FRONTEND_PID)..."
        kill $FRONTEND_PID 2>/dev/null || true
        sleep 2
        
        # 強制停止如果還在運行
        if ps -p $FRONTEND_PID > /dev/null 2>&1; then
            kill -9 $FRONTEND_PID 2>/dev/null || true
        fi
        
        rm "$PROJECT_ROOT/logs/frontend.pid"
        print_success "前端服務已停止"
    else
        print_info "前端服務未運行"
        rm "$PROJECT_ROOT/logs/frontend.pid"
    fi
fi

# 清理其他可能的進程
print_info "檢查其他相關進程..."

# 停止 uvicorn 進程
UVICORN_PIDS=$(pgrep -f "uvicorn.*itinerary_planner" || true)
if [ -n "$UVICORN_PIDS" ]; then
    print_warning "發現其他 uvicorn 進程，正在停止..."
    echo "$UVICORN_PIDS" | xargs kill 2>/dev/null || true
    sleep 1
fi

# 停止 npm dev 進程
NPM_PIDS=$(pgrep -f "next dev" || true)
if [ -n "$NPM_PIDS" ]; then
    print_warning "發現其他前端進程，正在停止..."
    echo "$NPM_PIDS" | xargs kill 2>/dev/null || true
    sleep 1
fi

print_header "✅ 所有服務已停止"

echo -e "${BLUE}💡 重新啟動服務:${NC}"
echo "  bash quick-start.sh"
echo "  或"
echo "  bash scripts/start.sh"
echo ""
