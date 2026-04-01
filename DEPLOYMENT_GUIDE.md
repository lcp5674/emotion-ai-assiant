# 部署建议文档

## 1. 环境准备

### 1.1 基础环境
- 操作系统：Linux (推荐Ubuntu 20.04+或CentOS 7+)
- Python：3.9+
- Node.js：16+
- 数据库：MySQL 8.0+ 或 PostgreSQL 12+
- Redis：6.0+
- 内存：至少4GB RAM（推荐8GB+）
- 存储空间：至少20GB可用空间

### 1.2 Docker环境（推荐）
如果使用Docker，需要：
- Docker Engine 20.10+
- Docker Compose 2.0+

---

## 2. Docker 部署（推荐）

### 2.1 环境配置

#### 2.1.1 复制环境变量文件
```bash
cd /path/to/emotion-ai-assistant
cp backend/.env.example backend/.env
cp frontend/web/.env.example frontend/web/.env
```

#### 2.1.2 编辑环境变量

**backend/.env**：
```env
# 必填项
SECRET_KEY=your-32-character-secret-key-here
DATABASE_URL=mysql+mysqlconnector://username:password@mysql:3306/emotion_ai

# 可选配置
DEBUG=false
LLM_PROVIDER=mock
```

**frontend/web/.env**：
```env
VITE_API_BASE_URL=http://your-domain.com/api
```

### 2.2 启动服务

```bash
cd /path/to/emotion-ai-assistant
docker-compose up -d
```

### 2.3 验证部署

```bash
# 检查服务状态
docker-compose ps

# 检查日志
docker-compose logs -f

# 验证健康检查
curl -s http://localhost:8000/health
# 预期响应：{"status":"ok","app":"心灵伴侣AI","version":"1.0.0"}
```

### 2.4 常用操作

```bash
# 停止服务
docker-compose down

# 重启服务
docker-compose restart

# 查看数据库
docker exec -it emotion-ai-assistant-mysql-1 mysql -uusername -p

# 重新构建
docker-compose build --no-cache && docker-compose up -d
```

---

## 3. 手动部署（生产环境）

### 3.1 后端部署

#### 3.1.1 虚拟环境
```bash
cd /path/to/emotion-ai-assistant/backend
python -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

#### 3.1.2 数据库初始化
```bash
# 确保MySQL服务运行
# 执行数据库迁移（如果有）
python -m app.db.migrate
```

#### 3.1.3 启动后端
```bash
# 使用Gunicorn（生产推荐）
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:8000 --log-level info --access-logfile - --error-logfile -

# 或使用uvicorn（开发用）
python -m app.main --host 0.0.0.0 --port 8000 --workers 4
```

### 3.2 前端部署

#### 3.2.1 安装依赖
```bash
cd /path/to/emotion-ai-assistant/frontend/web
npm install --legacy-peer-deps
```

#### 3.2.2 构建项目
```bash
npm run build
```

#### 3.2.3 部署到Nginx
```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 前端静态资源
    location / {
        root /path/to/emotion-ai-assistant/frontend/web/dist;
        try_files $uri $uri/ /index.html;
        index index.html;
    }

    # 后端API代理
    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 健康检查
    location /health {
        proxy_pass http://127.0.0.1:8000/health;
    }
}
```

---

## 4. 配置反向代理

### 4.1 Nginx SSL配置

**生产环境必须配置HTTPS**：
```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /path/to/ssl/fullchain.pem;
    ssl_certificate_key /path/to/ssl/privkey.pem;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # ... 其他配置
}

# 强制HTTPS
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}
```

---

## 5. 监控与日志

### 5.1 应用日志
- 后端日志：通过gunicorn/uvicorn配置
- 前端日志：Nginx访问日志
- 数据库日志：MySQL/PostgreSQL日志

### 5.2 监控建议

#### 5.2.1 服务器监控
- 使用Prometheus + Grafana
- 监控指标：CPU、内存、磁盘、网络

#### 5.2.2 应用监控
- 使用Sentry或ELK Stack
- 监控指标：请求响应时间、错误率、吞吐量

---

## 6. 安全建议

### 6.1 数据库安全
- 使用强密码
- 配置防火墙规则（只允许必要IP访问）
- 定期备份
- 启用SSL连接

### 6.2 应用安全
- 设置复杂的SECRET_KEY
- 定期更新依赖
- 配置CORS
- 启用HTTPS

---

## 7. 备份与恢复

### 7.1 数据库备份
```bash
# 每日备份
mysqldump -uusername -p emotion_ai > /path/to/backups/emotion_ai_$(date +%Y%m%d).sql

# 压缩备份
gzip /path/to/backups/emotion_ai_$(date +%Y%m%d).sql
```

### 7.2 恢复数据
```bash
gunzip -c /path/to/backups/emotion_ai_20240101.sql.gz | mysql -uusername -p emotion_ai
```

### 7.3 应用数据备份
- 备份uploads目录
- 备份配置文件
- 备份SSL证书

---

## 8. 性能优化

### 8.1 数据库优化
- 为频繁查询的字段添加索引
- 定期优化表
- 配置适当的缓冲池大小

### 8.2 应用优化
- 使用Redis缓存
- 启用Gunicorn worker进程
- 配置Nginx压缩
- 使用CDN加速静态资源

---

## 9. 常见问题

### 9.1 502 Bad Gateway
- 检查后端服务是否正常
- 检查端口是否被防火墙阻止
- 检查连接数限制

### 9.2 504 Gateway Timeout
- 增加Nginx代理超时时间
- 优化API响应时间
- 检查数据库查询性能

### 9.3 前端API调用失败
- 检查CORS配置
- 验证API_BASE_URL是否正确
- 检查HTTPS证书是否有效

---

## 10. 版本升级

### 10.1 备份数据
```bash
# 备份数据库和文件
```

### 10.2 应用升级
```bash
# 停止服务
# 拉取最新代码
# 安装依赖
# 数据库迁移
# 重启服务
```

---

**部署完成后，访问 `https://your-domain.com` 即可使用AI情感助手！**
