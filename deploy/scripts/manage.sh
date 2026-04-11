#!/bin/bash
set -e

# 服务管理脚本
# 提供便捷的服务管理命令

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$PROJECT_ROOT"

# 检查配置文件
if [ ! -f ".env" ]; then
    echo -e "${RED}错误: 未找到 .env 文件，请先运行部署脚本${NC}"
    exit 1
fi
source .env

COMPOSE_FILE="docker-compose.prod.yml"

show_help() {
    echo -e "${GREEN}AI情感助手服务管理脚本${NC}"
    echo -e "用法: $0 [命令] [选项]"
    echo ""
    echo -e "可用命令:"
    echo -e "  start           启动所有服务"
    echo -e "  stop            停止所有服务"
    echo -e "  restart         重启所有服务"
    echo -e "  status          查看服务状态"
    echo -e "  logs [服务名]   查看服务日志（不加服务名查看所有）"
    echo -e "  build [服务名]  重新构建服务镜像"
    echo -e "  update          更新到最新版本"
    echo -e "  health          健康检查"
    echo -e "  cleanup         清理无用资源"
    echo -e "  shell <服务名>  进入服务容器shell"
    echo -e "  backup          手动执行备份"
    echo -e "  restore         执行数据恢复"
    echo -e "  ssl             配置SSL证书"
    echo -e "  help            显示此帮助信息"
    echo ""
    echo -e "示例:"
    echo -e "  $0 status                # 查看所有服务状态"
    echo -e "  $0 logs backend          # 查看后端服务日志"
    echo -e "  $0 restart nginx         # 重启Nginx服务"
    echo -e "  $0 build backend         # 重新构建后端镜像"
    echo -e "  $0 update                # 拉取最新代码并重启服务"
}

start_services() {
    echo -e "${GREEN}启动所有服务...${NC}"
    docker-compose -f "${COMPOSE_FILE}" up -d "$@"
}

stop_services() {
    echo -e "${YELLOW}停止所有服务...${NC}"
    docker-compose -f "${COMPOSE_FILE}" down "$@"
}

restart_services() {
    echo -e "${YELLOW}重启服务...${NC}"
    docker-compose -f "${COMPOSE_FILE}" restart "$@"
}

show_status() {
    echo -e "${GREEN}服务状态:${NC}"
    docker-compose -f "${COMPOSE_FILE}" ps
}

show_logs() {
    echo -e "${GREEN}查看日志: $@${NC}"
    docker-compose -f "${COMPOSE_FILE}" logs -f --tail 100 "$@"
}

build_service() {
    echo -e "${YELLOW}构建服务镜像: $@${NC}"
    docker-compose -f "${COMPOSE_FILE}" build --no-cache "$@"
}

update_system() {
    echo -e "${YELLOW}更新系统到最新版本...${NC}"
    
    # 备份数据
    echo -e "${YELLOW}1. 执行备份...${NC}"
    ./deploy/scripts/backup.sh
    
    # 拉取最新代码
    echo -e "${YELLOW}2. 拉取最新代码...${NC}"
    git pull
    
    # 重新构建镜像
    echo -e "${YELLOW}3. 重新构建服务镜像...${NC}"
    docker-compose -f "${COMPOSE_FILE}" build --no-cache backend web
    
    # 重启服务
    echo -e "${YELLOW}4. 重启服务...${NC}"
    docker-compose -f "${COMPOSE_FILE}" up -d
    
    # 健康检查
    echo -e "${YELLOW}5. 健康检查...${NC}"
    sleep 10
    health_check
    
    echo -e "${GREEN}✅ 系统更新完成！${NC}"
}

health_check() {
    echo -e "${GREEN}健康检查:${NC}"
    
    # 检查服务状态
    echo -e "\n${YELLOW}服务状态:${NC}"
    docker-compose -f "${COMPOSE_FILE}" ps
    
    # 检查后端健康
    echo -e "\n${YELLOW}后端健康检查:${NC}"
    if curl -s http://localhost:8000/health | python3 -m json.tool 2>/dev/null || curl -s http://localhost:8000/health; then
        echo -e "${GREEN}✓ 后端服务正常${NC}"
    else
        echo -e "${RED}✗ 后端服务异常${NC}"
    fi
    
    # 检查Nginx健康
    echo -e "\n${YELLOW}Nginx健康检查:${NC}"
    if curl -s http://localhost/health; then
        echo -e "\n${GREEN}✓ Nginx服务正常${NC}"
    else
        echo -e "\n${RED}✗ Nginx服务异常${NC}"
    fi
    
    # 检查磁盘空间
    echo -e "\n${YELLOW}磁盘空间使用:${NC}"
    df -h | grep -E 'Filesystem|/dev/'
    
    # 检查内存使用
    echo -e "\n${YELLOW}内存使用:${NC}"
    free -h
}

cleanup_system() {
    echo -e "${YELLOW}清理系统资源...${NC}"
    
    # 清理无用镜像
    echo -e "${YELLOW}清理无用Docker镜像...${NC}"
    docker image prune -af
    
    # 清理无用容器
    echo -e "${YELLOW}清理无用Docker容器...${NC}"
    docker container prune -f
    
    # 清理无用卷
    echo -e "${YELLOW}清理无用Docker卷...${NC}"
    docker volume prune -f
    
    # 清理系统缓存
    echo -e "${YELLOW}清理系统缓存...${NC}"
    if command -v apt-get &> /dev/null; then
        apt-get autoremove -y
        apt-get clean
    fi
    
    echo -e "${GREEN}✓ 系统清理完成${NC}"
}

enter_shell() {
    if [ $# -eq 0 ]; then
        echo -e "${RED}错误: 请指定要进入的服务名${NC}"
        echo -e "可用服务: mysql, redis, backend, web, nginx"
        exit 1
    fi
    
    service_name="$1"
    echo -e "${GREEN}进入 ${service_name} 容器shell...${NC}"
    docker-compose -f "${COMPOSE_FILE}" exec "${service_name}" sh || docker-compose -f "${COMPOSE_FILE}" exec "${service_name}" bash
}

# 主命令处理
case "$1" in
    start)
        shift
        start_services "$@"
        ;;
    stop)
        shift
        stop_services "$@"
        ;;
    restart)
        shift
        restart_services "$@"
        ;;
    status)
        show_status
        ;;
    logs)
        shift
        show_logs "$@"
        ;;
    build)
        shift
        build_service "$@"
        ;;
    update)
        update_system
        ;;
    health)
        health_check
        ;;
    cleanup)
        cleanup_system
        ;;
    shell)
        shift
        enter_shell "$@"
        ;;
    backup)
        ./deploy/scripts/backup.sh
        ;;
    restore)
        ./deploy/scripts/restore.sh
        ;;
    ssl)
        ./deploy/scripts/ssl.sh
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo -e "${RED}错误: 未知命令 '$1'${NC}"
        show_help
        exit 1
        ;;
esac
