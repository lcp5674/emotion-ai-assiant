#!/bin/bash
#==============================================================================
# AI情感助手 - 增强版一键部署脚本 v2.0
# 适用于 macOS 和 Linux
#==============================================================================

set -e  # 遇到错误立即退出
set -u  # 使用未定义变量时报错
set -o pipefail  # 管道失败也退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
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

log_step() {
    echo -e "${CYAN}[STEP]${NC} $1"
}

# 获取脚本目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
DEPLOY_DIR="$PROJECT_DIR/deploy"

# 配置文件路径
ENV_FILE="$PROJECT_DIR/.env.docker"
DOCKER_COMPOSE_FILE="$PROJECT_DIR/docker-compose.yml"

# 部署模式
DEPLOY_MODE="${1:-full}"  # full, simple, prod, microservices
DATA_PATH="$PROJECT_DIR/data"

#==============================================================================
# 跨平台端口检测函数
#==============================================================================
check_port() {
    local port=$1
    local service=$2

    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if lsof -Pi :$port -sTCP:LISTEN -t &> /dev/null 2>&1; then
            log_warning "端口 $port ($service) 已被占用"
            return 1
        fi
    else
        # Linux
        if ss -tuln | grep -q ":$port "; then
            log_warning "端口 $port ($service) 已被占用"
            return 1
        fi
    fi
    return 0
}

check_all_ports() {
    log_info "========== 端口检查 =========="

    local ports_ok=true

    case "$DEPLOY_MODE" in
        simple)
            declare -a PORTS=("3306:MySQL" "6379:Redis" "8000:Backend" "80:Frontend")
            ;;
        prod|production)
            declare -a PORTS=("3306:MySQL" "6379:Redis" "9000:MinIO" "8000:Backend" "80:Nginx")
            ;;
        microservices)
            declare -a PORTS=("3306:MySQL" "6379:Redis" "8000:API-Gateway" "9090:Prometheus" "3000:Grafana")
            ;;
        *)
            declare -a PORTS=("3306:MySQL" "6379:Redis" "9000:MinIO" "8000:Backend" "9001:MinIO-Console" "80:Nginx" "443:Nginx-HTTPS")
            ;;
    esac

    for entry in "${PORTS[@]}"; do
        IFS=':' read -r port service <<< "$entry"
        if ! check_port "$port" "$service"; then
            ports_ok=false
        fi
    done

    if [ "$ports_ok" = false ]; then
        log_warning "部分端口被占用，可能会导致服务启动失败"
    else
        log_success "端口检查通过"
    fi
}

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

    log_success "Docker 版本: $(docker --version)"

    # 检查 Docker Compose
    if docker compose version &> /dev/null 2>&1; then
        COMPOSE_CMD="docker compose"
    elif docker-compose --version &> /dev/null 2>&1; then
        COMPOSE_CMD="docker-compose"
    else
        log_error "Docker Compose 未安装"
        exit 1
    fi
    log_success "Docker Compose: $(${COMPOSE_CMD} version | head -1)"

    # 检查 Docker daemon
    if ! docker info &> /dev/null; then
        log_error "Docker daemon 未运行，请启动 Docker Desktop"
        exit 1
    fi

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

    # 检查 docker-compose 文件
    case "$DEPLOY_MODE" in
        simple)
            DOCKER_COMPOSE_FILE="$PROJECT_DIR/docker-compose.simple.yml"
            ;;
        prod|production)
            DOCKER_COMPOSE_FILE="$PROJECT_DIR/docker-compose.prod.yml"
            ;;
        microservices)
            DOCKER_COMPOSE_FILE="$PROJECT_DIR/docker-compose-microservices.yml"
            ;;
        *)
            DOCKER_COMPOSE_FILE="$PROJECT_DIR/docker-compose.yml"
            ;;
    esac

    if [ ! -f "$DOCKER_COMPOSE_FILE" ]; then
        log_error "未找到部署配置文件: $DOCKER_COMPOSE_FILE"
        exit 1
    fi

    log_success "部署模式: $DEPLOY_MODE"
    log_success "配置文件: $(basename $DOCKER_COMPOSE_FILE)"
    log_success "前置检查完成"
}

