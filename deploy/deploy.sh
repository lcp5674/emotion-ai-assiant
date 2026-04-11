#!/bin/bash
#==============================================================================
# AI情感助手 - 一键部署脚本
# 适用于 macOS 和 Linux
#==============================================================================

set -e  # 遇到错误立即退出
set -u  # 使用未定义变量时报错

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
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
DEPLOY_DIR="$PROJECT_DIR/deploy"

# 配置文件路径
ENV_FILE="$PROJECT_DIR/.env.docker"
DOCKER_COMPOSE_FILE="$PROJECT_DIR/docker-compose.yml"

#==============================================================================
# 步骤 0: 前置检查
#==============================================================================
preflight_check() {
    log_info "========== 前置检查 =========="

    # 检查 Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker 未安装，请先安装 Docker Desktop"
        exit 1
    fi

    DOCKER_VERSION=$(docker --version | grep -oE '[0-9]+\.[0-9]+')
    log_success "Docker 版本: $(docker --version)"

    # 检查 Docker Compose
    if ! docker compose version &> /dev/null && ! docker-compose --version &> /dev/null; then
        log_error "Docker Compose 未安装"
        exit 1
    fi

    if docker compose version &> /dev/null; then
        COMPOSE_CMD="docker compose"
    else
        COMPOSE_CMD="docker-compose"
    fi
    log_success "Docker Compose: $(${COMPOSE_CMD} version | head -1)"

    # 检查端口占用
    PORTS=(80 443 3306 6379 8000 9000)
    for port in "${PORTS[@]}"; do
        if lsof -Pi :$port -sTCP:LISTEN -t &> /dev/null 2>&1; then
            log_warning "端口 $port 已被占用"
        fi
    done

    # 检查配置文件
    if [ ! -f "$ENV_FILE" ]; then
        if [ -f "$ENV_FILE.example" ]; then
            log_warning "未找到 .env.docker，将从 .env.docker.example 复制"
            cp "$ENV_FILE.example" "$ENV_FILE"
        else
            log_error "未找到环境配置文件"
            exit 1
        fi
    fi

    log_success "前置检查完成"
}

#==============================================================================
# 步骤 1: 环境配置生成
#==============================================================================
generate_config() {
    log_info "========== 环境配置 =========="

    # 读取或生成密钥
    if grep -q "SECRET_KEY=your-secret-key-here" "$ENV_FILE" 2>/dev/null; then
        SECRET_KEY=$(openssl rand -hex 32)
        sed -i.bak "s/SECRET_KEY=your-secret-key-here/SECRET_KEY=${SECRET_KEY}/" "$ENV_FILE"
        log_success "已生成应用密钥"
    fi

    # 验证关键环境变量
    REQUIRED_VARS=("DATABASE_URL" "REDIS_URL" "LLM_API_KEY")
    for var in "${REQUIRED_VARS[@]}"; do
        if ! grep -q "^${var}=" "$ENV_FILE" || grep -q "${var}=your-" "$ENV_FILE"; then
            log_warning "环境变量 $var 未正确配置，请在 $ENV_FILE 中设置"
        fi
    done

    log_success "环境配置验证完成"
}

#==============================================================================
# 步骤 2: 数据库迁移
#==============================================================================
run_migrations() {
    log_info "========== 数据库迁移 =========="

    # 检查数据库连接
    log_info "等待数据库就绪..."

    # 使用 docker-compose 运行迁移
    $COMPOSE_CMD run --rm backend python -m alembic upgrade head

    log_success "数据库迁移完成"
}

#==============================================================================
# 步骤 3: 服务启动
#==============================================================================
start_services() {
    log_info "========== 启动服务 =========="

    # 构建并启动服务
    $COMPOSE_CMD up -d --build

    log_success "服务启动命令已执行"
}

