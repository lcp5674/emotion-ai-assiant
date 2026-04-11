#!/bin/bash
#==============================================================================
# AI情感助手 - 完整清理脚本
#==============================================================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

REMOVE_VOLUMES="${1:-false}"

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

echo ""
echo -e "${RED}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${RED}║              ⚠️  警告: 完整清理操作 ⚠️                  ║${NC}"
echo -e "${RED}║                                                        ║${NC}"
echo -e "${RED}║  此操作将:                                            ║${NC}"
echo -e "${RED}║  - 停止所有服务                                       ║${NC}"
echo -e "${RED}║  - 删除所有容器                                       ║${NC}"
echo -e "${RED}║  - 删除所有镜像                                       ║${NC}"
if [ "$REMOVE_VOLUMES" = "true" ]; then
    echo -e "${RED}║  - 删除所有数据卷 (数据库数据将丢失!)                 ║${NC}"
fi
echo -e "${RED}║                                                        ║${NC}"
echo -e "${RED}╚════════════════════════════════════════════════════════╝${NC}"
echo ""

if [ "$REMOVE_VOLUMES" = "true" ]; then
    echo -n "确认清理所有数据? (输入 'DELETE ALL' 确认): "
else
    echo -n "确认清理服务? (输入 'YES' 确认): "
fi
read -r confirm

if [ "$REMOVE_VOLUMES" = "true" ] && [ "$confirm" != "DELETE ALL" ]; then
    log_info "取消清理操作"
    exit 0
elif [ "$REMOVE_VOLUMES" != "true" ] && [ "$confirm" != "YES" ]; then
    log_info "取消清理操作"
    exit 0
fi

log_info "========== 清理环境 =========="

# 停止并删除容器
log_info "停止并删除容器..."
$COMPOSE_CMD down

if [ "$REMOVE_VOLUMES" = "true" ]; then
    log_warning "删除数据卷..."
    $COMPOSE_CMD down -v --remove-orphans
fi

# 删除镜像
log_info "删除项目镜像..."
docker rmi emotion-ai-backend:latest emotion-ai-frontend:latest emotion-ai-nginx:latest 2>/dev/null || true

# 清理未使用的镜像
log_info "清理未使用的Docker资源..."
docker system prune -f

log_success "清理完成!"
echo ""
echo "如需重新部署，请运行: ./deploy/deploy.sh"
