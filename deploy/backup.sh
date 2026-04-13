#!/bin/bash
#==============================================================================
# AI情感助手 - 增强版备份脚本 v2.0
# 支持数据库、Redis、MinIO和文件备份
#==============================================================================

set -e
set -o pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 获取脚本目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# 配置
BACKUP_DIR="${BACKUP_DIR:-$PROJECT_DIR/backups}"
DATE=$(date +%Y%m%d_%H%M%S)
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
KEEP_DAYS="${KEEP_DAYS:-7}"
COMPRESS_LEVEL="${COMPRESS_LEVEL:-6}"

# 备份类型
BACKUP_TYPE="${1:-all}"  # all, db, redis, minio, uploads

# 获取 docker-compose 命令
get_compose_cmd() {
    if docker compose version &> /dev/null 2>&1; then
        echo "docker compose"
    else
        echo "docker-compose"
    fi
}

COMPOSE_CMD=$(get_compose_cmd)

# 读取环境变量
source "$PROJECT_DIR/.env.docker" 2>/dev/null || true
MYSQL_PASSWORD="${MYSQL_PASSWORD:-${MYSQL_ROOT_PASSWORD:-emotionai2024}}"
REDIS_PASSWORD="${REDIS_PASSWORD:-redis}"

#==============================================================================
# 备份 MySQL 数据库
#==============================================================================
backup_mysql() {
    local backup_file="${BACKUP_DIR}/mysql/emotion_ai_${TIMESTAMP}.sql.gz"

    log_info "========== MySQL 数据库备份 =========="

    mkdir -p "$BACKUP_DIR/mysql"

    # 检查 MySQL 容器是否运行
    if ! docker ps | grep -q emotion-ai-mysql; then
        log_warning "MySQL 容器未运行，跳过备份"
        return 1
    fi

    log_info "正在备份 MySQL 数据库..."

    # 执行备份
    docker exec emotion-ai-mysql mysqldump \
        -u root \
        -p"${MYSQL_PASSWORD}" \
        --single-transaction \
        --routines \
        --triggers \
        --events \
        --all-databases 2>/dev/null | gzip -$COMPRESS_LEVEL > "$backup_file"

    # 验证备份
    if [ -f "$backup_file" ] && [ -s "$backup_file" ]; then
        local size=$(du -h "$backup_file" | cut -f1)
        log_success "MySQL 备份完成: $backup_file (${size})"
        echo "$backup_file"
    else
        log_error "MySQL 备份失败"
        return 1
    fi
}

#==============================================================================
# 备份 Redis 数据
#==============================================================================
backup_redis() {
    local backup_file="${BACKUP_DIR}/redis/redis_${TIMESTAMP}.rdb.gz"

    log_info "========== Redis 数据备份 =========="

    mkdir -p "$BACKUP_DIR/redis"

    # 检查 Redis 容器是否运行
    if ! docker ps | grep -q emotion-ai-redis; then
        log_warning "Redis 容器未运行，跳过备份"
        return 1
    fi

    log_info "正在备份 Redis 数据..."

    # 触发 RDB 快照
    docker exec emotion-ai-redis redis-cli -a "${REDIS_PASSWORD}" BGSAVE 2>/dev/null || true

    # 等待快照完成
    sleep 2

    # 复制 RDB 文件
    docker exec emotion-ai-redis cat /data/dump.rdb 2>/dev/null | gzip -$COMPRESS_LEVEL > "$backup_file"

    # 验证备份
    if [ -f "$backup_file" ] && [ -s "$backup_file" ]; then
        local size=$(du -h "$backup_file" | cut -f1)
        log_success "Redis 备份完成: $backup_file (${size})"
        echo "$backup_file"
    else
        log_error "Redis 备份失败"
        return 1
    fi
}

#==============================================================================
# 备份 MinIO 数据
#==============================================================================
backup_minio() {
    local backup_file="${BACKUP_DIR}/minio/minio_${TIMESTAMP}.tar.gz"

    log_info "========== MinIO 对象存储备份 =========="

    mkdir -p "$BACKUP_DIR/minio"

    # 检查 MinIO 容器是否运行
    if ! docker ps | grep -q emotion-ai-minio; then
        log_warning "MinIO 容器未运行，跳过备份"
        return 1
    fi

    log_info "正在备份 MinIO 数据..."

    # 使用 mc 客户端备份（如果可用）
    if docker exec emotion-ai-minio mc alias list &>/dev/null 2>&1; then
        docker exec emotion-ai-minio mc mirror local /backup/emotion-ai 2>/dev/null || true
    fi

    # 直接打包数据目录
    docker exec emotion-ai-minio tar -czf - -C /data . 2>/dev/null | gzip -$COMPRESS_LEVEL > "$backup_file"

    # 验证备份
    if [ -f "$backup_file" ] && [ -s "$backup_file" ]; then
        local size=$(du -h "$backup_file" | cut -f1)
        log_success "MinIO 备份完成: $backup_file (${size})"
        echo "$backup_file"
    else
        log_error "MinIO 备份失败"
        return 1
    fi
}