#==============================================================================
# 步骤 4: 健康检查
#==============================================================================
health_check() {
    log_info "========== 健康检查 =========="

    local max_attempts=30
    local attempt=1
    local backend_ok=false
    local frontend_ok=false
    local db_ok=false

    log_info "开始健康检查 (最多 $max_attempts 次)..."

    while [ $attempt -le $max_attempts ]; do
        echo -n "[$attempt/$max_attempts] "

        # 检查后端 API
        if [ "$backend_ok" = false ]; then
            if curl -sf http://localhost:8000/api/v1/health &>/dev/null; then
                log_success "后端 API: OK"
                backend_ok=true
            else
                echo -n "后端 API: 等待中... "
            fi
        else
            echo -n "后端 API: OK "
        fi

        # 检查前端
        if [ "$frontend_ok" = false ]; then
            if curl -sf http://localhost/ &>/dev/null; then
                log_success "前端: OK"
                frontend_ok=true
            else
                echo -n "前端: 等待中... "
            fi
        else
            echo -n "前端: OK "
        fi

        # 检查数据库
        if [ "$db_ok" = false ]; then
            if $COMPOSE_CMD exec -T mysql mysqladmin ping -h localhost -u root -p"${MYSQL_ROOT_PASSWORD:-emotionai2024}" &>/dev/null; then
                log_success "数据库: OK"
                db_ok=true
            else
                echo -n "数据库: 等待中... "
            fi
        else
            echo -n "数据库: OK "
        fi

        # 所有服务都健康
        if [ "$backend_ok" = true ] && [ "$frontend_ok" = true ] && [ "$db_ok" = true ]; then
            echo ""
            log_success "所有服务健康检查通过!"
            return 0
        fi

        echo "($((max_attempts - attempt))次重试后超时)"
        attempt=$((attempt + 1))
        sleep 2
    done

    log_error "健康检查超时"
    log_info "服务状态:"
    $COMPOSE_CMD ps
    return 1
}

#==============================================================================
# 步骤 5: 生成部署报告
#==============================================================================
generate_report() {
    log_info "========== 部署报告 =========="

    echo ""
    echo "┌─────────────────────────────────────────────────────────┐"
    echo "│              AI情感助手 - 部署完成报告                  │"
    echo "├─────────────────────────────────────────────────────────┤"
    echo "│  部署时间: $(date '+%Y-%m-%d %H:%M:%S')                        │"
    echo "├─────────────────────────────────────────────────────────┤"
    echo "│  服务状态                                              │"
    echo "│  ├─ 前端 (Nginx):  http://localhost                      │"
    echo "│  ├─ 后端 (FastAPI): http://localhost/api/v1/health       │"
    echo "│  ├─ API文档:       http://localhost/docs                │"
    echo "│  └─ 数据库:        localhost:3306                       │"
    echo "├─────────────────────────────────────────────────────────┤"
    echo "│  管理命令                                              │"
    echo "│  ├─ 查看日志:       ./deploy/logs.sh                    │"
    echo "│  ├─ 停止服务:       ./deploy/stop.sh                    │"
    echo "│  ├─ 重启服务:       ./deploy/restart.sh                 │"
    echo "│  └─ 更新部署:       ./deploy/deploy.sh                  │"
    echo "├─────────────────────────────────────────────────────────┤"
    echo "│  常用命令                                              │"
    echo "│  ├─ 进入后端容器:   docker exec -it emotion-ai-backend bash"
    echo "│  ├─ 查看后端日志:   docker logs -f emotion-ai-backend"
    echo "│  └─ 数据库连接:     mysql -h localhost -u root -p       │"
    echo "└─────────────────────────────────────────────────────────┘"
    echo ""

    # 服务健康状态
    echo "服务详情:"
    $COMPOSE_CMD ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"
    echo ""
}

#==============================================================================
# 主流程
#==============================================================================
main() {
    echo ""
    echo "╔════════════════════════════════════════════════════════╗"
    echo "║          AI情感助手 - 一键部署脚本 v1.0                  ║"
    echo "╚════════════════════════════════════════════════════════╝"
    echo ""

    # 显示环境信息
    log_info "项目目录: $PROJECT_DIR"
    log_info "部署目录: $DEPLOY_DIR"
    echo ""

    # 执行部署步骤
    preflight_check
    echo ""

    generate_config
    echo ""

    run_migrations
    echo ""

    start_services
    echo ""

    if health_check; then
        echo ""
        generate_report
        log_success "部署完成!"
    else
        log_error "部署过程中出现问题，请检查日志"
        exit 1
    fi
}

# 捕获 Ctrl+C
trap 'log_warning "部署被中断"; exit 130' INT

# 执行主流程
main "$@"
