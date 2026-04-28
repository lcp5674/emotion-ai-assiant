#!/bin/bash
# 一键部署脚本 - 彻底解决挂载不一致问题
# 使用方法: bash deploy/deploy.sh

set -e

echo "=========================================="
echo "  情感AI助手 - 一键部署脚本"
echo "=========================================="
echo ""

# 检查docker-compose文件
if [ ! -f "docker-compose.prod.yml" ]; then
    echo "错误: docker-compose.prod.yml 文件不存在"
    exit 1
fi

# 进入项目根目录
cd "$(dirname "$0")/.."

echo "[1/4] 构建前端..."
cd frontend/web
npm run build
cd ../..
echo "      前端构建完成 ✓"

echo "[2/4] 停止旧容器..."
docker compose -f docker-compose.prod.yml stop nginx 2>/dev/null || true
docker compose -f docker-compose.prod.yml rm -f nginx 2>/dev/null || true
echo "      旧容器已停止 ✓"

echo "[3/4] 重新构建nginx镜像（包含最新前端代码）..."
docker compose -f docker-compose.prod.yml build --no-cache nginx
echo "      nginx镜像构建完成 ✓"

echo "[4/4] 启动nginx服务..."
# 使用 printf y 来自动应答 volume 重建提示
printf 'y\n' | docker compose -f docker-compose.prod.yml up -d nginx
echo "      服务启动完成 ✓"

echo ""
echo "=========================================="
echo "  部署完成！"
echo "=========================================="
echo ""
echo "访问地址: http://118.25.110.184:8080"
echo ""
docker compose -f docker-compose.prod.yml ps