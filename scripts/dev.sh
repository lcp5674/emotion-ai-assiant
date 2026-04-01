#!/bin/bash

# 心灵伴侣AI - 开发环境一键启停脚本
# 适用于 macOS 测试环境

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目根目录
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"

# 配置
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend/web"
VENV_DIR="$BACKEND_DIR/venv"
LOG_DIR="$PROJECT_ROOT/logs"

# PID文件
BACKEND_PID_FILE="$LOG_DIR/backend.pid"
FRONTEND_PID_FILE="$LOG_DIR/frontend.pid"

# 创建日志目录
mkdir -p "$LOG_DIR"

# 日志文件
BACKEND_LOG="$LOG_DIR/backend.log"
FRONTEND_LOG="$LOG_DIR/frontend.log"

# =======================
# 辅助函数
# =======================

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

# 检查命令是否存在
check_command() {
    if ! command -v "$1" &> /dev/null; then
        log_error "$1 未安装，请先安装: $2"
        return 1
    fi
    return 0
}

# 检查端口是否占用
check_port() {
    lsof -i :$1 &>/dev/null
}

# 读取PID
read_pid() {
    local pid_file=$1
    if [ -f "$pid_file" ]; then
        cat "$pid_file"
    fi
}

# 检查进程是否运行
is_process_running() {
    local pid=$1
    if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
        return 0
    fi
    return 1
}

# =======================
# 环境检查
# =======================

check_environment() {
    log_info "检查开发环境..."

    # 检查 Python
    if ! check_command python3 "Python 3.8+" "https://www.python.org/downloads/"; then
        return 1
    fi

    # 检查 Node.js
    if ! check_command node "Node.js 18+" "https://nodejs.org/"; then
        return 1
    fi

    # 检查 npm
    if ! check_command npm "npm" "https://nodejs.org/"; then
        return 1
    fi

    log_success "环境检查通过"
    return 0
}

# =======================
# 初始化环境
# =======================

init_environment() {
    log_info "初始化开发环境..."

    # 1. 设置Python虚拟环境
    if [ ! -d "$VENV_DIR" ]; then
        log_info "创建Python虚拟环境..."
        python3 -m venv "$VENV_DIR"
    fi

    # 激活虚拟环境
    source "$VENV_DIR/bin/activate"

    # 2. 安装后端依赖
    log_info "安装后端依赖..."
    pip install --upgrade pip -q
    pip install -r "$BACKEND_DIR/requirements.txt" -q

    # 3. 安装前端依赖
    log_info "安装前端依赖..."
    cd "$FRONTEND_DIR"
    if [ ! -d "node_modules" ]; then
        npm install
    fi

    # 4. 创建环境配置
    if [ ! -f "$BACKEND_DIR/.env" ]; then
        log_info "创建环境配置文件..."
        cat > "$BACKEND_DIR/.env" << 'EOF'
# 应用配置
APP_NAME=心灵伴侣AI
APP_VERSION=1.0.0
DEBUG=true

# 服务器
HOST=0.0.0.0
PORT=8000

# 数据库 (使用SQLite轻量测试)
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=root
MYSQL_DATABASE=emotion_ai

# 使用SQLite (轻量测试)
DATABASE_URL=sqlite:///./emotion_ai.db

# Redis (开发环境使用内存模拟)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0

# JWT
SECRET_KEY=dev-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# 大模型 (使用Mock)
LLM_PROVIDER=mock

# 向量数据库 (使用内存)
VECTOR_DB_TYPE=memory

# CORS
CORS_ORIGINS=["http://localhost:5173","http://localhost:3000"]
EOF
    fi

    # 恢复目录
    cd "$PROJECT_ROOT"

    log_success "环境初始化完成"
}

# =======================
# 启动服务
# =======================