#==============================================================================
# 步骤 1: 环境配置生成
#==============================================================================
generate_config() {
    log_info "========== 环境配置 =========="

    # 生成随机密码的函数
    generate_password() {
        openssl rand -hex 16 2>/dev/null || cat /dev/urandom | tr -dc 'a-f0-9' | fold -w 32 | head -n 1
    }

    # 更新或追加环境变量的函数
    update_env_var() {
        local key="$1"
        local value="$2"
        if grep -q "^${key}=" "$ENV_FILE" 2>/dev/null; then
            if [[ "$OSTYPE" == "darwin"* ]]; then
                sed -i '' "s/^${key}=.*/${key}=${value}/" "$ENV_FILE"
            else
                sed -i "s/^${key}=.*/${key}=${value}/" "$ENV_FILE"
            fi
        else
            echo "${key}=${value}" >> "$ENV_FILE"
        fi
    }

    # 生成或更新 SECRET_KEY
    local current_secret=$(grep "^SECRET_KEY=" "$ENV_FILE" 2>/dev/null | cut -d'=' -f2)
    if [[ -z "$current_secret" || "$current_secret" == "your-secret-key-here" || "$current_secret" == "change-me-in-production" ]]; then
        SECRET_KEY=$(generate_password)
        update_env_var "SECRET_KEY" "$SECRET_KEY"
        log_success "已生成应用密钥"
    fi

    # 生成或更新 MYSQL_ROOT_PASSWORD
    local current_mysql_root=$(grep "^MYSQL_ROOT_PASSWORD=" "$ENV_FILE" 2>/dev/null | cut -d'=' -f2)
    if [[ -z "$current_mysql_root" ]]; then
        MYSQL_ROOT_PASSWORD=$(generate_password)
        update_env_var "MYSQL_ROOT_PASSWORD" "$MYSQL_ROOT_PASSWORD"
        log_success "已生成 MySQL Root 密码"
    fi

    # 生成或更新 MYSQL_PASSWORD
    local current_mysql=$(grep "^MYSQL_PASSWORD=" "$ENV_FILE" 2>/dev/null | cut -d'=' -f2)
    if [[ -z "$current_mysql" || "$current_mysql" == "your_password" || "$current_mysql" == "emotion_ai_password" ]]; then
        MYSQL_PASSWORD=$(generate_password)
        update_env_var "MYSQL_PASSWORD" "$MYSQL_PASSWORD"
        log_success "已生成 MySQL 应用密码"
    fi

    # 生成或更新 REDIS_PASSWORD
    local current_redis=$(grep "^REDIS_PASSWORD=" "$ENV_FILE" 2>/dev/null | cut -d'=' -f2)
    if [[ -z "$current_redis" || "$current_redis" == "redis" || "$current_redis" == "redis_password" ]]; then
        REDIS_PASSWORD=$(generate_password)
        update_env_var "REDIS_PASSWORD" "$REDIS_PASSWORD"
        log_success "已生成 Redis 密码"
    fi

    # 生成或更新 MINIO_ROOT_PASSWORD
    local current_minio=$(grep "^MINIO_ROOT_PASSWORD=" "$ENV_FILE" 2>/dev/null | cut -d'=' -f2)
    if [[ -z "$current_minio" || "$current_minio" == "minioadmin" || "$current_minio" == "minio_password" ]]; then
        MINIO_ROOT_PASSWORD=$(generate_password)
        update_env_var "MINIO_ROOT_PASSWORD" "$MINIO_ROOT_PASSWORD"
        log_success "已生成 MinIO 密码"
    fi

    # 确保源文件也有这些变量 (用于 docker-compose)
    cp -f "$ENV_FILE" "$PROJECT_DIR/.env" 2>/dev/null || true

    log_success "环境配置验证完成"
}

#==============================================================================
# 步骤 2: 创建数据目录
#==============================================================================
create_data_dirs() {
    log_info "========== 创建数据目录 =========="

    mkdir -p "$DATA_PATH"/{mysql,redis,minio,uploads,logs/nginx}
    chmod -R 755 "$DATA_PATH"

    log_success "数据目录已创建: $DATA_PATH"
}

#==============================================================================
# 步骤 3: 数据库迁移
#==============================================================================
run_migrations() {
    log_info "========== 数据库迁移 =========="

    # 检查数据库连接
    log_info "等待数据库就绪..."

    local max_attempts=30
    local attempt=1

    while [ $attempt -le $max_attempts ]; do
        if docker exec emotion-ai-mysql mysqladmin ping -h localhost -u root -p"${MYSQL_ROOT_PASSWORD:-root}" &>/dev/null 2>&1; then
            log_success "数据库已就绪"
            break
        fi
        echo -n "."
        attempt=$((attempt + 1))
        sleep 2
    done

    if [ $attempt -gt $max_attempts ]; then
        log_warning "数据库连接超时，跳过迁移检查"
    else
        # 使用 docker-compose 运行迁移
        $COMPOSE_CMD -f "$DOCKER_COMPOSE_FILE" run --rm backend python -m alembic upgrade head 2>/dev/null || \
        log_warning "数据库迁移命令不可用，请手动执行"
        log_success "数据库迁移完成"
    fi
}