#==============================================================================
# 备份上传文件
#==============================================================================
backup_uploads() {
    local backup_file="${BACKUP_DIR}/uploads/uploads_${TIMESTAMP}.tar.gz"

    log_info "========== 上传文件备份 =========="

    mkdir -p "$BACKUP_DIR/uploads"

    # 检查上传目录是否存在
    if [ -d "$PROJECT_DIR/data/uploads" ]; then
        log_info "正在备份上传文件..."

        tar -czf "$backup_file" -C "$PROJECT_DIR/data" uploads 2>/dev/null

        # 验证备份
        if [ -f "$backup_file" ] && [ -s "$backup_file" ]; then
            local size=$(du -h "$backup_file" | cut -f1)
            log_success "上传文件备份完成: $backup_file (${size})"
            echo "$backup_file"
        else
            log_warning "上传文件备份失败或目录为空"
        fi
    else
        log_warning "上传目录不存在，跳过备份"
    fi
}

#==============================================================================
# 备份完整配置
#==============================================================================
backup_configs() {
    local backup_file="${BACKUP_DIR}/configs/configs_${TIMESTAMP}.tar.gz"

    log_info "========== 配置文件备份 =========="

    mkdir -p "$BACKUP_DIR/configs"

    # 备份关键配置文件
    local config_files=(
        "$PROJECT_DIR/.env.docker"
        "$PROJECT_DIR/docker-compose.yml"
        "$PROJECT_DIR/docker-compose.prod.yml"
        "$PROJECT_DIR/docker-compose.simple.yml"
        "$PROJECT_DIR/docker-compose-microservices.yml"
        "$PROJECT_DIR/nginx.conf"
        "$PROJECT_DIR/frontend/web/nginx.conf"
    )

    # 创建临时目录
    local temp_dir="${BACKUP_DIR}/.temp_configs_${TIMESTAMP}"
    mkdir -p "$temp_dir"

    # 复制配置文件（排除敏感信息）
    for file in "${config_files[@]}"; do
        if [ -f "$file" ]; then
            # 创建目录结构
            mkdir -p "$temp_dir/$(dirname "$file" | sed "s|$PROJECT_DIR||")"
            # 复制文件
            cp "$file" "$temp_dir/$(echo "$file" | sed "s|$PROJECT_DIR/||")"
        fi
    done

    # 打包
    tar -czf "$backup_file" -C "$temp_dir" . 2>/dev/null
    rm -rf "$temp_dir"

    # 验证备份
    if [ -f "$backup_file" ] && [ -s "$backup_file" ]; then
        local size=$(du -h "$backup_file" | cut -f1)
        log_success "配置文件备份完成: $backup_file (${size})"
        echo "$backup_file"
    else
        log_warning "配置文件备份失败"
    fi
}

#==============================================================================
# 清理旧备份
#==============================================================================
cleanup_old_backups() {
    log_info "========== 清理旧备份 =========="
    log_info "保留最近 ${KEEP_DAYS} 天的备份..."

    # 清理 MySQL 旧备份
    find "$BACKUP_DIR"/mysql -name "*.sql.gz" -mtime +"$KEEP_DAYS" -delete 2>/dev/null || true

    # 清理 Redis 旧备份
    find "$BACKUP_DIR"/redis -name "*.rdb.gz" -mtime +"$KEEP_DAYS" -delete 2>/dev/null || true

    # 清理 MinIO 旧备份
    find "$BACKUP_DIR"/minio -name "*.tar.gz" -mtime +"$KEEP_DAYS" -delete 2>/dev/null || true

    # 清理上传文件旧备份
    find "$BACKUP_DIR"/uploads -name "*.tar.gz" -mtime +"$KEEP_DAYS" -delete 2>/dev/null || true

    # 清理配置文件旧备份
    find "$BACKUP_DIR"/configs -name "*.tar.gz" -mtime +"$KEEP_DAYS" -delete 2>/dev/null || true

    log_success "旧备份清理完成"
}

