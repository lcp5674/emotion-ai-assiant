#!/bin/bash
set -e

# 数据恢复脚本
# 从备份文件恢复数据

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

BACKUP_DIR="${BACKUP_DIR:-./deploy/backup}"
MYSQL_CONTAINER="emotion-ai-mysql"

echo -e "${RED}=============================================${NC}"
echo -e "${RED}⚠️  数据恢复警告${NC}"
echo -e "${RED}=============================================${NC}"
echo -e "${RED}此操作将会覆盖现有数据！请确保已做好必要的备份。${NC}"
echo ""
read -p "确认要继续恢复操作吗？(yes/N) " -r
if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
    echo -e "${YELLOW}操作已取消${NC}"
    exit 0
fi
echo ""

# 显示可用备份
echo -e "${YELLOW}可用的数据库备份:${NC}"
ls -la "${BACKUP_DIR}/mysql/" | grep ".sql.gz" | sort -r
echo ""

read -p "请输入要恢复的数据库备份文件名（如: emotion_ai_20240101_120000.sql.gz）: " -r DB_BACKUP_FILE
DB_BACKUP_PATH="${BACKUP_DIR}/mysql/${DB_BACKUP_FILE}"

if [ ! -f "${DB_BACKUP_PATH}" ]; then
    echo -e "${RED}错误: 备份文件不存在: ${DB_BACKUP_PATH}${NC}"
    exit 1
fi

echo ""
echo -e "${YELLOW}要恢复的备份文件: ${DB_BACKUP_PATH}${NC}"
read -p "确认要恢复此数据库备份吗？(y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}操作已取消${NC}"
    exit 0
fi
echo ""

# 1. 恢复数据库
echo -e "${YELLOW}1. 恢复MySQL数据库...${NC}"

# 停止后端服务，避免写入
echo -e "${YELLOW}停止后端服务...${NC}"
docker-compose -f docker-compose.prod.yml stop backend

# 等待服务停止
sleep 5

# 导入数据库
echo -e "${YELLOW}导入数据库备份...${NC}"
gunzip -c "${DB_BACKUP_PATH}" | docker exec -i "${MYSQL_CONTAINER}" mysql \
    -u"${MYSQL_USER}" \
    -p"${MYSQL_PASSWORD}" \
    "${MYSQL_DATABASE}"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ 数据库恢复完成${NC}"
else
    echo -e "${RED}错误: 数据库恢复失败${NC}"
    # 启动后端服务
    docker-compose -f docker-compose.prod.yml start backend
    exit 1
fi

# 2. 恢复文件（可选）
echo ""
read -p "是否需要恢复上传文件？(y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}可用的文件备份:${NC}"
    ls -la "${BACKUP_DIR}/files/" | grep "uploads_" | sort -r
    echo ""
    
    read -p "请输入要恢复的上传文件备份文件名（如: uploads_20240101_120000.tar.gz）: " -r FILE_BACKUP_FILE
    FILE_BACKUP_PATH="${BACKUP_DIR}/files/${FILE_BACKUP_FILE}"
    
    if [ ! -f "${FILE_BACKUP_PATH}" ]; then
        echo -e "${RED}错误: 备份文件不存在: ${FILE_BACKUP_PATH}${NC}"
    else
        echo -e "${YELLOW}恢复上传文件...${NC}"
        # 备份当前上传文件
        if [ -d "backend/uploads" ]; then
            mv backend/uploads backend/uploads.bak.$(date +%Y%m%d_%H%M%S)
        fi
        # 恢复备份
        tar -xzf "${FILE_BACKUP_PATH}" -C backend
        echo -e "${GREEN}✓ 上传文件恢复完成${NC}"
    fi
fi

# 3. 恢复配置文件（可选）
echo ""
read -p "是否需要恢复配置文件？(y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}可用的配置备份:${NC}"
    ls -la "${BACKUP_DIR}/files/" | grep "config_" | sort -r
    echo ""
    
    read -p "请输入要恢复的配置文件备份文件名（如: config_20240101_120000.tar.gz）: " -r CONFIG_BACKUP_FILE
    CONFIG_BACKUP_PATH="${BACKUP_DIR}/files/${CONFIG_BACKUP_FILE}"
    
    if [ ! -f "${CONFIG_BACKUP_PATH}" ]; then
        echo -e "${RED}错误: 备份文件不存在: ${CONFIG_BACKUP_PATH}${NC}"
    else
        echo -e "${YELLOW}恢复配置文件...${NC}"
        # 备份当前配置
        mkdir -p config.bak.$(date +%Y%m%d_%H%M%S)
        cp -r .env docker-compose.prod.yml deploy/config deploy/nginx config.bak.$(date +%Y%m%d_%H%M%S)/
        # 恢复备份
        tar -xzf "${CONFIG_BACKUP_PATH}" -C .
        echo -e "${GREEN}✓ 配置文件恢复完成${NC}"
    fi
fi

# 4. 重启服务
echo ""
echo -e "${YELLOW}4. 重启所有服务...${NC}"
docker-compose -f docker-compose.prod.yml up -d

# 等待服务启动
sleep 10

# 5. 验证恢复
echo -e "${YELLOW}5. 验证恢复结果...${NC}"
if curl -s http://localhost:8000/health | grep -q "ok"; then
    echo -e "${GREEN}✓ 后端服务正常${NC}"
else
    echo -e "${RED}错误: 后端服务异常，请检查日志${NC}"
    exit 1
fi

if curl -s http://localhost/health | grep -q "ok"; then
    echo -e "${GREEN}✓ 前端服务正常${NC}"
else
    echo -e "${RED}错误: 前端服务异常，请检查日志${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}=============================================${NC}"
echo -e "${GREEN}✅ 数据恢复完成！${NC}"
echo -e "${GREEN}=============================================${NC}"
echo ""
echo -e "${YELLOW}恢复信息:${NC}"
echo -e "  数据库备份: ${DB_BACKUP_FILE}"
echo -e "  恢复时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""
echo -e "${YELLOW}请验证系统功能是否正常。如果有问题，可以从备份的文件中恢复。${NC}"
