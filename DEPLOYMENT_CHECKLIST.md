# SBTI模块部署检查清单

## 部署前检查

### 1. 数据库迁移状态
- [ ] 检查迁移文件存在: `backend/alembic/versions/2026_04_11_001_add_personality_models.py`
- [ ] 确认迁移链完整: `alembic history`
- [ ] 记录当前迁移版本: `alembic current`

### 2. 环境变量检查
- [ ] `.env.docker` 文件存在
- [ ] MySQL 配置正确:
  - [ ] `MYSQL_HOST=mysql`
  - [ ] `MYSQL_DATABASE=emotion_ai`
  - [ ] `MYSQL_USER` 和 `MYSQL_PASSWORD` 已设置
- [ ] Redis 配置正确:
  - [ ] `REDIS_HOST=redis`
  - [ ] `REDIS_PASSWORD` 已设置
- [ ] LLM 配置:
  - [ ] `LLM_PROVIDER` 已设置 (mock/openai/deepseek)
  - [ ] `LLM_API_KEY` 已设置

### 3. 代码检查
- [ ] SBTI 模型已创建: `backend/app/models/personality.py`
- [ ] SBTI API 路由已创建
- [ ] 依恋风格模型和API已创建
- [ ] 深度画像API已创建

### 4. Docker 镜像检查
- [ ] 后端镜像可构建: `docker-compose build backend`
- [ ] 前端镜像可构建: `docker-compose build web`
- [ ] 端口未被占用: `lsof -i :8000`, `lsof -i :3306`, `lsof -i :6379`

## 部署执行

### 步骤1: 拉取最新代码
```bash
git pull origin main
```

### 步骤2: 构建镜像
```bash
# 生产环境
docker-compose -f docker-compose.prod.yml build

# 开发环境
docker-compose -f docker-compose.simple.yml build
```

### 步骤3: 启动基础服务
```bash
docker-compose up -d mysql redis
sleep 10
```

### 步骤4: 执行数据库迁移
```bash
# 确认当前版本
docker-compose exec -T backend alembic current

# 执行迁移
docker-compose exec -T backend alembic upgrade head

# 验证迁移结果
docker-compose exec -T backend alembic current
```

### 步骤5: 启动所有服务
```bash
docker-compose up -d
```

### 步骤6: 健康检查
- [ ] 后端健康: `curl http://localhost:8000/health`
- [ ] 数据库连接: `docker-compose exec -T backend python -c "from app.database import engine; print(engine.url)"`
- [ ] Redis连接: `docker-compose exec -T redis redis-cli -a $REDIS_PASSWORD ping`

## SBTI功能验证

### API测试
```bash
# SBTI问题接口
curl -X GET http://localhost:8000/api/v1/sbti/questions

# SBTI提交评估
curl -X POST http://localhost:8000/api/v1/sbti/assess \
  -H "Content-Type: application/json" \
  -d '{"answers": [...]}'

# 依恋风格问题
curl -X GET http://localhost:8000/api/v1/attachment/questions

# 依恋风格提交
curl -X POST http://localhost:8000/api/v1/attachment/assess \
  -H "Content-Type: application/json" \
  -d '{"answers": [...]}'

# 深度画像
curl -X GET http://localhost:8000/api/v1/profile/summary
```

### 前端验证
- [ ] SBTI测试页面可访问
- [ ] 依恋风格测试页面可访问
- [ ] 测试结果正确显示

## RAG知识库初始化 (可选)

```bash
# 初始化SBTI知识库
docker-compose exec -T backend python -c "from app.services.rag.knowledge_init import init_sbti_knowledge; init_sbti_knowledge()"

# 验证知识库
docker-compose exec -T backend python -c "from app.services.rag.knowledge_base import KnowledgeBase; kb = KnowledgeBase(); print(kb.collection.count())"
```

## 回滚准备

### 备份当前状态
```bash
# 备份数据库
docker-compose exec -T mysql mysqldump -u root -p$MYSQL_ROOT_PASSWORD emotion_ai > backup_$(date +%Y%m%d_%H%M%S).sql

# 记录当前commit
git rev-parse HEAD > backup_commit.txt
```

### 回滚命令
```bash
# 回滚迁移
./scripts/rollback.sh

# 或手动回滚
docker-compose exec -T backend alembic downgrade -1
docker-compose restart backend
```

## 部署完成确认

- [ ] 所有容器运行正常: `docker-compose ps`
- [ ] 健康检查全部通过
- [ ] SBTI功能验证通过
- [ ] 前端页面正常访问
- [ ] 日志无错误: `docker-compose logs --tail=100`

## 监控建议

```bash
# 查看后端日志
docker-compose logs -f backend

# 查看错误日志
docker-compose logs backend | grep -i error

# 监控资源使用
docker stats
```

## 紧急联系人

如遇到问题，请联系:
- 后端开发: @backend-dev
- 前端开发: @frontend-dev
- AI工程师: @ai-engineer
- DevOps: @devops