start_backend() {
    log_info "启动后端服务..."

    # 激活虚拟环境
    source "$VENV_DIR/bin/activate"

    # 检查是否已运行
    local backend_pid=$(read_pid "$BACKEND_PID_FILE")
    if [ -n "$backend_pid" ] && is_process_running "$backend_pid"; then
        log_warning "后端服务已在运行 (PID: $backend_pid)"
        return 0
    fi

    # 检查端口
    if check_port 8000; then
        log_warning "端口8000已被占用，尝试关闭..."
        lsof -ti:8000 | xargs kill -9 2>/dev/null || true
        sleep 1
    fi

    # 启动后端
    cd "$BACKEND_DIR"
    nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > "$BACKEND_LOG" 2>&1 &
    local pid=$!
    echo "$pid" > "$BACKEND_PID_FILE"

    # 等待启动
    local count=0
    while [ $count -lt 30 ]; do
        if curl -s http://localhost:8000/health &>/dev/null; then
            log_success "后端服务已启动 (PID: $pid)"
            log_info "API文档: http://localhost:8000/docs"
            return 0
        fi
        sleep 1
        count=$((count + 1))
    done

    log_error "后端服务启动失败，请查看日志: $BACKEND_LOG"
    return 1
}

start_frontend() {
    log_info "启动前端服务..."

    cd "$FRONTEND_DIR"

    # 检查是否已运行
    local frontend_pid=$(read_pid "$FRONTEND_PID_FILE")
    if [ -n "$frontend_pid" ] && is_process_running "$frontend_pid"; then
        log_warning "前端服务已在运行 (PID: $frontend_pid)"
        return 0
    fi

    # 检查端口
    if check_port 5173; then
        log_warning "端口5173已被占用，尝试关闭..."
        lsof -ti:5173 | xargs kill -9 2>/dev/null || true
        sleep 1
    fi

    # 启动前端
    nohup npm run dev > "$FRONTEND_LOG" 2>&1 &
    local pid=$!
    echo "$pid" > "$FRONTEND_PID_FILE"

    # 等待启动
    local count=0
    while [ $count -lt 30 ]; do
        if curl -s http://localhost:5173 &>/dev/null; then
            log_success "前端服务已启动 (PID: $pid)"
            log_info "访问地址: http://localhost:5173"
            return 0
        fi
        sleep 1
        count=$((count + 1))
    done

    log_error "前端服务启动失败，请查看日志: $FRONTEND_LOG"
    return 1
}

start_all() {
    log_info "========================================="
    log_info "  启动心灵伴侣AI开发环境"
    log_info "========================================="

    # 初始化环境
    if ! init_environment; then
        log_error "环境初始化失败"
        exit 1
    fi

    # 启动后端
    if ! start_backend; then
        log_error "后端启动失败"
        exit 1
    fi

    # 启动前端
    if ! start_frontend; then
        log_error "前端启动失败"
        exit 1
    fi

    echo ""
    log_success "========================================="
    log_success "  所有服务已启动！"
    log_success "========================================="
    log_info "前端页面: ${BLUE}http://localhost:5173${NC}"
    log_info "后端API:  ${BLUE}http://localhost:8000${NC}"
    log_info "API文档:  ${BLUE}http://localhost:8000/docs${NC}"
    echo ""
}

# =======================
# 停止服务
# =======================

stop_backend() {
    log_info "停止后端服务..."

    local pid=$(read_pid "$BACKEND_PID_FILE")
    if [ -z "$pid" ] || ! is_process_running "$pid"; then
        # 尝试通过端口查找
        pid=$(lsof -ti:8000 2>/dev/null | head -1)
        if [ -z "$pid" ]; then
            log_warning "后端服务未运行"
            return 0
        fi
    fi

    kill "$pid" 2>/dev/null || true
    sleep 1

    # 强制杀死
    if is_process_running "$pid"; then
        kill -9 "$pid" 2>/dev/null || true
    fi

    rm -f "$BACKEND_PID_FILE"
    log_success "后端服务已停止"
}

stop_frontend() {
    log_info "停止前端服务..."

    local pid=$(read_pid "$FRONTEND_PID_FILE")
    if [ -z "$pid" ] || ! is_process_running "$pid"; then
        # 尝试通过端口查找
        pid=$(lsof -ti:5173 2>/dev/null | head -1)
        if [ -z "$pid" ]; then
            log_warning "前端服务未运行"
            return 0
        fi
    fi

    kill "$pid" 2>/dev/null || true
    sleep 1

    # 强制杀死
    if is_process_running "$pid"; then
        kill -9 "$pid" 2>/dev/null || true
    fi

    rm -f "$FRONTEND_PID_FILE"
    log_success "前端服务已停止"
}

stop_all() {
    log_info "========================================="
    log_info "  停止所有服务"
    log_info "========================================="

    stop_backend
    stop_frontend

    log_success "所有服务已停止"
}

# =======================
# 重启服务
# =======================

