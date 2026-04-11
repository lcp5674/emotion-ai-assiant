# AI情感助手运维手册

## 文档版本
- 版本: v1.0
- 日期: 2024-01-01
- 作者: 运维团队

## 目录
1. [架构概述](#架构概述)
2. [快速部署](#快速部署)
3. [服务管理](#服务管理)
4. [SSL证书配置](#ssl证书配置)
5. [备份与恢复](#备份与恢复)
6. [监控告警](#监控告警)
7. [日志管理](#日志管理)
8. [性能优化](#性能优化)
9. [安全加固](#安全加固)
10. [故障排查](#故障排查)
11. [版本升级](#版本升级)
12. [应急响应](#应急响应)

---

## 1. 架构概述

### 1.1 系统架构
```
┌─────────────────┐     ┌───────────────┐     ┌───────────────┐
│   用户浏览器    │────▶│   Nginx反向代理│────▶│   前端Web服务 │
└─────────────────┘     └───────────────┘     └───────────────┘
                               │
                               ▼
                        ┌───────────────┐     ┌───────────────┐
                        │   后端API服务 │────▶│   MySQL数据库 │
                        └───────────────┘     └───────────────┘
                               │
                               ▼
                        ┌───────────────┐
                        │   Redis缓存   │
                        └───────────────┘
                               │
                               ▼
                        ┌───────────────┐
                        │  LLM大模型服务│
                        └───────────────┘
```

### 1.2 服务组件
| 服务 | 端口 | 说明 | 网络 |
|------|------|------|------|
| Nginx | 80/443 | 反向代理、SSL终端 | web/frontend |
| Web | 80 | 前端静态服务 | frontend |
| Backend | 8000 | 后端API服务 | frontend/backend |
| MySQL | 3306 | 关系型数据库 | backend（内部） |
| Redis | 6379 | 缓存服务 | backend（内部） |
| Prometheus | 9090 | 监控指标存储 | monitoring（内部） |
| Grafana | 3000 | 监控可视化 | monitoring/frontend |

### 1.3 网络隔离
- **web网络**: 公网暴露，仅Nginx接入
- **frontend网络**: 前端服务网络，包含Nginx、Web、Backend
- **backend网络**: 后端内部网络，包含MySQL、Redis，不对外暴露
- **monitoring网络**: 监控网络，内部使用

---

## 2. 快速部署

### 2.1 环境要求
- 操作系统: Ubuntu 20.04+ / CentOS 7+
- 硬件配置: 4核CPU / 8GB内存 / 50GB磁盘
- 软件依赖: Docker 20.10+, Docker Compose 2.0+
- 网络要求: 开放80/443端口，可访问公网

### 2.2 一键部署
```bash
# 1. 克隆项目
git clone <repository-url>
cd emotion-ai-assiant

# 2. 复制并配置环境变量
cp .env.example .env
# 编辑 .env 文件，配置所有必填项（密码、密钥等）

# 3. 执行一键部署
sudo ./deploy/scripts/deploy.sh
```

### 2.3 部署验证
```bash
# 查看服务状态
./deploy/scripts/manage.sh status

# 健康检查
./deploy/scripts/manage.sh health

# 访问验证
curl http://localhost/health  # 应返回 ok
curl http://localhost/api/health  # 应返回 {"status":"ok"}
```

---

## 3. 服务管理

### 3.1 快速管理命令
使用统一的管理脚本：
```bash
# 查看帮助
./deploy/scripts/manage.sh help

# 查看服务状态
./deploy/scripts/manage.sh status

# 启动/停止/重启服务
./deploy/scripts/manage.sh start
./deploy/scripts/manage.sh stop
./deploy/scripts/manage.sh restart [服务名]

# 查看日志
./deploy/scripts/manage.sh logs [服务名]

# 进入容器shell
./deploy/scripts/manage.sh shell backend
```

### 3.2 常用Docker Compose命令
```bash
# 启动所有服务
docker-compose -f docker-compose.prod.yml up -d

# 停止所有服务
docker-compose -f docker-compose.prod.yml down

# 查看日志
docker-compose -f docker-compose.prod.yml logs -f backend

# 重启单个服务
docker-compose -f docker-compose.prod.yml restart nginx

# 重新构建镜像
docker-compose -f docker-compose.prod.yml build --no-cache backend
```

### 3.3 服务启停顺序
1. 启动顺序: MySQL → Redis → Backend → Web → Nginx → 监控服务
2. 停止顺序: Nginx → Web → Backend → Redis → MySQL → 监控服务

---

## 4. SSL证书配置

### 4.1 自动配置（推荐）
使用Let's Encrypt免费证书，支持自动续期：
```bash
# 确保域名已解析到服务器
# 在 .env 文件中配置 DOMAIN 和 SSL_EMAIL
./deploy/scripts/manage.sh ssl
```

### 4.2 手动配置
如果使用第三方证书：
```bash
# 创建证书目录
mkdir -p deploy/ssl/live/your-domain.com

# 复制证书文件
cp fullchain.pem deploy/ssl/live/your-domain.com/
cp privkey.pem deploy/ssl/live/your-domain.com/

# 生成HTTPS配置
sed "s/\${DOMAIN}/your-domain.com/g" deploy/nginx/conf.d/emotion-ai.https.conf.template > deploy/nginx/conf.d/emotion-ai.conf

# 重启Nginx
./deploy/scripts/manage.sh restart nginx
```

### 4.3 证书续期
- Let's Encrypt证书有效期90天
- 系统已配置自动续期任务，每天检查2次
- 续期成功后会自动重启Nginx服务

---

## 5. 备份与恢复

### 5.1 自动备份
- 系统默认配置每日凌晨2点自动备份
- 备份内容: MySQL数据库、上传文件、配置文件
- 备份保留: 默认保留7天
- 备份位置: `deploy/backup/`

### 5.2 手动备份
```bash
# 执行手动备份
./deploy/scripts/manage.sh backup
```

### 5.3 数据恢复
```bash
# 执行恢复操作（会覆盖现有数据，请谨慎操作）
./deploy/scripts/manage.sh restore
```

### 5.4 备份策略建议
- 每日全量备份
- 异地备份（建议同步到对象存储或其他服务器）
- 定期验证备份可用性（每月至少1次恢复测试）

---

## 6. 监控告警

### 6.1 监控体系
- **主机监控**: Node Exporter + Prometheus + Grafana
- **应用监控**: 后端内置健康检查接口
- **日志监控**: ELK Stack（可选）
- **链路追踪**: Jaeger（可选）

### 6.2 Grafana使用
```bash
# 访问地址: http://your-domain/grafana/ (需要先在Nginx配置中开启)
# 默认用户名: admin
# 默认密码: 在.env文件中配置的GRAFANA_PASSWORD
```

### 6.3 关键监控指标
| 指标类型 | 阈值 | 告警级别 |
|----------|------|----------|
| CPU使用率 | >80% 持续5分钟 | 警告 |
| 内存使用率 | >85% 持续5分钟 | 警告 |
| 磁盘使用率 | >90% | 严重 |
| 服务存活 | 服务异常 | 严重 |
| API错误率 | >5% 持续1分钟 | 警告 |
| API响应时间 | >1s 持续1分钟 | 警告 |

### 6.4 告警配置
支持多种告警渠道：
- 邮件告警
- 企业微信/钉钉/飞书机器人
- 短信告警
- PagerDuty/Opsgenie

---

## 7. 日志管理

### 7.1 日志位置
| 服务 | 日志路径 | 说明 |
|------|----------|------|
| Nginx | `docker logs emotion-ai-nginx` 或 `deploy/logs/nginx/` | 访问日志和错误日志 |
| 后端 | `docker logs emotion-ai-backend` 或 `backend/logs/` | 应用日志 |
| MySQL | `docker logs emotion-ai-mysql` | 数据库日志、慢查询日志 |
| Redis | `docker logs emotion-ai-redis` | 缓存服务日志 |

### 7.2 日志查询
```bash
# 查看所有服务日志
./deploy/scripts/manage.sh logs

# 查看特定服务日志
./deploy/scripts/manage.sh logs backend

# 查看最近100行日志
docker logs --tail 100 emotion-ai-nginx

# 实时查看日志
docker logs -f --tail 10 emotion-ai-backend
```

### 7.3 日志轮转
- Docker日志默认配置自动轮转
- 保留最近30天日志
- 单个日志文件最大100M

---

## 8. 性能优化

### 8.1 系统优化
```bash
# 优化文件句柄限制
echo "* soft nofile 65535" >> /etc/security/limits.conf
echo "* hard nofile 65535" >> /etc/security/limits.conf

# 优化内核参数
cat >> /etc/sysctl.conf << EOF
net.core.somaxconn = 65535
net.core.netdev_max_backlog = 65535
net.ipv4.tcp_max_syn_backlog = 65535
net.ipv4.tcp_fin_timeout = 30
net.ipv4.tcp_tw_reuse = 1
net.ipv4.tcp_tw_recycle = 1
EOF
sysctl -p
```

### 8.2 数据库优化
- MySQL缓冲池设置为物理内存的50-70%
- 为常用查询字段添加索引
- 定期清理慢查询日志
- 每月进行一次数据表优化

### 8.3 应用优化
- 启用Gzip压缩
- 配置静态资源CDN
- 合理设置Redis缓存过期时间
- 调整后端工作进程数（建议为CPU核心数的2倍）

---

## 9. 安全加固

### 9.1 系统安全
- 定期更新系统补丁
- 配置防火墙，仅开放必要端口（80/443）
- 禁用root用户SSH登录
- 使用SSH密钥登录，禁用密码登录
- 配置fail2ban防止暴力破解

### 9.2 应用安全
- 所有密码使用强密码（至少16位，包含大小写、数字、特殊字符）
- SECRET_KEY使用32位随机字符串
- 定期更新依赖包，修复安全漏洞
- 配置CORS白名单
- 启用HTTPS，强制HTTP跳转到HTTPS

### 9.3 数据安全
- 数据库开启SSL连接
- 敏感数据加密存储
- 定期备份，异地存储
- 数据库访问权限最小化

### 9.4 容器安全
- 使用官方基础镜像，定期更新
- 容器以非root用户运行
- 禁用容器特权模式
- 限制容器资源使用
- 定期扫描镜像漏洞

---

## 10. 故障排查

### 10.1 通用排查步骤
1. **查看服务状态**: `./deploy/scripts/manage.sh status`
2. **查看错误日志**: `./deploy/scripts/manage.sh logs [服务名]`
3. **检查资源使用**: `./deploy/scripts/manage.sh health`
4. **检查网络连通性**: 测试服务间网络通信
5. **检查配置文件**: 确认配置文件没有错误

### 10.2 常见故障

#### 10.2.1 502 Bad Gateway
**可能原因**:
- 后端服务未启动
- 后端服务崩溃
- 服务间网络不通

**排查步骤**:
```bash
# 1. 检查后端服务状态
./deploy/scripts/manage.sh status backend

# 2. 查看后端日志
./deploy/scripts/manage.sh logs backend

# 3. 测试后端健康检查
curl http://localhost:8000/health

# 4. 重启后端服务
./deploy/scripts/manage.sh restart backend
```

#### 10.2.2 504 Gateway Timeout
**可能原因**:
- 后端API响应太慢
- 数据库查询慢
- 系统资源不足

**排查步骤**:
```bash
# 1. 查看系统资源使用
top/htop

# 2. 查看数据库慢查询日志
docker exec emotion-ai-mysql slowlog get 10

# 3. 分析API性能
# 开启后端慢查询日志
```

#### 10.2.3 数据库连接失败
**可能原因**:
- 数据库服务未启动
- 数据库密码错误
- 网络不通

**排查步骤**:
```bash
# 1. 检查数据库状态
./deploy/scripts/manage.sh status mysql

# 2. 测试数据库连接
docker exec -it emotion-ai-mysql mysql -u emotion_ai -p

# 3. 检查后端配置中的数据库连接信息
```

#### 10.2.4 内存不足
**可能原因**:
- 内存配置不足
- 内存泄漏
- 并发量太高

**排查步骤**:
```bash
# 1. 查看内存使用
free -h

# 2. 查看进程内存占用
docker stats

# 3. 调整服务资源限制
# 修改docker-compose.prod.yml中的resources配置
```

---

## 11. 版本升级

### 11.1 升级流程
```bash
# 1. 备份数据（非常重要）
./deploy/scripts/manage.sh backup

# 2. 拉取最新代码
git pull

# 3. 检查配置文件变化，更新.env文件
diff .env.example .env

# 4. 重新构建镜像
./deploy/scripts/manage.sh build backend web

# 5. 重启服务
./deploy/scripts/manage.sh restart

# 6. 验证服务正常
./deploy/scripts/manage.sh health
```

### 11.2 降级方案
如果升级出现问题，快速回滚：
```bash
# 1. 停止服务
./deploy/scripts/manage.sh stop

# 2. 回滚到之前的代码版本
git reset --hard <commit-hash>

# 3. 恢复数据（如果有数据库变更）
./deploy/scripts/manage.sh restore

# 4. 重新构建并启动
./deploy/scripts/manage.sh build backend web
./deploy/scripts/manage.sh start
```

### 11.3 数据库迁移
如果版本包含数据库迁移：
```bash
# 进入后端容器
./deploy/scripts/manage.sh shell backend

# 执行迁移命令
python -m app.db.migrate
```

---

## 12. 应急响应

### 12.1 紧急故障处理流程
1. **故障发现**: 监控告警或用户反馈
2. **故障确认**: 确认故障影响范围和严重程度
3. **故障止血**: 优先恢复服务，减少影响时间
   - 重启相关服务
   - 切换到备用节点
   - 临时扩容
4. **根因分析**: 排查故障根本原因
5. **问题修复**: 修复问题，避免再次发生
6. **复盘总结**: 记录故障，更新运维手册

### 12.2 服务不可用紧急处理
```bash
# 1. 查看所有服务状态
./deploy/scripts/manage.sh status

# 2. 重启所有服务
./deploy/scripts/manage.sh restart

# 3. 如果还是不可用，检查最近的变更
# 回滚到上一个稳定版本

# 4. 必要时联系开发人员
```

### 12.3 安全事件响应
1. 立即隔离受影响的服务
2. 保留现场证据（日志、内存dump等）
3. 评估影响范围
4. 修复安全漏洞
5. 全面排查系统
6. 通知相关人员

### 12.4 联系方式
- 运维负责人: [姓名] [电话] [邮箱]
- 技术负责人: [姓名] [电话] [邮箱]
- 紧急联系人: [姓名] [电话]

---

**文档更新记录**:
- v1.0 (2024-01-01): 初始版本发布
