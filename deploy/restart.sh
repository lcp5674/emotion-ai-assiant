#!/bin/bash
#==============================================================================
# AI情感助手 - 重启单个服务脚本
#==============================================================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

SERVICE="${1:-backend}"
KEEP_LOGS="${2:-true}"

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
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

case "$SERVICE" in
    backend)
        log_info "重启后端服务..."
        $COMPOSE_CMD restart backend
        ;;
    frontend)
        log_info "重启前端服务..."
        $COMPOSE_CMD restart frontend
        ;;
    mysql)
        log_info "重启MySQL服务..."
        $COMPOSE_CMD restart mysql
        ;;
    redis)
        log_info "重启Redis服务..."
        $COMPOSE_CMD restart redis
        ;;
    all)
        log_info "重启所有服务..."
        $COMPOSE_CMD restart
        ;;
    *)
        echo "用法: $0 {backend|frontend|mysql|redis|all}"
        exit 1
        ;;
esac

sleep 2

log_success "$SERVICE 服务已重启"
echo ""
log_info "查看日志: docker logs -f emotion-ai-${SERVICE}"