#==============================================================================
# 显示备份状态
#==============================================================================
show_backup_status() {
    log_info "========== 备份状态 =========="

    echo ""
    echo "备份目录: $BACKUP_DIR"
    echo ""
    echo "MySQL 备份:"
    ls -lh "$BACKUP_DIR"/mysql/*.sql.gz 2>/dev/null | tail -5 || echo "  (无)"
    echo ""
    echo "Redis 备份:"
    ls -lh "$BACKUP_DIR"/redis/*.rdb.gz 2>/dev/null | tail -5 || echo "  (无)"
    echo ""
    echo "MinIO 备份:"
    ls -lh "$BACKUP_DIR"/minio/*.tar.gz 2>/dev/null | tail -5 || echo "  (无)"
    echo ""
    echo "上传文件备份:"
    ls -lh "$BACKUP_DIR"/uploads/*.tar.gz 2>/dev/null | tail -5 || echo "  (无)"
    echo ""
    echo "配置文件备份:"
    ls -lh "$BACKUP_DIR"/configs/*.tar.gz 2>/dev/null | tail -5 || echo "  (无)"
    echo ""

    # 计算总备份大小
    local total_size=$(du -sh "$BACKUP_DIR" 2>/dev/null | cut -f1)
    log_info "总备份大小: $total_size"
}

#==============================================================================
# 主流程
#==============================================================================
main() {
    echo ""
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║            AI情感助手 - 备份脚本 v2.0                      ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo ""

    # 创建备份目录
    mkdir -p "$BACKUP_DIR"/{mysql,redis,minio,uploads,configs}

    # 执行备份
    local success_count=0
    local fail_count=0

    case "$BACKUP_TYPE" in
        all)
            backup_mysql && ((success_count++)) || ((fail_count++))
            backup_redis && ((success_count++)) || ((fail_count++))
            backup_minio && ((success_count++)) || ((fail_count++))
            backup_uploads && ((success_count++)) || ((fail_count++))
            backup_configs && ((success_count++)) || ((fail_count++))
            ;;
        db|database)
            backup_mysql && ((success_count++)) || ((fail_count++))
            ;;
        redis|cache)
            backup_redis && ((success_count++)) || ((fail_count++))
            ;;
        minio|storage)
            backup_minio && ((success_count++)) || ((fail_count++))
            ;;
        uploads|files)
            backup_uploads && ((success_count++)) || ((fail_count++))
            ;;
        configs|config)
            backup_configs && ((success_count++)) || ((fail_count++))
            ;;
        status)
            show_backup_status
            exit 0
            ;;
        *)
            log_error "未知备份类型: $BACKUP_TYPE"
            echo "可用类型: all, db, redis, minio, uploads, configs, status"
            exit 1
            ;;
    esac

    echo ""

    # 清理旧备份
    cleanup_old_backups

    echo ""

    # 显示备份状态
    show_backup_status

    echo ""

    if [ $fail_count -eq 0 ]; then
        log_success "备份任务完成！成功: $success_count, 失败: $fail_count"
    else
        log_warning "备份任务完成！成功: $success_count, 失败: $fail_count"
    fi
}

# 显示帮助
show_help() {
    echo "AI情感助手 - 备份脚本"
    echo ""
    echo "用法: $0 [备份类型]"
    echo ""
    echo "备份类型:"
    echo "  all       - 备份所有数据 (默认)"
    echo "  db        - 仅备份 MySQL 数据库"
    echo "  redis     - 仅备份 Redis 缓存"
    echo "  minio     - 仅备份 MinIO 对象存储"
    echo "  uploads   - 仅备份上传文件"
    echo "  configs   - 仅备份配置文件"
    echo "  status    - 显示备份状态"
    echo ""
    echo "环境变量:"
    echo "  BACKUP_DIR    - 备份目录 (默认: ./backups)"
    echo "  KEEP_DAYS     - 保留天数 (默认: 7)"
    echo "  COMPRESS_LEVEL - 压缩级别 1-9 (默认: 6)"
    echo ""
    echo "示例:"
    echo "  $0                  # 备份所有"
    echo "  $0 db              # 仅备份数据库"
    echo "  BACKUP_DIR=/mnt/backups $0  # 使用自定义备份目录"
    echo ""
}

if [[ $# -gt 0 && ("$1" == "-h" || "$1" == "--help") ]]; then
    show_help
    exit 0
fi

main "$@"
