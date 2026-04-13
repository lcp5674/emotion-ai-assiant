# AI情感助手 - 部署检查清单 v2.0

## 一、部署前检查

### 1.1 环境要求

| 项目 | 最低要求 | 推荐配置 |
|------|---------|---------|
| CPU | 2核 | 4核+ |
| 内存 | 4GB | 8GB+ |
| 磁盘 | 20GB | 50GB+ |
| Docker | 20.10+ | 最新版本 |
| Docker Compose | 2.0+ | 最新版本 |

### 1.2 必需文件检查

```bash
# 配置文件
[ ] .env.docker                  # 环境变量配置
[ ] docker-compose.yml           # 完整部署配置
[ ] docker-compose.prod.yml      # 生产部署配置
[ ] docker-compose.simple.yml    # 简化部署配置

# 后端文件
[ ] backend/Dockerfile           # 后端容器配置
[ ] backend/app/main.py          # FastAPI 入口
[ ] backend/requirements.txt      # Python 依赖

# 前端文件
[ ] frontend/web/Dockerfile      # 前端容器配置
[ ] frontend/web/nginx.conf      # Nginx 配置
[ ] frontend/web/dist/           # 构建产物目录

# 部署脚本
[ ] deploy/deploy.sh             # 部署脚本
[ ] deploy/backup.sh             # 备份脚本
[ ] deploy/health_check.sh       # 健康检查脚本
```

### 1.3 端口检查

| 端口 | 服务 | 用途 | 必需 |
|------|------|------|------|
| 80 | Nginx | HTTP 服务 | ✅ |
| 443 | Nginx | HTTPS 服务 | 可选 |
| 3306 | MySQL | 数据库 | ✅ |
| 6379 | Redis | 缓存服务 | ✅ |
| 8000 | Backend | API 服务 | ✅ |
| 9000 | MinIO | 对象存储 | 推荐 |
| 9001 | MinIO Console | 管理界面 | 可选 |

### 1.4 环境变量检查

```bash
# 必填项
MYSQL_ROOT_PASSWORD=xxx          # MySQL root 密码
MYSQL_PASSWORD=xxx               # MySQL 应用密码
SECRET_KEY=xxx                  # 应用密钥 (32位十六进制)
REDIS_PASSWORD=xxx              # Redis 密码

# 选填项 (有默认值)
MYSQL_DATABASE=emotion_ai       # 数据库名
MYSQL_USER=emotion_ai           # 数据库用户
LLM_PROVIDER=mock               # LLM 提供商
LLM_API_KEY=xxx                 # LLM API Key
LLM_API_BASE=xxx                # LLM API 地址
MINIO_ROOT_USER=minioadmin      # MinIO 用户
MINIO_ROOT_PASSWORD=xxx         # MinIO 密码
```

## 二、部署模式选择

### 2.1 简化部署 (开发/测试)

```bash
./deploy/deploy.sh --simple
# 或
./deploy/deploy.sh -s
```

**包含服务**: MySQL, Redis, Backend, Nginx

**资源需求**: 2CPU / 4GB

### 2.2 完整部署 (小规模生产)

```bash
./deploy/deploy.sh
```

**包含服务**: MySQL, Redis, MinIO, Backend, Nginx

**资源需求**: 4CPU / 8GB

### 2.3 生产部署 (大规模生产)

```bash
./deploy/deploy.sh --prod
# 或
./deploy/deploy.sh -p
```

**包含服务**: 所有服务 + 资源限制 + 安全加固

**资源需求**: 6CPU / 12GB

### 2.4 微服务部署 (企业级)

```bash
./deploy/deploy.sh --microservices
# 或
./deploy/deploy.sh -ms
```

**包含服务**: API Gateway, Auth Service, Chat Service, Member Service, MySQL, Redis, Prometheus, Grafana, Frontend

**资源需求**: 8CPU / 16GB

## 三、部署流程检查

### 3.1 部署步骤

