#!/bin/bash
#==============================================================================
# AI情感助手 - 优雅停止脚本
#==============================================================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

FORCE="${1:-false}"
TIMEOUT=30  # 优雅停止超时(秒)

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

# 获取 docker-compose 命令
get_compose_cmd() {
    if docker compose version &> /dev/null; then
        echo "docker compose"
    else
        echo "docker-compose"
    fi
}

COMPOSE_CMD=$(get_compose_cmd)

#==============================================================================
# 主流程
#==============================================================================

log_info "========== 停止服务 =========="

# 检查是否有运行的服务
if ! $COMPOSE_CMD ps -q | grep -q . 2>/dev/null; then
    log_warning "没有运行中的服务"
    exit 0
fi

log_info "正在停止服务..."

if [ "$FORCE" = "true" ]; then
    log_warning "强制模式 - 立即停止所有容器"
    $COMPOSE_CMD down --remove-orphans
    log_success "服务已强制停止"
else
    # 优雅停止
    log_info "等待服务处理完成 (超时 ${TIMEOUT}秒)..."

    # 停止服务，允许完成当前请求
    $COMPOSE_CMD stop -t "$TIMEOUT" || true

    # 显示已停止状态
    echo ""
    log_info "服务状态:"
    $COMPOSE_CMD ps

    echo ""
    log_success "服务已优雅停止"
    echo ""
    echo "如需完全清理，请运行: ./deploy/clean.sh"
fi
