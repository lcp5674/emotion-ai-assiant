#!/usr/bin/env bash
set -euo pipefail

# ============================================
# Docker 部署脚本
# 用法: ./scripts/docker-deploy.sh [dev|prod]
# ============================================

ENV="${1:-dev}"
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "========================================"
echo "  部署环境: ${ENV}"
echo "  项目路径: ${PROJECT_ROOT}"
echo "========================================"

if [ "${ENV}" = "prod" ]; then
    COMPOSE_FILE="docker-compose.prod.yml"
    echo "  生产模式: 启用 HTTPS、资源限制、日志轮转"
else
    COMPOSE_FILE="docker-compose.yml"
    echo "  开发模式: 基础配置、端口映射"
fi

echo "========================================"

# 检查前置条件
command -v docker >/dev/null 2>&1 || { echo "错误: Docker 未安装"; exit 1; }
command -v docker compose >/dev/null 2>&1 || { echo "错误: Docker Compose 未安装"; exit 1; }

# 检查配置文件
if [ ! -f ".env.docker" ]; then
    echo "警告: .env.docker 不存在，从示例文件复制..."
    cp .env.docker.example .env.docker
    echo "请编辑 .env.docker 设置密码和密钥后重新运行"
    exit 1
fi

if [ ! -f "backend/.env.docker" ]; then
    echo "警告: backend/.env.docker 不存在，从示例文件复制..."
    cp backend/.env.docker.example backend/.env.docker
    echo "请编辑 backend/.env.docker 设置配置后重新运行"
    exit 1
fi

case "${2:-up}" in
    up)
        echo "启动服务..."
        docker compose -f "${COMPOSE_FILE}" up -d --build
        echo "等待服务启动..."
        sleep 10
        docker compose -f "${COMPOSE_FILE}" ps
        echo ""
        echo "验证健康检查..."
        curl -sf http://localhost:8000/health && echo " 后端: OK" || echo " 后端: 等待中..."
        curl -sf http://localhost/ && echo " 前端: OK" || echo " 前端: 等待中..."
        ;;
    down)
        echo "停止服务..."
        docker compose -f "${COMPOSE_FILE}" down
        ;;
    logs)
        docker compose -f "${COMPOSE_FILE}" logs -f "${3:-}"
        ;;
    rebuild)
        echo "重新构建..."
        docker compose -f "${COMPOSE_FILE}" build --no-cache
        docker compose -f "${COMPOSE_FILE}" up -d
        ;;
    status)
        docker compose -f "${COMPOSE_FILE}" ps
        docker compose -f "${COMPOSE_FILE}" top
        ;;
    *)
        echo "用法: $0 [dev|prod] [up|down|logs|rebuild|status]"
        echo "  up      - 启动服务 (默认)"
        echo "  down    - 停止服务"
        echo "  logs    - 查看日志 (可跟服务名)"
        echo "  rebuild - 重新构建并启动"
        echo "  status  - 查看状态"
        exit 1
        ;;
esac
