# SBTI模块部署指南

## 概述

本文档描述AI情感助手SBTI模块的部署流程，包括数据库迁移、服务启动、验证和回滚操作。

## 前置准备

### 环境要求
- Docker >= 20.10
- Docker Compose >= 2.0
- MySQL 8.0
- Redis 7
- Python 3.10+ (本地开发)

### 环境变量配置

创建 `.env.prod` 文件:

```bash
# 数据库配置
MYSQL_ROOT_PASSWORD=your_root_password
MYSQL_DATABASE=emotion_ai
MYSQL_USER=emotion_ai
MYSQL_PASSWORD=your_password

# Redis配置
REDIS_PASSWORD=your_redis_password

# 应用配置
SECRET_KEY=your-secret-key-here
DEBUG=false
LOG_LEVEL=info

# LLM配置
LLM_PROVIDER=openai  # 或 mock
LLM_API_KEY=your-api-key
LLM_BASE_URL=https://api.openai.com/v1

# 端口配置
HTTP_PORT=80
HTTPS_PORT=443
VITE_API_BASE_URL=/api

# 监控配置
GRAFANA_PASSWORD=your_grafana_password
```

## 部署步骤

### 方式一：完整部署（生产环境）

```bash
# 1. 进入项目目录
cd /path/to/emotion-ai-assiant

# 2. 配置环境变量
cp .env.docker.example .env.prod
vim .env.prod

# 3. 执行部署脚本
chmod +x scripts/deploy-sbti.sh
./scripts/deploy-sbti.sh
```

### 方式二：快速部署（开发/测试环境）

```bash
chmod +x scripts/quick-deploy.sh
./scripts/quick-deploy.sh
```

### 方式三：手动部署

```bash
# 1. 构建镜像
docker-compose -f docker-compose.prod.yml build

# 2. 启动基础服务
docker-compose -f docker-compose.prod.yml up -d mysql redis

# 3. 等待服务就绪
sleep 10

# 4. 运行数据库迁移
docker-compose -f docker-compose.prod.yml exec -T backend alembic upgrade head

# 5. 启动所有服务
docker-compose -f docker-compose.prod.yml up -d
```

## 数据库迁移

### 查看迁移状态
```bash
docker-compose -f docker-compose.prod.yml exec -T backend alembic current
docker-compose -f docker-compose.prod.yml exec -T backend alembic history
```

### 执行迁移
```bash
# 升级到最新
docker-compose -f docker-compose.prod.yml exec -T backend alembic upgrade head

# 升级到指定版本
docker-compose -f docker-compose.prod.yml exec -T backend alembic upgrade <revision_id>
```

### 回滚迁移
```bash
# 回滚一步
docker-compose -f docker-compose.prod.yml exec -T backend alembic downgrade -1

# 回滚到起点
docker-compose -f docker-compose.prod.yml exec -T backend alembic downgrade base

# 回滚到指定版本
docker-compose -f docker-compose.prod.yml exec -T backend alembic downgrade <revision_id>
```

或使用回滚脚本:
```bash
chmod +x scripts/rollback.sh
./scripts/rollback.sh              # 回滚一步
./scripts/rollback.sh base          # 回滚到初始状态
./scripts/rollback.sh <version>     # 回滚到指定版本
```

## 验证部署

### API健康检查
```bash
# 基础健康检查
curl http://localhost:8000/health

# SBTI问题接口
curl http://localhost:8000/api/v1/sbti/questions

# 依恋风格接口
curl http://localhost:8000/api/v1/attachment/questions

# 深度画像接口
curl http://localhost:8000/api/v1/profile/summary
```

### 前端检查
```bash
curl http://localhost
```

### 容器状态检查
```bash
docker-compose -f docker-compose.prod.yml ps
```

## 监控和日志

### 查看日志
```bash
# 后端日志
docker-compose -f docker-compose.prod.yml logs -f backend

# 前端日志
docker-compose -f docker-compose.prod.yml logs -f web

# Nginx日志
docker-compose -f docker-compose.prod.yml logs -f nginx

# 所有服务日志
docker-compose -f docker-compose.prod.yml logs -f
```

### 监控面板
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (admin/grafana_password)

## 备份策略

### 数据库备份
```bash
# 创建备份
docker-compose -f docker-compose.prod.yml exec -T mysql mysqldump \
  -u root -p$MYSQL_ROOT_PASSWORD emotion_ai > backup_$(date +%Y%m%d).sql

# 恢复备份
docker-compose exec -T mysql mysql -u root -p$MYSQL_ROOT_PASSWORD emotion_ai < backup_20260411.sql
```

## 故障排除

### 常见问题

1. **迁移失败**
   ```bash
   # 检查数据库连接
   docker-compose -f docker-compose.prod.yml exec -T backend python -c "from app.database import engine; print(engine.url)"
   
   # 手动运行迁移并查看详细错误
   docker-compose -f docker-compose.prod.yml exec -T backend alembic upgrade head --sql
   ```

2. **服务启动失败**
   ```bash
   # 检查容器状态
   docker-compose -f docker-compose.prod.yml ps -a
   
   # 查看详细日志
   docker-compose -f docker-compose.prod.yml logs backend
   ```

3. **端口冲突**
   ```bash
   # 检查端口占用
   lsof -i :8000
   lsof -i :80
   
   # 修改.env.prod中的端口配置
   ```

## 安全建议

1. 生产环境务必修改默认密码
2. 启用HTTPS (配置SSL证书)
3. 定期更新镜像版本
4. 限制数据库访问权限
5. 启用防火墙规则

## 联系我们

如有问题，请联系开发团队。
