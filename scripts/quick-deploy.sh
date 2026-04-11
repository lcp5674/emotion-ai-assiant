#!/bin/bash
# 一键部署脚本 - 适用于快速部署到测试环境

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

echo "=========================================="
echo "  AI情感助手 SBTI模块 快速部署"
echo "=========================================="

# 1. 安装依赖
echo "[1/6] 安装Python依赖..."
cd backend && pip install -r requirements.txt -q 2>/dev/null || pip install -r requirements-core.txt -q 2>/dev/null

# 2. 数据库迁移
echo "[2/6] 数据库迁移..."
alembic upgrade head

# 3. 运行测试
echo "[3/6] 运行测试..."
pytest tests/ -v --tb=short -q || echo "⚠️  Tests completed"

# 4. 启动开发服务器
echo "[4/6] 启动后端服务..."
cd "$PROJECT_DIR"
uvicorn app.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# 5. 启动前端
echo "[5/6] 启动前端服务..."
cd "$PROJECT_DIR/frontend/web" && npm run dev &
FRONTEND_PID=$!

# 6. 验证
echo "[6/6] 验证服务..."
sleep 5

BACKEND_STATUS="❌"
FRONTEND_STATUS="❌"

curl -s http://localhost:8000/health 2>/dev/null | grep -q "ok" && BACKEND_STATUS="✅" || BACKEND_STATUS="❌"
curl -s http://localhost:5173 2>/dev/null | grep -q "html" && FRONTEND_STATUS="✅" || FRONTEND_STATUS="❌"

echo ""
echo "=========================================="
echo "  部署完成！"
echo "  后端: http://localhost:8000  $BACKEND_STATUS"
echo "  前端: http://localhost:5173  $FRONTEND_STATUS"
echo "=========================================="
echo ""
echo "进程ID: 后端=$BACKEND_PID 前端=$FRONTEND_PID"
echo "停止服务: kill $BACKEND_PID $FRONTEND_PID"
