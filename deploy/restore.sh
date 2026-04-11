#!/bin/bash
#==============================================================================
# AI情感助手 - 数据库恢复脚本
#==============================================================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

BACKUP_DIR="${BACKUP_DIR:-./backups}"
BACKUP_FILE="${1:-}"

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
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

# 读取数据库密码
source .env.docker 2>/dev/null || true
MYSQL_PASSWORD="${MYSQL_ROOT_PASSWORD:-emotionai2024}"

#==============================================================================
# 主流程
#==============================================================================

echo ""
echo -e "${RED}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${RED}║              ⚠️  警告: 数据库恢复操作 ⚠️                  ║${NC}"
echo -e "${RED}║                                                        ║${NC}"
echo -e "${RED}║  此操作将覆盖当前数据库数据，请谨慎操作！              ║${NC}"
echo -e "${RED}╚════════════════════════════════════════════════════════╝${NC}"
echo ""

# 如果没有指定备份文件，列出可用的
if [ -z "$BACKUP_FILE" ]; then
    log_info "可用备份文件:"
    echo ""
    ls -lh "$BACKUP_DIR"/emotion_ai_*.sql.gz 2>/dev/null || {
        log_error "未找到备份文件，请先运行 backup.sh"
        exit 1
    }
    echo ""
    echo "用法: $0 <备份文件路径>"
    exit 1
fi

# 检查文件是否存在
if [ ! -f "$BACKUP_FILE" ]; then
    log_error "备份文件不存在: $BACKUP_FILE"
    exit 1
fi

# 确认恢复
echo -n "确认恢复数据库? (输入 'YES' 确认): "
read -r confirm

if [ "$confirm" != "YES" ]; then
    log_info "取消恢复操作"
    exit 0
fi

log_info "========== 数据库恢复 =========="
log_info "备份文件: $BACKUP_FILE"

# 解压并恢复
log_info "正在恢复数据库..."

gunzip -c "$BACKUP_FILE" | $COMPOSE_CMD exec -T mysql mysql \
    -u root \
    -p"${MYSQL_PASSWORD}"

log_success "数据库恢复完成"
echo ""
log_info "建议重启后端服务以加载新数据: ./deploy/restart.sh backend"
