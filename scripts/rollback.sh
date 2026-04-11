#!/bin/bash
# 回滚到上一个版本

set -e

VERSION=${1:-"-1"}
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

echo "🔄 Starting rollback..."

if [ "$VERSION" == "-1" ]; then
    echo "📊 Rolling back to previous migration..."
    docker-compose -f docker-compose.prod.yml exec -T backend alembic downgrade -1
elif [ "$VERSION" == "base" ]; then
    echo "📊 Rolling back to base (all migrations)..."
    docker-compose -f docker-compose.prod.yml exec -T backend alembic downgrade base
else
    echo "📊 Rolling back to version: $VERSION"
    docker-compose -f docker-compose.prod.yml exec -T backend alembic downgrade "$VERSION"
fi

echo "🔄 Restarting backend service..."
docker-compose -f docker-compose.prod.yml restart backend

echo ""
echo "=========================================="
echo "  ✅ Rollback completed!"
echo "=========================================="
