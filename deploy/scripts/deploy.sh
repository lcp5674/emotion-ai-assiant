#!/bin/bash
set -e

# AI情感助手一键部署脚本
# 生产环境部署自动化

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$PROJECT_ROOT"

echo -e "${GREEN}=============================================${NC}"
echo -e "${GREEN}AI情感助手生产环境一键部署脚本${NC}"
echo -e "${GREEN}=============================================${NC}"
echo ""

# 检查是否为root用户
if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}错误: 请使用root权限运行此脚本${NC}" 
   exit 1
fi

# 检查Docker和Docker Compose
check_dependencies() {
    echo -e "${YELLOW}1. 检查系统依赖...${NC}"
    
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}错误: Docker 未安装，请先安装 Docker${NC}"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        echo -e "${RED}错误: Docker Compose 未安装，请先安装 Docker Compose${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✓ Docker 版本: $(docker --version | cut -d' ' -f3)${NC}"
    echo -e "${GREEN}✓ Docker Compose 版本: $(docker-compose --version | cut -d' ' -f3)${NC}"
    echo ""
}

# 检查配置文件
check_config() {
    echo -e "${YELLOW}2. 检查配置文件...${NC}"
    
    if [ ! -f ".env" ]; then
        echo -e "${YELLOW}⚠️  未找到 .env 文件，正在从模板创建...${NC}"
        cp .env.example .env
        echo -e "${YELLOW}⚠️  请编辑 .env 文件配置生产环境参数，然后重新运行脚本${NC}"
        exit 0
    fi
    
    # 加载环境变量
    source .env
    
    # 检查必要配置
    required_vars=("MYSQL_ROOT_PASSWORD" "MYSQL_PASSWORD" "REDIS_PASSWORD" "SECRET_KEY" "GRAFANA_PASSWORD")
    for var in "${required_vars[@]}"; do
        if [ -z "${!var}" ] || [[ "${!var}" == *"your_strong"* ]]; then
            echo -e "${RED}错误: 请在 .env 文件中配置 ${var} 为强密码${NC}"
            exit 1
        fi
    done
    
    # 检查SECRET_KEY长度
    if [ ${#SECRET_KEY} -lt 32 ]; then
        echo -e "${RED}错误: SECRET_KEY 长度必须至少32个字符${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✓ 配置文件检查通过${NC}"
    echo ""
}

# 创建必要目录
create_directories() {
    echo -e "${YELLOW}3. 创建必要目录...${NC}"
    
    dirs=(
        "deploy/backup/mysql"
        "deploy/backup/files"
        "deploy/ssl"
        "deploy/logs"
        "backend/uploads"
    )
    
    for dir in "${dirs[@]}"; do
        if [ ! -d "$dir" ]; then
            mkdir -p "$dir"
            echo -e "${GREEN}✓ 创建目录: $dir${NC}"
        fi
    done
    
    # 设置权限
    chmod -R 755 deploy/backup
    chmod -R 700 deploy/ssl
    
    echo -e "${GREEN}✓ 目录创建完成${NC}"
    echo ""
}

# 数据库初始化
init_database() {
    echo -e "${YELLOW}4. 初始化数据库...${NC}"
    
    # 检查数据库是否已经初始化
    if docker volume inspect emotion-ai-assistant_mysql_data &> /dev/null; then
        echo -e "${YELLOW}⚠️  数据库已存在，跳过初始化${NC}"
        return
    fi
    
    # 启动数据库服务
    echo -e "${YELLOW}启动数据库服务...${NC}"
    docker-compose -f docker-compose.prod.yml up -d mysql redis
    
    # 等待数据库就绪
    echo -e "${YELLOW}等待数据库就绪...${NC}"
    until docker-compose -f docker-compose.prod.yml exec -T mysql mysqladmin ping -h localhost -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" --silent; do
        sleep 2
        echo -n "."
    done
    echo ""
    
    echo -e "${GREEN}✓ 数据库初始化完成${NC}"
    echo ""
}

# 构建并启动服务
start_services() {
    echo -e "${YELLOW}5. 构建并启动所有服务...${NC}"
    
    # 拉取最新镜像
    echo -e "${YELLOW}拉取基础镜像...${NC}"
    docker-compose -f docker-compose.prod.yml pull
    
    # 构建服务
    echo -e "${YELLOW}构建服务镜像...${NC}"
    docker-compose -f docker-compose.prod.yml build --no-cache backend web
    
    # 启动所有服务
    echo -e "${YELLOW}启动所有服务...${NC}"
    docker-compose -f docker-compose.prod.yml up -d
    
    echo -e "${GREEN}✓ 服务启动完成${NC}"
    echo ""
}

# 健康检查
health_check() {
    echo -e "${YELLOW}6. 服务健康检查...${NC}"
    
    # 等待服务启动
    sleep 10
    
    # 检查所有服务状态
    echo -e "${YELLOW}检查服务状态:${NC}"
    docker-compose -f docker-compose.prod.yml ps
    
    # 检查后端健康状态
    echo -e "${YELLOW}检查后端服务健康状态...${NC}"
    for i in {1..10}; do
        if curl -s http://localhost:8000/health | grep -q "ok"; then
            echo -e "${GREEN}✓ 后端服务健康检查通过${NC}"
            break
        fi
        sleep 3
        echo -n "."
        if [ $i -eq 10 ]; then
            echo -e "${RED}错误: 后端服务健康检查失败${NC}"
            exit 1
        fi
    done
    
    # 检查Nginx健康状态
    echo -e "${YELLOW}检查Nginx服务健康状态...${NC}"
    for i in {1..10}; do
        if curl -s http://localhost/health | grep -q "ok"; then
            echo -e "${GREEN}✓ Nginx服务健康检查通过${NC}"
            break
        fi
        sleep 3
        echo -n "."
        if [ $i -eq 10 ]; then
            echo -e "${RED}错误: Nginx服务健康检查失败${NC}"
            exit 1
        fi
    done
    
    echo ""
}

# 配置定时任务
setup_cron() {
    echo -e "${YELLOW}7. 配置定时任务...${NC}"
    
    # 添加备份任务
    backup_script="$PROJECT_ROOT/deploy/scripts/backup.sh"
    cron_job="$BACKUP_CRON root $backup_script >> /var/log/emotion-ai-backup.log 2>&1"
    
    # 检查是否已存在
    if ! grep -q "$backup_script" /etc/crontab; then
        echo "$cron_job" >> /etc/crontab
        echo -e "${GREEN}✓ 已添加定时备份任务${NC}"
    else
        echo -e "${YELLOW}⚠️  定时备份任务已存在${NC}"
    fi
    
    # 重启cron服务
    if command -v systemctl &> /dev/null; then
        systemctl restart cron
    else
        service cron restart
    fi
    
    echo -e "${GREEN}✓ 定时任务配置完成${NC}"
    echo ""
}

# 部署完成提示
show_complete() {
    echo -e "${GREEN}=============================================${NC}"
    echo -e "${GREEN}✅ 部署完成！${NC}"
    echo -e "${GREEN}=============================================${NC}"
    echo ""
    echo -e "${YELLOW}服务访问地址:${NC}"
    echo -e "  前端应用: http://localhost"
    echo -e "  后端API: http://localhost/api"
    echo -e "  健康检查: http://localhost/health"
    echo ""
    echo -e "${YELLOW}下一步操作:${NC}"
    echo -e "  1. 配置域名解析到服务器IP"
    echo -e "  2. 运行 ./deploy/scripts/ssl.sh 配置SSL证书"
    echo -e "  3. 配置防火墙规则，开放80和443端口"
    echo -e "  4. 阅读运维手册了解更多运维操作"
    echo ""
    echo -e "${YELLOW}常用命令:${NC}"
    echo -e "  查看服务状态: docker-compose -f docker-compose.prod.yml ps"
    echo -e "  查看服务日志: docker-compose -f docker-compose.prod.yml logs -f [服务名]"
    echo -e "  重启服务: docker-compose -f docker-compose.prod.yml restart [服务名]"
    echo -e "  停止服务: docker-compose -f docker-compose.prod.yml down"
    echo ""
    echo -e "${GREEN}部署日志已保存到 deploy/logs/deploy_$(date +%Y%m%d_%H%M%S).log${NC}"
}

# 主流程
main() {
    # 创建日志目录
    mkdir -p deploy/logs
    LOG_FILE="deploy/logs/deploy_$(date +%Y%m%d_%H%M%S).log"
    exec > >(tee -a "$LOG_FILE") 2>&1
    
    check_dependencies
    check_config
    create_directories
    init_database
    start_services
    health_check
    setup_cron
    show_complete
}

main "$@"