```
[ ] 步骤 1: 前置检查
    - [ ] Docker 已安装
    - [ ] Docker Compose 已安装
    - [ ] Docker daemon 正在运行
    - [ ] 配置文件存在

[ ] 步骤 2: 端口检查
    - [ ] 必需端口未被占用
    - [ ] 防火墙已配置

[ ] 步骤 3: 环境配置
    - [ ] SECRET_KEY 已生成
    - [ ] 数据库密码已设置
    - [ ] Redis 密码已设置

[ ] 步骤 4: 数据目录创建
    - [ ] ./data/mysql 目录
    - [ ] ./data/redis 目录
    - [ ] ./data/minio 目录
    - [ ] ./data/uploads 目录
    - [ ] ./data/logs/nginx 目录

[ ] 步骤 5: 服务启动
    - [ ] Docker 镜像构建
    - [ ] 容器启动
    - [ ] 服务依赖满足

[ ] 步骤 6: 健康检查
    - [ ] MySQL 健康检查通过
    - [ ] Redis 健康检查通过
    - [ ] Backend API 健康检查通过
    - [ ] Frontend 健康检查通过
```

### 3.2 部署后验证

```bash
# 1. 检查服务状态
docker ps

# 2. 检查服务日志
docker logs emotion-ai-backend
docker logs emotion-ai-nginx

# 3. 检查 API 健康
curl http://localhost:8000/api/v1/health
curl http://localhost:8000/health

# 4. 检查前端访问
curl http://localhost/

# 5. 检查数据库连接
docker exec emotion-ai-mysql mysqladmin ping -h localhost -u root -p

# 6. 检查 Redis 连接
nc -z localhost 6379
```

## 四、生产环境配置检查

### 4.1 容器安全配置 ✅ 已完善

| 配置项 | 状态 | 说明 |
|--------|------|------|
| `restart: unless-stopped` | ✅ | 容器异常自动重启 |
| `security_opt: no-new-privileges` | ✅ | 禁止提升权限 |
| `user: non-root` | ✅ | 非 root 用户运行 |
| `read_only: true` | ✅ | 只读文件系统 |
| `tmpfs` | ✅ | 临时内存文件系统 |

### 4.2 资源限制配置 ✅ 已完善

| 服务 | CPU 限制 | 内存限制 |
|------|---------|---------|
| MySQL | 2.0 | 4G |
| Redis | 1.0 | 1G |
| MinIO | 1.0 | 2G |
| Backend | 2.0 | 4G |
| Nginx | 1.0 | 512M |

### 4.3 健康检查配置 ✅ 已完善

| 服务 | 检查间隔 | 超时 | 重试次数 |
|------|---------|------|---------|
| MySQL | 30s | 10s | 5 |
| Redis | 30s | 10s | 5 |
| MinIO | 30s | 20s | 3 |
| Backend | 30s | 10s | 3 |
| Nginx | 30s | 10s | 3 |

### 4.4 日志配置 ✅ 已完善

| 配置项 | 设置 |
|--------|------|
| 日志驱动 | json-file |
| 最大文件大小 | 100m |
| 最大文件数 | 5 |

## 五、数据备份检查

### 5.1 备份策略

| 数据类型 | 备份频率 | 保留时间 | 备份命令 |
|---------|---------|---------|---------|
| MySQL | 每日 | 7天 | `./deploy/backup.sh db` |
| Redis | 每日 | 7天 | `./deploy/backup.sh redis` |
| MinIO | 每日 | 7天 | `./deploy/backup.sh minio` |
| 上传文件 | 每周 | 30天 | `./deploy/backup.sh uploads` |
| 配置文件 | 每次部署 | 30天 | `./deploy/backup.sh configs` |
| 全量备份 | 每周 | 30天 | `./deploy/backup.sh all` |

### 5.2 备份验证

```bash
# 查看备份状态
./deploy/backup.sh status

# 验证备份完整性
gunzip -t ./backups/mysql/emotion_ai_*.sql.gz

# 测试备份恢复
docker exec -i emotion-ai-mysql mysql -u root -p < ./backups/mysql/emotion_ai_*.sql.gz
```

## 六、监控与告警检查

### 6.1 监控端点

