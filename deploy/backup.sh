#!/bin/bash
#==============================================================================
# AI情感助手 - 数据库备份脚本
#==============================================================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

BACKUP_DIR="${BACKUP_DIR:-./backups}"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/emotion_ai_${DATE}.sql.gz"
KEEP_DAYS="${KEEP_DAYS:-7}"

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

# 读取数据库密码
source .env.docker 2>/dev/null || true
MYSQL_PASSWORD="${MYSQL_ROOT_PASSWORD:-emotionai2024}"

#==============================================================================
# 主流程
#==============================================================================

log_info "========== 数据库备份 =========="

# 创建备份目录
mkdir -p "$BACKUP_DIR"

# 执行备份
log_info "正在备份数据库..."
$COMPOSE_CMD exec -T mysql mysqldump \
    -u root \
    -p"${MYSQL_PASSWORD}" \
    --single-transaction \
    --routines \
    --triggers \
    --events \
    --all-databases | gzip > "$BACKUP_FILE"

# 验证备份
if [ -f "$BACKUP_FILE" ] && [ -s "$BACKUP_FILE" ]; then
    BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    log_success "备份完成: $BACKUP_FILE (${BACKUP_SIZE})"
else
    echo -e "${RED}[ERROR]${NC} 备份文件无效"
    exit 1
fi

# 清理旧备份
log_info "清理 ${KEEP_DAYS} 天前的备份..."
find "$BACKUP_DIR" -name "emotion_ai_*.sql.gz" -mtime +"$KEEP_DAYS" -delete

# 列出当前备份
echo ""
log_info "当前备份列表:"
ls -lh "$BACKUP_DIR"/emotion_ai_*.sql.gz 2>/dev/null | tail -5

echo ""
log_success "数据库备份任务完成"