restart_all() {
    log_info "重启所有服务..."
    stop_all
    sleep 2
    start_all
}

# =======================
# 查看状态
# =======================

status() {
    echo "========================================="
    echo "  服务状态"
    echo "========================================="

    # 后端状态
    local backend_pid=$(read_pid "$BACKEND_PID_FILE")
    if [ -n "$backend_pid" ] && is_process_running "$backend_pid"; then
        echo -e "后端服务:  ${GREEN}运行中${NC} (PID: $backend_pid)"
    else
        # 检查端口
        if check_port 8000; then
            echo -e "后端服务:  ${YELLOW}运行中 (未知PID)${NC}"
        else
            echo -e "后端服务:  ${RED}未运行${NC}"
        fi
    fi

    # 前端状态
    local frontend_pid=$(read_pid "$FRONTEND_PID_FILE")
    if [ -n "$frontend_pid" ] && is_process_running "$frontend_pid"; then
        echo -e "前端服务:  ${GREEN}运行中${NC} (PID: $frontend_pid)"
    else
        # 检查端口
        if check_port 5173; then
            echo -e "前端服务:  ${YELLOW}运行中 (未知PID)${NC}"
        else
            echo -e "前端服务:  ${RED}未运行${NC}"
        fi
    fi

    echo ""
    echo "访问地址:"
    echo "  前端:  http://localhost:5173"
    echo "  API:   http://localhost:8000"
    echo "  文档:  http://localhost:8000/docs"
}

# =======================
# 查看日志
# =======================

logs() {
    local service=${1:-all}

    case $service in
        backend)
            if [ -f "$BACKEND_LOG" ]; then
                tail -f "$BACKEND_LOG"
            else
                log_error "后端日志不存在"
            fi
            ;;
        frontend)
            if [ -f "$FRONTEND_LOG" ]; then
                tail -f "$FRONTEND_LOG"
            else
                log_error "前端日志不存在"
            fi
            ;;
        all)
            echo "=== 后端日志 ==="
            tail -50 "$BACKEND_LOG" 2>/dev/null || echo "暂无日志"
            echo ""
            echo "=== 前端日志 ==="
            tail -50 "$FRONTEND_LOG" 2>/dev/null || echo "暂无日志"
            ;;
        *)
            log_error "用法: $0 logs [backend|frontend|all]"
            ;;
    esac
}

# =======================
# 清理
# =======================

clean() {
    log_info "清理开发环境..."

    # 停止所有服务
    stop_all

    # 删除日志
    rm -rf "$LOG_DIR"

    # 删除Python缓存
    find "$BACKEND_DIR" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find "$BACKEND_DIR" -type f -name "*.pyc" -delete 2>/dev/null || true

    # 删除前端缓存
    rm -rf "$FRONTEND_DIR/node_modules/.vite" 2>/dev/null || true

    # 删除数据库文件
    rm -f "$BACKEND_DIR/emotion_ai.db" 2>/dev/null || true

    log_success "清理完成"
}

# =======================
# 帮助
# =======================

help() {
    echo "========================================="
    echo "  心灵伴侣AI - 开发环境管理脚本"
    echo "========================================="
    echo ""
    echo "用法: $0 <command>"
    echo ""
    echo "命令:"
    echo "  start         启动所有服务"
    echo "  stop          停止所有服务"
    echo "  restart       重启所有服务"
    echo "  status        查看服务状态"
    echo "  logs          查看日志 (可选: backend/frontend/all)"
    echo "  clean         清理环境"
    echo "  init          初始化环境"
    echo "  help          显示帮助"
    echo ""
    echo "示例:"
    echo "  $0 start          # 启动所有服务"
    echo "  $0 status         # 查看状态"
    echo "  $0 logs backend   # 查看后端日志"
    echo "  $0 restart        # 重启服务"
}

# =======================
# 主程序
# =======================

# 检查环境
if ! check_environment; then
    exit 1
fi

# 处理命令
case ${1:-help} in
    start)
        start_all
        ;;
    stop)
        stop_all
        ;;
    restart)
        restart_all
        ;;
    status)
        status
        ;;
    logs)
        logs ${2:-all}
        ;;
    clean)
        clean
        ;;
    init)
        init_environment
        ;;
    help|--help|-h)
        help
        ;;
    *)
        log_error "未知命令: $1"
        echo ""
        help
        exit 1
        ;;
esac