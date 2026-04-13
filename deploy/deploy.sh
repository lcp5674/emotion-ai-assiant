#!/bin/bash
#==============================================================================
# AI情感助手 - 增强版一键部署脚本 v2.1
# 适用于 macOS 和 Linux
#==============================================================================

set -e  # 遇到错误立即退出
set -o pipefail  # 管道失败也退出
# 注意：移除 set -u，因为数组和间接变量引用在某些情况下会有问题

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
DEPLOY_MODE="simple"  # 默认简单模式
DATA_PATH="$PROJECT_DIR/data"

#==============================================================================
# 端口检测函数 - 简单可靠版
#==============================================================================
check_and_fix_ports() {
    log_info "========== 端口检查与修复 =========="
    
    # 确保 .env 文件存在
    if [ ! -f "$ENV_FILE" ]; then
        if [ -f "$ENV_FILE.example" ]; then
            cp "$ENV_FILE.example" "$ENV_FILE"
            log_success "已从示例文件创建环境配置文件"
        fi
    fi
    
    # 定义要检查的端口及其对应的环境变量名
    # 直接使用关联数组，避免间接引用问题
    local port_conflicts=()
    local port_changes=()
    
    # 直接检查并处理每个端口
    # MySQL 端口 3306
    local mysql_port=$(grep "^MYSQL_PORT=" "$ENV_FILE" 2>/dev/null | head -1 | cut -d'=' -f2 | tr -d ' \r\n')
    [ -z "$mysql_port" ] && mysql_port="3306"
    
    # Redis 端口 6379
    local redis_port=$(grep "^REDIS_PORT=" "$ENV_FILE" 2>/dev/null | head -1 | cut -d'=' -f2 | tr -d ' \r\n')
    [ -z "$redis_port" ] && redis_port="6379"
    
    # 后端端口 8000
    local backend_port=$(grep "^BACKEND_PORT=" "$ENV_FILE" 2>/dev/null | head -1 | cut -d'=' -f2 | tr -d ' \r\n')
    [ -z "$backend_port" ] && backend_port="8000"
    
    # MinIO 端口 9000
    local minio_port=$(grep "^MINIO_PORT=" "$ENV_FILE" 2>/dev/null | head -1 | cut -d'=' -f2 | tr -d ' \r\n')
    [ -z "$minio_port" ] && minio_port="9000"
    
    # MinIO Console 端口 9001
    local minio_console_port=$(grep "^MINIO_CONSOLE_PORT=" "$ENV_FILE" 2>/dev/null | head -1 | cut -d'=' -f2 | tr -d ' \r\n')
    [ -z "$minio_console_port" ] && minio_console_port="9001"
    
    # HTTP 端口 80
    local http_port=$(grep "^HTTP_PORT=" "$ENV_FILE" 2>/dev/null | head -1 | cut -d'=' -f2 | tr -d ' \r\n')
    [ -z "$http_port" ] && http_port="80"
    
    # HTTPS 端口 443
    local https_port=$(grep "^HTTPS_PORT=" "$ENV_FILE" 2>/dev/null | head -1 | cut -d'=' -f2 | tr -d ' \r\n')
    [ -z "$https_port" ] && https_port="443"
    
    # 检查并修复函数 - 使用 lsof 或 /proc/net/tcp 检测
    fix_port() {
        local var_name=$1
        local actual_port=$2
        local new_port=""
        local port_in_use=false
        
        # 尝试使用 lsof 检测
        if command -v lsof &>/dev/null; then
            if lsof -i:$actual_port &>/dev/null 2>&1; then
                port_in_use=true
            fi
        elif [ -f /proc/net/tcp ]; then
            # Linux 使用 /proc/net/tcp 检测
            if grep -q ":$(printf '%x' $actual_port) " /proc/net/tcp /proc/net/tcp6 2>/dev/null; then
                port_in_use=true
            fi
        fi
        
        if [ "$port_in_use" = true ]; then
            new_port=$((actual_port + 10000))
            local attempts=0
            local new_port_in_use=true
            
            while [ "$new_port_in_use" = true ] && [ $attempts -lt 100 ]; do
                if command -v lsof &>/dev/null; then
                    if lsof -i:$new_port &>/dev/null 2>&1; then
                        new_port=$((new_port + 1))
                        [ $new_port -gt 65535 ] && new_port=10000
                        attempts=$((attempts + 1))
                    else
                        new_port_in_use=false
                    fi
                elif [ -f /proc/net/tcp ]; then
                    if grep -q ":$(printf '%x' $new_port) " /proc/net/tcp /proc/net/tcp6 2>/dev/null; then
                        new_port=$((new_port + 1))
                        [ $new_port -gt 65535 ] && new_port=10000
                        attempts=$((attempts + 1))
                    else
                        new_port_in_use=false
                    fi
                else
                    new_port=$((new_port + 1))
                    attempts=$((attempts + 1))
                fi
            done
            
            log_warning "端口 ${actual_port} 被占用，自动更换为 ${new_port}"
            port_conflicts+=("${actual_port}")
            port_changes+=("${actual_port}->${new_port}")
            
            # 更新 .env 文件
            if grep -q "^${var_name}=" "$ENV_FILE" 2>/dev/null; then
                sed -i "s|^${var_name}=.*|${var_name}=${new_port}|" "$ENV_FILE"
            else
                echo "${var_name}=${new_port}" >> "$ENV_FILE"
            fi
        fi
    }
    
    # 执行检查
    fix_port "MYSQL_PORT" "$mysql_port"
    fix_port "REDIS_PORT" "$redis_port"
    fix_port "BACKEND_PORT" "$backend_port"
    fix_port "MINIO_PORT" "$minio_port"
    fix_port "MINIO_CONSOLE_PORT" "$minio_console_port"
    fix_port "HTTP_PORT" "$http_port"
    fix_port "HTTPS_PORT" "$https_port"
    
    if [ ${#port_conflicts[@]} -eq 0 ]; then
        log_success "所有端口可用，无冲突"
    else
        log_success "已自动修复 ${#port_conflicts[@]} 个端口冲突：${port_changes[*]}"
    fi
    
    # 同步 .env 到项目根目录
    cp -f "$ENV_FILE" "$PROJECT_DIR/.env" 2>/dev/null || true
}

#==============================================================================
# 步骤 0: 前置检查
#==============================================================================
preflight_check() {
    log_info "========== 前置检查 =========="

    # 检查 Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker 未安装，请先安装 Docker"
        exit 1
    fi

    log_success "Docker 版本: $(docker --version)"

    # 检查 Docker Compose
    if docker compose version &> /dev/null 2>&1; then
        COMPOSE_CMD="docker compose"
    elif command -v docker-compose &> /dev/null; then
        COMPOSE_CMD="docker-compose"
    else
        log_error "Docker Compose 未安装"
        exit 1
    fi
    log_success "Docker Compose: $(${COMPOSE_CMD} version | head -1)"

    # 检查 Docker daemon
    if ! docker info &> /dev/null; then
        log_error "Docker daemon 未运行，请启动 Docker"
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

    # 确保 .env 文件存在
    if [ ! -f "$ENV_FILE" ]; then
        if [ -f "$ENV_FILE.example" ]; then
            cp "$ENV_FILE.example" "$ENV_FILE"
        fi
    fi

    # 生成随机密码的函数
    generate_password() {
        if command -v openssl &>/dev/null; then
            openssl rand -hex 16 2>/dev/null
        else
            head -c 32 /dev/urandom | xxd -p | head -c 32
        fi
    }

    # 更新或追加环境变量的函数
    update_env_var() {
        local key="$1"
        local value="$2"
        if grep -q "^${key}=" "$ENV_FILE" 2>/dev/null; then
            if [[ "$OSTYPE" == "darwin"* ]]; then
                sed -i '' "s/^${key}=.*/${key}=${value}/" "$ENV_FILE"
            else
                sed -i "s|^${key}=.*|${key}=${value}|" "$ENV_FILE"
            fi
        else
            echo "${key}=${value}" >> "$ENV_FILE"
        fi
    }

    # 生成 SECRET_KEY
    local current_secret=$(grep "^SECRET_KEY=" "$ENV_FILE" 2>/dev/null | cut -d'=' -f2 | tr -d ' \r\n')
    if [ -z "$current_secret" ] || [ "$current_secret" = "your-secret-key-here" ] || [ "$current_secret" = "change-me-in-production" ]; then
        SECRET_KEY=$(generate_password)
        update_env_var "SECRET_KEY" "$SECRET_KEY"
        log_success "已生成应用密钥"
    fi

    # 生成 MYSQL_ROOT_PASSWORD
    local current_mysql_root=$(grep "^MYSQL_ROOT_PASSWORD=" "$ENV_FILE" 2>/dev/null | cut -d'=' -f2 | tr -d ' \r\n')
    if [ -z "$current_mysql_root" ]; then
        MYSQL_ROOT_PASSWORD=$(generate_password)
        update_env_var "MYSQL_ROOT_PASSWORD" "$MYSQL_ROOT_PASSWORD"
        log_success "已生成 MySQL Root 密码"
    fi

    # 生成 MYSQL_PASSWORD
    local current_mysql=$(grep "^MYSQL_PASSWORD=" "$ENV_FILE" 2>/dev/null | cut -d'=' -f2 | tr -d ' \r\n')
    if [ -z "$current_mysql" ] || [ "$current_mysql" = "your_password" ] || [ "$current_mysql" = "emotion_ai_password" ]; then
        MYSQL_PASSWORD=$(generate_password)
        update_env_var "MYSQL_PASSWORD" "$MYSQL_PASSWORD"
        log_success "已生成 MySQL 应用密码"
    fi

    # 生成 REDIS_PASSWORD
    local current_redis=$(grep "^REDIS_PASSWORD=" "$ENV_FILE" 2>/dev/null | cut -d'=' -f2 | tr -d ' \r\n')
    if [ -z "$current_redis" ] || [ "$current_redis" = "redis" ] || [ "$current_redis" = "redis_password" ]; then
        REDIS_PASSWORD=$(generate_password)
        update_env_var "REDIS_PASSWORD" "$REDIS_PASSWORD"
        log_success "已生成 Redis 密码"
    fi

    # 生成 MINIO_ROOT_PASSWORD
    local current_minio=$(grep "^MINIO_ROOT_PASSWORD=" "$ENV_FILE" 2>/dev/null | cut -d'=' -f2 | tr -d ' \r\n')
    if [ -z "$current_minio" ] || [ "$current_minio" = "minioadmin" ] || [ "$current_minio" = "minio_password" ]; then
        MINIO_ROOT_PASSWORD=$(generate_password)
        update_env_var "MINIO_ROOT_PASSWORD" "$MINIO_ROOT_PASSWORD"
        log_success "已生成 MinIO 密码"
    fi

    # 确保源文件也有这些变量
    cp -f "$ENV_FILE" "$PROJECT_DIR/.env" 2>/dev/null || true

    log_success "环境配置完成"
}

#==============================================================================
# 步骤 2: 创建数据目录
#==============================================================================
create_data_dirs() {
    log_info "========== 创建数据目录 =========="

    mkdir -p "$DATA_PATH"/{mysql,redis,minio,uploads,logs/nginx}
    chmod -R 755 "$DATA_PATH" 2>/dev/null || true

    log_success "数据目录已创建: $DATA_PATH"
}

#==============================================================================
# 步骤 3: 构建前端
#==============================================================================
build_frontend() {
    log_info "========== 构建前端 =========="

    local frontend_dir="$PROJECT_DIR/frontend/web"
    
    if [ ! -d "$frontend_dir" ]; then
        log_warning "前端目录不存在，跳过前端构建"
        return 0
    fi
    
    # 检查是否需要构建
    if [ -f "$frontend_dir/dist/index.html" ] && [ "$1" != "--force-rebuild" ]; then
        log_success "前端已构建，跳过构建步骤"
        log_info "如需重新构建，请删除 frontend/web/dist 目录后重新部署"
        return 0
    fi
    
    # 检查 node_modules
    if [ ! -d "$frontend_dir/node_modules" ]; then
        log_info "安装前端依赖..."
        cd "$frontend_dir"
        if command -v yarn &>/dev/null; then
            yarn install
        elif command -v npm &>/dev/null; then
            npm install
        else
            log_error "未找到 yarn 或 npm，无法安装前端依赖"
            return 1
        fi
        cd - > /dev/null
    fi
    
    # 构建前端
    log_info "构建前端..."
    cd "$frontend_dir"
    if [ -f "yarn.lock" ]; then
        yarn build
    else
        npm run build
    fi
    
    if [ $? -eq 0 ]; then
        log_success "前端构建完成"
    else
        log_warning "前端构建失败，请检查前端代码"
    fi
    cd - > /dev/null
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
    local required_vars="SECRET_KEY MYSQL_ROOT_PASSWORD MYSQL_PASSWORD REDIS_PASSWORD"
    for var in $required_vars; do
        local value=$(grep "^${var}=" "$ENV_FILE" 2>/dev/null | head -1 | cut -d'=' -f2 | tr -d ' \r\n')
        if [ -z "$value" ]; then
            log_error "必需变量 ${var} 未设置或为空"
            log_info "请删除 .env.docker 后重新运行"
            exit 1
        fi
    done

    # 同步到项目根目录的 .env
    cp -f "$ENV_FILE" "$PROJECT_DIR/.env"

    log_success "环境变量验证完成"

    # 启动所有服务
    log_info "构建并启动所有服务..."
    $COMPOSE_CMD -f "$DOCKER_COMPOSE_FILE" up -d --build

    log_success "服务启动完成"
}

#==============================================================================
# 步骤 4: 健康检查
#==============================================================================
health_check() {
    log_info "========== 健康检查 =========="

    # 从 .env 获取实际端口
    local backend_port=$(grep "^BACKEND_PORT=" "$ENV_FILE" 2>/dev/null | cut -d'=' -f2 | tr -d ' \r\n')
    [ -z "$backend_port" ] && backend_port="8000"
    
    local frontend_port=$(grep "^HTTP_PORT=" "$ENV_FILE" 2>/dev/null | cut -d'=' -f2 | tr -d ' \r\n')
    [ -z "$frontend_port" ] && frontend_port="80"

    local max_attempts=60
    local attempt=1

    log_info "开始健康检查 (最多 $max_attempts 次)..."

    while [ $attempt -le $max_attempts ]; do
        echo -n "[$attempt/$max_attempts] "
        
        local all_ok=true

        # 检查后端 API
        if curl -sf --connect-timeout 3 "http://localhost:${backend_port}/health" &>/dev/null || \
           curl -sf --connect-timeout 3 "http://localhost:${backend_port}/api/v1/health" &>/dev/null; then
            echo -n "后端:OK "
        else
            echo -n "后端:等待中 "
            all_ok=false
        fi

        # 检查前端
        if curl -sf --connect-timeout 3 "http://localhost:${frontend_port}/" &>/dev/null; then
            echo -n "前端:OK "
        else
            echo -n "前端:等待中 "
            all_ok=false
        fi

        echo ""

        if [ "$all_ok" = true ]; then
            log_success "所有服务健康检查通过!"
            return 0
        fi

        attempt=$((attempt + 1))
        sleep 3
    done

    log_error "健康检查超时"
    log_info "服务状态:"
    $COMPOSE_CMD -f "$DOCKER_COMPOSE_FILE" ps
    return 1
}

#==============================================================================
# 步骤 5: 生成部署报告
#==============================================================================
generate_report() {
    log_info "========== 部署报告 =========="

    # 从 .env 获取端口
    local backend_port=$(grep "^BACKEND_PORT=" "$ENV_FILE" 2>/dev/null | cut -d'=' -f2 | tr -d ' \r\n')
    [ -z "$backend_port" ] && backend_port="8000"
    
    local frontend_port=$(grep "^HTTP_PORT=" "$ENV_FILE" 2>/dev/null | cut -d'=' -f2 | tr -d ' \r\n')
    [ -z "$frontend_port" ] && frontend_port="80"

    echo ""
    echo "┌─────────────────────────────────────────────────────────────────┐"
    echo "│                  AI情感助手 - 部署完成报告                      │"
    echo "├─────────────────────────────────────────────────────────────────┤"
    echo "│  部署时间: $(date '+%Y-%m-%d %H:%M:%S')                              │"
    echo "│  部署模式: $DEPLOY_MODE                                           │"
    echo "├─────────────────────────────────────────────────────────────────┤"
    echo "│  服务状态                                                          │"
    echo "│  ├─ 前端 (Nginx):    http://localhost:${frontend_port}                     │"
    echo "│  ├─ 后端 (FastAPI):  http://localhost:${backend_port}                     │"
    echo "│  ├─ API文档:         http://localhost:${backend_port}/docs                  │"
    echo "│  └─ 数据库:          localhost:3306                                │"
    echo "├─────────────────────────────────────────────────────────────────┤"
    echo "│  管理命令                                                          │"
    echo "│  ├─ 查看日志:       docker compose -f $DOCKER_COMPOSE_FILE logs       │"
    echo "│  ├─ 停止服务:       docker compose -f $DOCKER_COMPOSE_FILE down      │"
    echo "│  └─ 重启服务:       docker compose -f $DOCKER_COMPOSE_FILE restart    │"
    echo "├─────────────────────────────────────────────────────────────────┤"
    echo "│  容器命令                                                          │"
    echo "│  ├─ 进入后端:        docker exec -it emotion-ai-backend bash         │"
    echo "│  ├─ 查看后端日志:   docker logs -f emotion-ai-backend              │"
    echo "│  └─ 数据库连接:      docker exec -it emotion-ai-mysql mysql -u root -p  │"
    echo "└─────────────────────────────────────────────────────────────────┘"
    echo ""

    # 服务健康状态
    echo "服务详情:"
    $COMPOSE_CMD -f "$DOCKER_COMPOSE_FILE" ps
    echo ""
}

#==============================================================================
# 主流程
#==============================================================================
main() {
    echo ""
    echo "╔══════════════════════════════════════════════════════════════════╗"
    echo "║              AI情感助手 - 一键部署脚本 v2.2                       ║"
    echo "╚══════════════════════════════════════════════════════════════════╝"
    echo ""

    # 显示环境信息
    log_info "项目目录: $PROJECT_DIR"
    log_info "部署目录: $DEPLOY_DIR"
    log_info "数据目录: $DATA_PATH"
    echo ""

    # 解析部署模式
    if [ $# -gt 0 ]; then
        case "$1" in
            -m|--mode)
                DEPLOY_MODE="${2:-simple}"
                ;;
            -s|--simple)
                DEPLOY_MODE="simple"
                ;;
            -p|--prod)
                DEPLOY_MODE="prod"
                ;;
            -ms|--microservices)
                DEPLOY_MODE="microservices"
                ;;
            *)
                DEPLOY_MODE="simple"
                ;;
        esac
    fi

    # 执行部署步骤
    log_step "步骤 1/6: 前置检查"
    preflight_check
    echo ""

    log_step "步骤 2/6: 端口检查与修复"
    check_and_fix_ports
    echo ""

    log_step "步骤 3/6: 环境配置"
    generate_config
    echo ""

    log_step "步骤 4/6: 构建前端"
    build_frontend
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
        echo "  - 查看日志: docker compose -f $DOCKER_COMPOSE_FILE logs"
        echo "  - 进入后端: docker exec -it emotion-ai-backend bash"
        echo "  - 停止服务: docker compose -f $DOCKER_COMPOSE_FILE down"
    else
        log_error "部署过程中出现问题，请检查日志"
        log_info "调试命令:"
        echo "  - docker compose -f $DOCKER_COMPOSE_FILE ps"
        echo "  - docker compose -f $DOCKER_COMPOSE_FILE logs"
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
    echo "  -m, --mode MODE         部署模式 (simple/prod/microservices)"
    echo "  -s, --simple            使用简化部署模式"
    echo "  -p, --prod              使用生产部署模式"
    echo "  --ms, --microservices   使用微服务部署模式"
    echo "  -h, --help              显示帮助信息"
    echo ""
    echo "示例:"
    echo "  $0                      # 默认简单部署"
    echo "  $0 -p                   # 生产模式部署"
    exit 0
}

# 根据参数执行
if [ "$#" -gt 0 ] && [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
    show_help
else
    main "$@"
fi
