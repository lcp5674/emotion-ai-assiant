#!/bin/bash
#==============================================================================
# AI情感助手 - 服务健康检查脚本
#==============================================================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 输出格式: JSON 或 简洁
FORMAT="${1:-simple}"
TIMEOUT="${2:-5}"

# 健康状态
declare -A services_status
all_healthy=true

# 检查函数
check_service() {
    local name=$1
    local url=$2
    local expected_code="${3:-200}"

    if curl -sf --connect-timeout "$TIMEOUT" -o /dev/null -w "%{http_code}" "$url" 2>/dev/null | grep -q "$expected_code"; then
        services_status["$name"]="healthy"
        return 0
    else
        services_status["$name"]="unhealthy"
        all_healthy=false
        return 1
    fi
}

check_tcp() {
    local name=$1
    local host=$2
    local port=$3

    if nc -z -w "$TIMEOUT" "$host" "$port" 2>/dev/null; then
        services_status["$name"]="healthy"
        return 0
    else
        services_status["$name"]="unhealthy"
        all_healthy=false
        return 1
    fi
}

# 简洁输出
print_simple() {
    echo ""
    echo "═══════════════════════════════════════"
    echo "         服务健康检查"
    echo "═══════════════════════════════════════"

    for service in "${!services_status[@]}"; do
        status="${services_status[$service]}"
        if [ "$status" = "healthy" ]; then
            echo -e "  ${GREEN}✓${NC} $service"
        else
            echo -e "  ${RED}✗${NC} $service"
        fi
    done

    echo "═══════════════════════════════════════"

    if [ "$all_healthy" = true ]; then
        echo -e "${GREEN}所有服务运行正常${NC}"
        exit 0
    else
        echo -e "${RED}部分服务异常${NC}"
        exit 1
    fi
}

# JSON 输出
print_json() {
    echo "{"
    echo "  \"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\","
    echo "  \"overall_status\": \"$([ "$all_healthy" = true ] && echo 'healthy' || echo 'unhealthy')\","
    echo "  \"services\": {"

    local first=true
    for service in "${!services_status[@]}"; do
        if [ "$first" = true ]; then
            first=false
        else
            echo ","
        fi
        echo -n "    \"$service\": \"${services_status[$service]}\""
    done

    echo ""
    echo "  }"
    echo "}"
}

#==============================================================================
# 执行检查
#==============================================================================

# 后端 API 健康检查
check_service "backend-api" "http://localhost:8000/api/v1/health" || true

# 后端 API 详细检查 (含数据库连接)
check_service "backend-db" "http://localhost:8000/api/v1/health?check=db" || true

# 前端 Nginx
check_service "frontend-nginx" "http://localhost/" || true

# MySQL 数据库
check_tcp "mysql" "localhost" "3306" || true

# Redis
check_tcp "redis" "localhost" "6379" || true

# MinIO (如果有)
check_tcp "minio" "localhost" "9000" || true

#==============================================================================
# 输出结果
#==============================================================================

case "$FORMAT" in
    json)
        print_json
        ;;
    *)
        print_simple
        ;;
esac
