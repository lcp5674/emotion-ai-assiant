#!/bin/bash
set -e

# 自动备份脚本
# 备份数据库、上传文件和配置文件

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$PROJECT_ROOT"

# 加载环境变量
if [ ! -f ".env" ]; then
    echo -e "${RED}错误: 未找到 .env 文件${NC}"
    exit 1
fi
source .env

# 备份配置
BACKUP_DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="${BACKUP_DIR:-./deploy/backup}"
BACKUP_RETENTION_DAYS=${BACKUP_RETENTION_DAYS:-7}
MYSQL_CONTAINER="emotion-ai-mysql"

echo -e "${GREEN}=============================================${NC}"
echo -e "${GREEN}AI情感助手自动备份脚本${NC}"
echo -e "${GREEN}=============================================${NC}"
echo -e "${YELLOW}备份时间: ${BACKUP_DATE}${NC}"
echo ""

# 创建备份目录
mkdir -p "${BACKUP_DIR}/mysql" "${BACKUP_DIR}/files"

# 1. 备份MySQL数据库
echo -e "${YELLOW}1. 备份MySQL数据库...${NC}"
docker exec -i "${MYSQL_CONTAINER}" mysqldump \
    -u"${MYSQL_USER}" \
    -p"${MYSQL_PASSWORD}" \
    "${MYSQL_DATABASE}" \
    --single-transaction \
    --quick \
    --lock-tables=false \
    | gzip > "${BACKUP_DIR}/mysql/emotion_ai_${BACKUP_DATE}.sql.gz"

if [ $? -eq 0 ]; then
    BACKUP_SIZE=$(du -h "${BACKUP_DIR}/mysql/emotion_ai_${BACKUP_DATE}.sql.gz" | cut -f1)
    echo -e "${GREEN}✓ 数据库备份完成: ${BACKUP_SIZE}${NC}"
else
    echo -e "${RED}错误: 数据库备份失败${NC}"
    exit 1
fi

# 2. 备份上传文件
echo -e "${YELLOW}2. 备份上传文件...${NC}"
if [ -d "backend/uploads" ]; then
    tar -czf "${BACKUP_DIR}/files/uploads_${BACKUP_DATE}.tar.gz" -C backend uploads
    UPLOAD_SIZE=$(du -h "${BACKUP_DIR}/files/uploads_${BACKUP_DATE}.tar.gz" | cut -f1)
    echo -e "${GREEN}✓ 上传文件备份完成: ${UPLOAD_SIZE}${NC}"
else
    echo -e "${YELLOW}⚠️  未找到上传文件目录，跳过${NC}"
fi

# 3. 备份配置文件
echo -e "${YELLOW}3. 备份配置文件...${NC}"
tar -czf "${BACKUP_DIR}/files/config_${BACKUP_DATE}.tar.gz" \
    .env \
    docker-compose.prod.yml \
    deploy/config/ \
    deploy/nginx/ \
    --exclude="deploy/backup"

CONFIG_SIZE=$(du -h "${BACKUP_DIR}/files/config_${BACKUP_DATE}.tar.gz" | cut -f1)
echo -e "${GREEN}✓ 配置文件备份完成: ${CONFIG_SIZE}${NC}"

# 4. 清理旧备份
echo -e "${YELLOW}4. 清理${BACKUP_RETENTION_DAYS}天前的旧备份...${NC}"
find "${BACKUP_DIR}/mysql" -name "*.sql.gz" -type f -mtime +${BACKUP_RETENTION_DAYS} -delete
find "${BACKUP_DIR}/files" -name "*.tar.gz" -type f -mtime +${BACKUP_RETENTION_DAYS} -delete

DELETED_COUNT=$(find "${BACKUP_DIR}" -name "*.gz" -type f -mtime +${BACKUP_RETENTION_DAYS} | wc -l)
echo -e "${GREEN}✓ 清理完成，删除了 ${DELETED_COUNT} 个旧备份文件${NC}"

# 5. 生成备份报告
echo -e "${YELLOW}5. 生成备份报告...${NC}"
TOTAL_SIZE=$(du -sh "${BACKUP_DIR}" | cut -f1)
FILE_COUNT=$(find "${BACKUP_DIR}" -name "*.gz" -type f | wc -l)

cat > "${BACKUP_DIR}/backup_report_${BACKUP_DATE}.log" << EOF
AI情感助手备份报告
==================
备份时间: ${BACKUP_DATE}
备份类型: 自动定时备份
保留天数: ${BACKUP_RETENTION_DAYS} 天
总备份大小: ${TOTAL_SIZE}
总备份文件数: ${FILE_COUNT}

备份文件列表:
- 数据库备份: mysql/emotion_ai_${BACKUP_DATE}.sql.gz (${BACKUP_SIZE})
- 上传文件备份: files/uploads_${BACKUP_DATE}.tar.gz (${UPLOAD_SIZE:-0})
- 配置文件备份: files/config_${BACKUP_DATE}.tar.gz (${CONFIG_SIZE})
EOF

echo -e "${GREEN}✓ 备份报告生成完成${NC}"
echo ""

# 完成提示
echo -e "${GREEN}=============================================${NC}"
echo -e "${GREEN}✅ 备份完成！${NC}"
echo -e "${GREEN}=============================================${NC}"
echo ""
echo -e "${YELLOW}备份统计:${NC}"
echo -e "  总大小: ${TOTAL_SIZE}"
echo -e "  文件数: ${FILE_COUNT}"
echo -e "  保留天数: ${BACKUP_RETENTION_DAYS} 天"
echo ""
echo -e "${YELLOW}备份文件位置:${NC}"
echo -e "  数据库: ${BACKUP_DIR}/mysql/emotion_ai_${BACKUP_DATE}.sql.gz"
echo -e "  上传文件: ${BACKUP_DIR}/files/uploads_${BACKUP_DATE}.tar.gz"
echo -e "  配置文件: ${BACKUP_DIR}/files/config_${BACKUP_DATE}.tar.gz"
echo -e "  备份报告: ${BACKUP_DIR}/backup_report_${BACKUP_DATE}.log"
echo ""

# 如果配置了告警，这里可以添加邮件/企业微信/钉钉告警通知
# if [ ! -z "${ALERT_WEBHOOK}" ]; then
#     # 发送告警通知
# fi
