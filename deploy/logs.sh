#!/bin/bash
#==============================================================================
# AI情感助手 - 日志查看脚本
#==============================================================================

set -e

SERVICE="${1:-all}"
LINES="${2:-100}"
FOLLOW="${3:-false}"

# 颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 获取 docker-compose 命令
get_compose_cmd() {
    if docker compose version &> /dev/null; then
        echo "docker compose"
    else
        echo "docker-compose"
    fi
}

COMPOSE_CMD=$(get_compose_cmd)

# 服务名称映射
get_container_name() {
    case "$1" in
        backend) echo "emotion-ai-backend" ;;
        frontend) echo "emotion-ai-frontend" ;;
        nginx) echo "emotion-ai-frontend" ;;
        mysql) echo "emotion-ai-mysql" ;;
        redis) echo "emotion-ai-redis" ;;
        minio) echo "emotion-ai-minio" ;;
        all) echo "" ;;
        *) echo "" ;;
    esac
}

#==============================================================================
# 主流程
#==============================================================================

show_usage() {
    echo "用法: $0 [服务] [行数] [跟随]"
    echo ""
    echo "服务选项:"
    echo "  backend  - 后端 FastAPI 日志"
    echo "  frontend - 前端 Nginx 日志"
    echo "  mysql    - MySQL 日志"
    echo "  redis    - Redis 日志"
    echo "  minio    - MinIO 日志"
    echo "  all      - 所有服务日志 (默认)"
    echo ""
    echo "示例:"
    echo "  $0 backend 200           # 查看后端最近200行日志"
    echo "  $0 frontend 50 true      # 跟随查看前端日志"
    echo "  $0 all 100 false         # 查看所有服务最近100行日志"
}

# 显示帮助
if [ "$SERVICE" = "-h" ] || [ "$SERVICE" = "--help" ]; then
    show_usage
    exit 0
fi

CONTAINER=$(get_container_name "$SERVICE")

if [ -z "$CONTAINER" ] && [ "$SERVICE" != "all" ]; then
    show_usage
    exit 1
fi

echo ""
echo -e "${BLUE}═══════════════════════════════════════════${NC}"
echo -e "${BLUE}         AI情感助手 - 日志查看${NC}"
echo -e "${BLUE}═══════════════════════════════════════════${NC}"
echo ""

if [ "$SERVICE" = "all" ]; then
    echo -e "${GREEN}[全部服务日志]${NC} - 最近 ${LINES} 行"
    if [ "$FOLLOW" = "true" ]; then
        $COMPOSE_CMD logs --tail="$LINES" -f
    else
        $COMPOSE_CMD logs --tail="$LINES"
    fi
else
    if ! docker ps --format '{{.Names}}' | grep -q "^${CONTAINER}$"; then
        echo -e "${RED}错误: 容器 ${CONTAINER} 不存在或未运行${NC}"
        exit 1
    fi

    echo -e "${GREEN}[${SERVICE}]${NC} - 最近 ${LINES} 行"
    echo ""

    if [ "$FOLLOW" = "true" ]; then
        docker logs -f --tail="$LINES" "$CONTAINER"
    else
        docker logs --tail="$LINES" "$CONTAINER"
    fi
fi