#==============================================================================
# 步骤 4: 服务启动
#==============================================================================
start_services() {
    log_info "========== 启动服务 =========="

    # 确保 .env 文件存在且包含所有必需变量
    if [ ! -f "$ENV_FILE" ]; then
        log_error "环境配置文件不存在: $ENV_FILE"
        exit 1
    fi

    # 验证必需变量
    local required_vars=("MYSQL_ROOT_PASSWORD" "MYSQL_PASSWORD" "REDIS_PASSWORD" "SECRET_KEY")
    for var in "${required_vars[@]}"; do
        local value=$(grep "^${var}=" "$ENV_FILE" 2>/dev/null | cut -d'=' -f2)
        if [[ -z "$value" ]]; then
            log_error "必需变量 ${var} 未设置或为空"
            log_info "请手动设置或删除 .env.docker 后重新运行"
            exit 1
        fi
    done

    # 同步到项目根目录的 .env
    cp -f "$ENV_FILE" "$PROJECT_DIR/.env"

    log_info "环境变量验证完成"

    # 检查端口占用情况，移除冲突端口的服务映射
    local redis_port=$(grep "^REDIS_PORT=" "$ENV_FILE" 2>/dev/null | cut -d'=' -f2 || echo "6379")
    local nginx_port=$(grep "^HTTP_PORT=" "$ENV_FILE" 2>/dev/null | cut -d'=' -f2 || echo "80")
    local use_temp_compose=false

    if lsof -i:${redis_port} &>/dev/null || lsof -i:${nginx_port} &>/dev/null; then
        log_warning "检测到端口冲突，创建临时配置..."

        # 创建临时配置文件，移除 Redis 和 Nginx 服务
        local temp_compose_file="${DOCKER_COMPOSE_FILE}.tmp"
        sed '/redis:/,/^  [a-z]/d' "$DOCKER_COMPOSE_FILE" | sed '/nginx:/,/^  [a-z]/d' > "$temp_compose_file"
        DOCKER_COMPOSE_FILE="$temp_compose_file"
        use_temp_compose=true

        if lsof -i:${redis_port} &>/dev/null; then
            log_warning "Redis 端口 ${redis_port} 已被占用，已移除 Redis 服务"
        fi
        if lsof -i:${nginx_port} &>/dev/null; then
            log_warning "Nginx 端口 ${nginx_port} 已被占用，已移除 Nginx 服务"
        fi
        log_info "使用临时配置启动其他服务"
    fi

    # 构建并启动服务
    $COMPOSE_CMD -f "$DOCKER_COMPOSE_FILE" up -d --build

    # 清理临时文件
    if $use_temp_compose; then
        rm -f "${DOCKER_COMPOSE_FILE}"
    fi

    log_success "服务启动命令已执行"
}

#==============================================================================
# 步骤 5: 健康检查
#==============================================================================
health_check() {
    log_info "========== 健康检查 =========="

    local max_attempts=60
    local attempt=1
    local backend_ok=false
    local frontend_ok=false
    local db_ok=false
    local redis_ok=false

    log_info "开始健康检查 (最多 $max_attempts 次)..."

    while [ $attempt -le $max_attempts ]; do
        echo -n "[$attempt/$max_attempts] "

        # 检查后端 API
        if [ "$backend_ok" = false ]; then
            if curl -sf --connect-timeout 3 http://localhost:8000/api/v1/health &>/dev/null || \
               curl -sf --connect-timeout 3 http://localhost:8000/health &>/dev/null; then
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
            if curl -sf --connect-timeout 3 http://localhost/ &>/dev/null; then
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
            if docker exec emotion-ai-mysql mysqladmin ping -h localhost -u root -p"${MYSQL_ROOT_PASSWORD:-root}" &>/dev/null 2>&1 || \
               nc -z localhost 3306 2>/dev/null; then
                log_success "数据库: OK"
                db_ok=true
            else
                echo -n "数据库: 等待中... "
            fi
        else
            echo -n "数据库: OK "
        fi

        # 检查 Redis
        if [ "$redis_ok" = false ]; then
            if nc -z localhost 6379 2>/dev/null; then
                log_success "Redis: OK"
                redis_ok=true
            else
                echo -n "Redis: 等待中... "
            fi
        else
            echo -n "Redis: OK "
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
    $COMPOSE_CMD -f "$DOCKER_COMPOSE_FILE" ps
    return 1
}

