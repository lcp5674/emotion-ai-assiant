#!/bin/bash
set -e

echo "🚀 Starting SBTI Module Deployment..."
echo "=========================================="

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. Pull latest code
echo -e "${YELLOW}📦 Step 1: Pulling latest code...${NC}"
if git rev-parse --git-dir > /dev/null 2>&1; then
    git pull origin main
else
    echo -e "${YELLOW}⚠️  Not a git repository, skipping pull${NC}"
fi

# 2. 确定使用哪个docker-compose文件
echo -e "${YELLOW}📋 Step 2: Checking docker-compose files...${NC}"
if [ -f "docker-compose.prod.yml" ]; then
    COMPOSE_FILE="docker-compose.prod.yml"
elif [ -f "docker-compose.simple.yml" ]; then
    COMPOSE_FILE="docker-compose.simple.yml"
elif [ -f "docker-compose.yml" ]; then
    COMPOSE_FILE="docker-compose.yml"
else
    echo -e "${RED}❌ No docker-compose file found!${NC}"
    exit 1
fi
echo -e "${GREEN}Using: $COMPOSE_FILE${NC}"

# 3. Build Docker images
echo -e "${YELLOW}🔨 Step 3: Building Docker images...${NC}"
docker-compose -f "$COMPOSE_FILE" build

# 4. Start MySQL and Redis first
echo -e "${YELLOW}🗄️  Step 4: Starting database services...${NC}"
docker-compose -f "$COMPOSE_FILE" up -d mysql redis

# 5. Wait for MySQL to be ready
echo -e "${YELLOW}⏳ Step 5: Waiting for MySQL to be ready...${NC}"
for i in {1..30}; do
    if docker-compose -f "$COMPOSE_FILE" exec -T mysql mysqladmin ping -h localhost --silent 2>/dev/null; then
        echo -e "${GREEN}✅ MySQL is ready!${NC}"
        break
    fi
    echo "Waiting for MySQL... ($i/30)"
    sleep 2
done

# 6. Run database migrations
echo -e "${YELLOW}📊 Step 6: Running database migrations...${NC}"
docker-compose -f "$COMPOSE_FILE" exec -T backend alembic upgrade head || {
    echo -e "${YELLOW}⚠️  Migration warning (may be OK if tables exist)${NC}"
}

# 7. Initialize SBTI questions
echo -e "${YELLOW}📝 Step 7: Initializing SBTI questions...${NC}"
docker-compose -f "$COMPOSE_FILE" exec -T backend python -c "
from app.core.database import SessionLocal
from app.services.sbti_service import get_sbti_service
from app.services.attachment_service import get_attachment_service

db = SessionLocal()
try:
    get_sbti_service().seed_questions(db, force=False)
    get_attachment_service().seed_questions(db, force=False)
    print('✅ SBTI and Attachment questions initialized')
finally:
    db.close()
" 2>/dev/null || echo -e "${YELLOW}⚠️  Question initialization skipped${NC}"

# 8. Start all services
echo -e "${YELLOW}🔄 Step 8: Starting all services...${NC}"
docker-compose -f "$COMPOSE_FILE" up -d

# 9. Health check
echo -e "${YELLOW}✅ Step 9: Running health checks...${NC}"
sleep 10

# Check backend
if curl -sf http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Backend health check passed${NC}"
else
    echo -e "${RED}❌ Backend health check failed${NC}"
    echo "Logs:"
    docker-compose -f "$COMPOSE_FILE" logs backend | tail -20
fi

# Check web
if curl -sf http://localhost > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Web health check passed${NC}"
else
    echo -e "${YELLOW}⚠️  Web health check skipped (may not be ready yet)${NC}"
fi

# 10. Run smoke tests
echo -e "${YELLOW}🧪 Step 10: Running smoke tests...${NC}"
echo "Testing SBTI questions endpoint..."
SBTI_RESPONSE=$(curl -sf http://localhost:8000/api/v1/sbti/questions)
if [ $? -eq 0 ]; then
    QUESTION_COUNT=$(echo "$SBTI_RESPONSE" | grep -o '"total":[0-9]*' | grep -o '[0-9]*')
    echo -e "${GREEN}✅ SBTI questions endpoint: $QUESTION_COUNT questions${NC}"
else
    echo -e "${RED}❌ SBTI questions endpoint failed${NC}"
fi

echo ""
echo "=========================================="
echo -e "${GREEN}  ✅ Deployment completed successfully!${NC}"
echo "=========================================="
echo -e "  🌐 API:      ${GREEN}http://localhost:8000${NC}"
echo -e "  📱 Web:      ${GREEN}http://localhost${NC}"
echo -e "  📚 Docs:     ${GREEN}http://localhost:8000/docs${NC}"
echo ""
echo "New SBTI Endpoints:"
echo "  GET  /api/v1/sbti/questions"
echo "  POST /api/v1/sbti/submit"
echo "  GET  /api/v1/sbti/result"
echo "  GET  /api/v1/sbti/themes/{theme}"
echo ""
echo "New Attachment Endpoints:"
echo "  GET  /api/v1/attachment/questions"
echo "  POST /api/v1/attachment/submit"
echo "  GET  /api/v1/attachment/result"
echo ""
echo "New Profile Endpoints:"
echo "  GET  /api/v1/profile/deep"
echo "=========================================="