| 端点 | 用途 | 访问方式 |
|------|------|---------|
| http://localhost:9090 | Prometheus | 监控指标 |
| http://localhost:3000 | Grafana | 可视化面板 |
| http://localhost:8000/metrics | 应用指标 | Prometheus 格式 |

### 6.2 健康检查脚本

```bash
# 简洁模式
./deploy/health_check.sh

# JSON 模式 (适用于程序调用)
./deploy/health_check.sh json

# 自定义超时
./deploy/health_check.sh simple 10
```

## 七、安全检查清单

### 7.1 容器安全 ✅

- [ ] 容器以非 root 用户运行
- [ ] 启用 `no-new-privileges`
- [ ] 使用只读文件系统
- [ ] 敏感数据通过环境变量注入
- [ ] 不在容器中存储密钥

### 7.2 网络安全 ✅

- [ ] 使用自定义网络隔离
- [ ] 禁用 IPv6
- [ ] 限制端口暴露
- [ ] 配置 SSL/TLS (生产环境)

### 7.3 数据安全 ✅

- [ ] 数据库密码足够复杂
- [ ] Redis 密码已设置
- [ ] 定期备份数据
- [ ] 备份文件加密存储
- [ ] SECRET_KEY 已更新

### 7.4 应用安全 ⚠️ 需配置

- [ ] 启用 CORS 限制
- [ ] 配置 Rate Limiting
- [ ] 启用请求日志
- [ ] 配置会话超时

## 八、故障排查检查

### 8.1 常见问题

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| 容器无法启动 | 端口被占用 | 检查并释放端口 |
| 数据库连接失败 | 密码错误 | 检查 .env.docker |
| 前端无法访问 | Nginx 未启动 | 检查容器状态 |
| API 返回 500 | 代码错误 | 查看后端日志 |
| 内存不足 | 资源限制过小 | 调整 docker-compose |

### 8.2 排查命令

```bash
# 1. 查看所有容器状态
docker ps -a

# 2. 查看容器日志
docker logs -f emotion-ai-backend
docker logs -f emotion-ai-mysql

# 3. 进入容器调试
docker exec -it emotion-ai-backend bash
docker exec -it emotion-ai-mysql mysql -u root -p

# 4. 检查网络连接
docker network inspect emotion-ai-network

# 5. 检查资源使用
docker stats

# 6. 重启单个服务
docker-compose restart backend
```

## 九、回滚检查

### 9.1 回滚步骤

```bash
# 1. 停止当前服务
docker-compose down

# 2. 恢复数据库
gunzip < ./backups/mysql/emotion_ai_YYYYMMDD_HHMMSS.sql.gz | \
  docker exec -i emotion-ai-mysql mysql -u root -p

# 3. 恢复 Redis
gunzip < ./backups/redis/redis_YYYYMMDD_HHMMSS.rdb.gz | \
  docker exec -i emotion-ai-redis redis-cli -a PASSWORD --pipe

# 4. 恢复 MinIO
gunzip -c ./backups/minio/minio_YYYYMMDD_HHMMSS.tar.gz | \
  docker exec -i emotion-ai-minio tar -xzf - -C /data

# 5. 重新启动服务
docker-compose up -d
```

## 十、部署完成确认

### 10.1 功能验证清单

```
[ ] 前端页面正常访问
[ ] 用户注册功能正常
[ ] 用户登录功能正常
[ ] MBTI 测试功能正常
[ ] AI 聊天功能正常
[ ] 会员充值功能正常 (如已配置)
[ ] 文件上传功能正常
```

### 10.2 性能验证清单

```
[ ] 页面加载时间 < 3s
[ ] API 响应时间 < 500ms
[ ] 数据库查询时间 < 100ms
[ ] 无内存泄漏
[ ] 无 CPU 异常飙升
```

### 10.3 最终确认

```
[ ] 所有服务运行正常
[ ] 健康检查全部通过
[ ] 备份已配置并测试
[ ] 监控已配置
[ ] 日志正常记录
[ ] 文档已更新
```

---

**部署完成日期**: _________________

**部署版本**: _________________

**部署人**: _________________

**备注**: _________________