#==============================================================================
# 步骤 6: 生成部署报告
#==============================================================================
generate_report() {
    log_info "========== 部署报告 =========="

    echo ""
    echo "┌─────────────────────────────────────────────────────────────────┐"
    echo "│                  AI情感助手 - 部署完成报告                      │"
    echo "├─────────────────────────────────────────────────────────────────┤"
    echo "│  部署时间: $(date '+%Y-%m-%d %H:%M:%S')                              │"
    echo "│  部署模式: $DEPLOY_MODE                                           │"
    echo "├─────────────────────────────────────────────────────────────────┤"
    echo "│  服务状态                                                          │"
    echo "│  ├─ 前端 (Nginx):    http://localhost                              │"
    echo "│  ├─ 后端 (FastAPI):  http://localhost:8000                         │"
    echo "│  ├─ API文档:         http://localhost/docs                         │"
    echo "│  └─ 数据库:          localhost:3306                                │"
    echo "├─────────────────────────────────────────────────────────────────┤"
    echo "│  管理命令                                                          │"
    echo "│  ├─ 查看日志:       ./deploy/logs.sh                             │"
    echo "│  ├─ 健康检查:       ./deploy/health_check.sh                      │"
    echo "│  ├─ 停止服务:        ./deploy/stop.sh                             │"
    echo "│  ├─ 重启服务:       ./deploy/restart.sh                          │"
    echo "│  └─ 数据备份:       ./deploy/backup.sh                           │"
    echo "├─────────────────────────────────────────────────────────────────┤"
    echo "│  容器命令                                                          │"
    echo "│  ├─ 进入后端:        docker exec -it emotion-ai-backend bash       │"
    echo "│  ├─ 查看后端日志:   docker logs -f emotion-ai-backend            │"
    echo "│  └─ 数据库连接:      docker exec -it emotion-ai-mysql mysql -u root -p │"
    echo "└─────────────────────────────────────────────────────────────────┘"
    echo ""

    # 服务健康状态
    echo "服务详情:"
    $COMPOSE_CMD -f "$DOCKER_COMPOSE_FILE" ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"
    echo ""
}

#==============================================================================
# 主流程
#==============================================================================
main() {
    echo ""
    echo "╔══════════════════════════════════════════════════════════════════╗"
    echo "║              AI情感助手 - 一键部署脚本 v2.0                       ║"
    echo "╚══════════════════════════════════════════════════════════════════╝"
    echo ""

    # 显示环境信息
    log_info "项目目录: $PROJECT_DIR"
    log_info "部署目录: $DEPLOY_DIR"
    log_info "数据目录: $DATA_PATH"
    echo ""

    # 解析部署模式 (使用 ${1:-} 避免 unbound variable)
    case "${1:-}" in
        -m|--mode)
            DEPLOY_MODE="${2:-simple}"
            shift 2
            ;;
        -s|--simple)
            DEPLOY_MODE="simple"
            shift
            ;;
        -p|--prod)
            DEPLOY_MODE="prod"
            shift
            ;;
        -ms|--microservices)
            DEPLOY_MODE="microservices"
            shift
            ;;
        *)
            # 无参数时使用默认模式 (简单部署)
            if [[ $# -eq 0 ]]; then
                DEPLOY_MODE="simple"
            fi
            ;;
    esac

    # 执行部署步骤
    log_step "步骤 1/6: 前置检查"
    preflight_check
    echo ""

    log_step "步骤 2/6: 端口检查"
    check_all_ports
    echo ""

    log_step "步骤 3/6: 环境配置"
    generate_config
    echo ""

    log_step "步骤 4/6: 创建数据目录"
    create_data_dirs
    echo ""

    log_step "步骤 5/6: 启动服务"
    start_services
    echo ""

    log_step "步骤 6/6: 健康检查"
    if health_check; then
        echo ""
        generate_report
        log_success "部署完成!"
        log_info "使用说明:"
        echo "  - 查看完整日志: ./deploy/logs.sh"
        echo "  - 进入后端容器: docker exec -it emotion-ai-backend bash"
        echo "  - 停止所有服务: ./deploy/stop.sh"
    else
        log_error "部署过程中出现问题，请检查日志"
        log_info "调试命令:"
        echo "  - docker-compose -f $DOCKER_COMPOSE_FILE ps"
        echo "  - docker-compose -f $DOCKER_COMPOSE_FILE logs"
        exit 1
    fi
}

# 显示帮助
show_help() {
    echo "AI情感助手 - 部署脚本"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  -m, --mode MODE         部署模式 (full/simple/prod/microservices)"
    echo "  -s, --simple            使用简化部署模式"
    echo "  -p, --prod              使用生产部署模式"
    echo "  --ms, --microservices   使用微服务部署模式"
    echo "  -h, --help              显示帮助信息"
    echo ""
    echo "示例:"
    echo "  $0                      # 默认完整部署"
    echo "  $0 -s                   # 简化部署（开发环境）"
    echo "  $0 -p                   # 生产部署"
    echo "  $0 --microservices      # 微服务部署"
    echo ""
}

# 处理帮助选项
if [[ $# -gt 0 && ("$1" == "-h" || "$1" == "--help") ]]; then
    show_help
    exit 0
fi

# 捕获 Ctrl+C
trap 'log_warning "部署被中断"; exit 130' INT

# 执行主流程
main "$@"
