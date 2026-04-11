# AI情感助手故障排查指南

## 文档信息
- 版本: v1.0
- 最后更新: 2024-01-01
- 适用场景: 生产环境故障快速定位和修复

---

## 目录
1. [故障排查方法论](#故障排查方法论)
2. [紧急故障快速处理](#紧急故障快速处理)
3. [常见故障排查](#常见故障排查)
   - [网站无法访问](#网站无法访问)
   - [502 Bad Gateway](#502-bad-gateway)
   - [503 Service Unavailable](#503-service-unavailable)
   - [504 Gateway Timeout](#504-gateway-timeout)
   - [数据库连接错误](#数据库连接错误)
   - [Redis连接错误](#redis连接错误)
   - [静态资源加载失败](#静态资源加载失败)
   - [API请求失败](#api请求失败)
   - [文件上传失败](#文件上传失败)
   - [SSL证书错误](#ssl证书错误)
   - [磁盘空间不足](#磁盘空间不足)
   - [内存不足(OOM)](#内存不足oom)
   - [CPU使用率过高](#cpu使用率过高)
4. [日志分析指南](#日志分析指南)
5. [性能瓶颈定位](#性能瓶颈定位)
6. [附录：常用命令速查](#附录常用命令速查)

---

## 故障排查方法论

### 1. 黄金排查步骤
```
1. 现象确认 → 2. 范围评估 → 3. 分层排查 → 4. 根因定位 → 5. 修复验证 → 6. 复盘总结
```

### 2. 分层排查顺序
从外到内，逐层排查：
```
用户端 → 网络 → 防火墙 → Nginx → Web服务 → Backend服务 → 缓存 → 数据库 → 硬件
```

### 3. 先止血，后排查
- 优先恢复服务，减少影响时间
- 重启服务是最简单有效的快速恢复手段
- 保留故障现场（日志、监控数据）以便后续分析

---

## 紧急故障快速处理

### 快速恢复 Checklist
当发生严重故障时，按以下顺序尝试恢复：

| 步骤 | 操作 | 预期效果 | 耗时 |
|------|------|----------|------|
| 1 | 重启所有服务: `./deploy/scripts/manage.sh restart` | 80%的故障可通过重启恢复 | 1分钟 |
| 2 | 检查磁盘空间: `df -h` | 清理磁盘空间 | 30秒 |
| 3 | 检查端口占用: `netstat -tlnp` | 确认端口没有被占用 | 30秒 |
| 4 | 查看错误日志: `./deploy/scripts/manage.sh logs` | 找到明显的错误信息 | 2分钟 |
| 5 | 回滚到上一版本 | 如果是版本升级导致的问题 | 5分钟 |
| 6 | 恢复备份 | 如果是数据损坏导致的问题 | 10分钟 |

---

## 常见故障排查

### 网站无法访问

#### 症状
用户无法打开网站，浏览器显示"无法访问此网站"或"连接超时"

#### 排查步骤
1. **检查网络连通性**
   ```bash
   # 本地测试端口是否开放
   telnet your-domain.com 80
   telnet your-domain.com 443
   
   # 或者使用curl
   curl -v http://your-domain.com
   ```

2. **检查服务器状态**
   ```bash
   # 确认服务器是否存活
   ping your-server-ip
   
   # 登录服务器查看服务状态
   ./deploy/scripts/manage.sh status
   ```

3. **检查防火墙/安全组**
   ```bash
   # 查看防火墙规则
   iptables -L -n
   
   # 或UFW
   ufw status
   
   # 检查云服务商安全组是否开放80/443端口
   ```

4. **检查Nginx状态**
   ```bash
   # 查看Nginx进程
   ps aux | grep nginx
   
   # 检查Nginx配置是否正确
   docker exec emotion-ai-nginx nginx -t
   
   # 查看Nginx日志
   ./deploy/scripts/manage.sh logs nginx
   ```

### 502 Bad Gateway

#### 症状
网站可以访问，但显示502错误页面

#### 排查步骤
1. **检查后端服务状态**
   ```bash
   # 查看后端服务是否运行
   ./deploy/scripts/manage.sh status backend
   
   # 查看后端日志
   ./deploy/scripts/manage.sh logs backend
   
   # 直接测试后端服务
   curl http://localhost:8000/health
   ```

2. **检查服务间网络连通性**
   ```bash
   # 进入Nginx容器测试到后端的连通性
   docker exec -it emotion-ai-nginx curl http://backend:8000/health
   ```

3. **检查端口监听**
   ```bash
   # 检查后端是否在监听8000端口
   docker exec emotion-ai-backend netstat -tlnp | grep 8000
   ```

4. **常见原因和解决方法**
   - 后端服务崩溃 → 重启后端服务
   - 后端启动失败 → 查看日志修复错误
   - 端口冲突 → 修改端口配置
   - 内存不足OOM → 增加内存或调整进程数

### 503 Service Unavailable

#### 症状
网站显示503服务不可用

#### 排查步骤
1. **检查服务是否全部启动**
   ```bash
   ./deploy/scripts/manage.sh status
   ```

2. **检查负载情况**
   ```bash
   # 查看系统负载
   top
   # 或
   htop
   
   # 查看Docker资源使用
   docker stats
   ```

3. **检查连接数**
   ```bash
   # 查看Nginx连接数
   netstat -an | grep :80 | wc -l
   
   # 查看后端连接数
   netstat -an | grep :8000 | wc -l
   ```

4. **常见原因**
   - 并发量过高，服务被打满 → 扩容服务
   - 服务正在启动中 → 等待启动完成
   - 维护模式开启 → 关闭维护模式

### 504 Gateway Timeout

#### 症状
请求超时，显示504错误

#### 排查步骤
1. **检查后端响应时间**
   ```bash
   # 测试API响应时间
   time curl http://localhost:8000/api/health
   ```

2. **检查数据库性能**
   ```bash
   # 查看MySQL进程列表
   docker exec -it emotion-ai-mysql mysql -u root -p -e "SHOW PROCESSLIST;"
   
   # 查看慢查询
   docker exec emotion-ai-mysql mysqldumpslow -s t /var/log/mysql/slow.log | head -20
   ```

3. **检查Redis性能**
   ```bash
   # 查看Redis性能
   docker exec emotion-ai-redis redis-cli info stats
   
   # 查看慢查询
   docker exec emotion-ai-redis redis-cli slowlog get 10
   ```

4. **常见原因**
   - 数据库查询慢 → 优化SQL或加索引
   - 外部API调用超时 → 增加超时时间或降级
   - 系统资源不足 → 扩容资源

### 数据库连接错误

#### 症状
后端日志显示"Connection refused"或"Access denied"

#### 排查步骤
1. **检查MySQL服务状态**
   ```bash
   ./deploy/scripts/manage.sh status mysql
   
   # 查看MySQL日志
   ./deploy/scripts/manage.sh logs mysql
   ```

2. **测试数据库连接**
   ```bash
   # 直接测试数据库连接
   docker exec -it emotion-ai-mysql mysql -u emotion_ai -p
   
   # 从后端容器测试连接
   docker exec -it emotion-ai-backend mysql -h mysql -u emotion_ai -p
   ```

3. **检查配置**
   ```bash
   # 确认.env文件中的数据库配置正确
   grep MYSQL_ .env
   ```

4. **常见原因**
   - 密码错误 → 更新正确的密码
   - 数据库服务未启动 → 启动数据库
   - 权限不足 → 授予用户正确的权限
   - 连接数满 → 增加max_connections配置

### Redis连接错误

#### 症状
后端日志显示Redis连接失败

#### 排查步骤
1. **检查Redis服务状态**
   ```bash
   ./deploy/scripts/manage.sh status redis
   
   # 查看Redis日志
   ./deploy/scripts/manage.sh logs redis
   ```

2. **测试Redis连接**
   ```bash
   # 本地测试
   docker exec -it emotion-ai-redis redis-cli ping
   
   # 从后端容器测试
   docker exec -it emotion-ai-backend redis-cli -h redis ping
   ```

3. **检查配置**
   ```bash
   # 确认Redis密码配置正确
   grep REDIS_PASSWORD .env
   ```

4. **常见原因**
   - 密码错误 → 更新正确的密码
   - Redis服务未启动 → 启动Redis
   - 内存满 → 增加内存或调整maxmemory策略

### 静态资源加载失败

#### 症状
页面样式混乱，图片/JS/CSS加载失败

#### 排查步骤
1. **检查前端构建产物**
   ```bash
   # 确认dist目录存在且有文件
   ls -la frontend/web/dist/
   ```

2. **检查Nginx配置**
   ```bash
   # 测试Nginx配置
   docker exec emotion-ai-nginx nginx -t
   
   # 查看Nginx静态资源配置
   docker exec emotion-ai-nginx cat /etc/nginx/conf.d/default.conf
   ```

3. **检查文件权限**
   ```bash
   # 确认静态文件权限正确
   ls -la /usr/share/nginx/html/
   ```

4. **常见原因**
   - 前端构建失败 → 重新构建前端
   - Nginx配置错误 → 修复Nginx配置
   - 文件权限错误 → 调整文件权限

### API请求失败

#### 症状
前端调用API失败，控制台显示错误

#### 排查步骤
1. **检查API地址配置**
   ```bash
   # 确认前端API_BASE_URL配置正确
   grep VITE_API_BASE_URL .env
   ```

2. **检查CORS配置**
   ```bash
   # 查看后端CORS配置
   # 检查响应头是否包含Access-Control-Allow-Origin
   curl -v -H "Origin: https://your-domain.com" http://localhost:8000/api/health
   ```

3. **检查API日志**
   ```bash
   # 查看后端API请求日志
   ./deploy/scripts/manage.sh logs backend
   ```

4. **常见原因**
   - API地址配置错误 → 更新正确的API地址
   - CORS配置错误 → 修复CORS配置
   - 后端API报错 → 修复后端代码

### 文件上传失败

#### 症状
用户上传文件失败

#### 排查步骤
1. **检查上传目录权限**
   ```bash
   # 确认上传目录存在且权限正确
   ls -la backend/uploads/
   
   # 调整权限
   chmod -R 755 backend/uploads/
   chown -R nobody:nogroup backend/uploads/
   ```

2. **检查Nginx上传大小限制**
   ```bash
   # 查看client_max_body_size配置
   docker exec emotion-ai-nginx grep client_max_body_size /etc/nginx/nginx.conf
   ```

3. **检查磁盘空间**
   ```bash
   # 确认磁盘有足够空间
   df -h backend/uploads/
   ```

4. **常见原因**
   - 目录权限不足 → 调整目录权限
   - 文件大小超过限制 → 调整Nginx和后端的上传限制
   - 磁盘满 → 清理磁盘空间

### SSL证书错误

#### 症状
浏览器显示证书不安全或NET::ERR_CERT_*错误

#### 排查步骤
1. **检查证书有效性**
   ```bash
   # 检查证书有效期
   openssl x509 -in deploy/ssl/live/your-domain.com/fullchain.pem -text -noout | grep "Not After"
   
   # 检查证书链
   openssl s_client -connect your-domain.com:443 -servername your-domain.com
   ```

2. **检查Nginx SSL配置**
   ```bash
   # 确认证书路径配置正确
   docker exec emotion-ai-nginx grep ssl_certificate /etc/nginx/conf.d/emotion-ai.conf
   ```

3. **检查证书权限**
   ```bash
   # 确认证书文件权限正确
   ls -la deploy/ssl/live/your-domain.com/
   ```

4. **常见原因**
   - 证书过期 → 重新颁发证书
   - 证书配置错误 → 修复配置路径
   - 证书不匹配 → 使用正确的域名证书

### 磁盘空间不足

#### 症状
服务异常，日志显示"No space left on device"

#### 排查步骤
1. **检查磁盘使用**
   ```bash
   df -h
   ```

2. **查找大文件**
   ```bash
   # 查找大于100M的文件
   find / -type f -size +100M -exec ls -lh {} \; | sort -hr
   
   # 查看Docker占用
   docker system df
   ```

3. **清理空间**
   ```bash
   # 清理Docker无用资源
   ./deploy/scripts/manage.sh cleanup
   
   # 清理旧日志
   find /var/lib/docker/containers/ -name "*.log" -exec truncate -s 0 {} \;
   
   # 清理旧备份（确认备份已转存）
   find deploy/backup/ -name "*.gz" -mtime +7 -delete
   ```

### 内存不足(OOM)

#### 症状
服务被系统杀死，日志显示"OOM killer"或"Killed"

#### 排查步骤
1. **检查内存使用**
   ```bash
   free -h
   
   # 查看OOM日志
   dmesg | grep -i oom
   ```

2. **检查进程内存使用**
   ```bash
   # 查看内存占用最高的进程
   top -o %MEM
   
   # 查看Docker容器内存使用
   docker stats --no-stream
   ```

3. **解决方法**
   - 增加服务器内存
   - 调整服务的内存限制配置
   - 减少后端工作进程数
   - 优化应用内存使用

### CPU使用率过高

#### 症状
系统响应慢，load average很高

#### 排查步骤
1. **检查CPU使用**
   ```bash
   top
   # 或
   mpstat -P ALL 1 3
   ```

2. **查找高CPU进程**
   ```bash
   ps aux --sort=-%cpu | head -10
   
   # 查看Docker容器CPU使用
   docker stats --no-stream
   ```

3. **分析进程**
   ```bash
   # 分析Java进程
   jstack <pid>
   
   # 分析Python进程
   py-spy top --pid <pid>
   ```

4. **常见原因**
   - 死循环 → 修复代码
   - 大量计算任务 → 优化算法或异步处理
   - 流量突增 → 扩容服务

---

## 日志分析指南

### 错误日志关键字
搜索以下关键字快速定位问题：
```
ERROR
Exception
Traceback
Fatal
Killed
OOM
Connection refused
Timeout
denied
No space left
```

### 日志查询技巧
```bash
# 搜索包含ERROR的日志
./deploy/scripts/manage.sh logs backend | grep ERROR

# 搜索最近1小时的错误
./deploy/scripts/manage.sh logs backend --since 1h | grep ERROR

# 实时监控错误日志
./deploy/scripts/manage.sh logs backend -f | grep --line-buffered ERROR

# 统计错误出现次数
./deploy/scripts/manage.sh logs backend | grep "500 Internal Server Error" | wc -l
```

---

## 性能瓶颈定位

### 使用火焰图分析性能
```bash
# 安装py-spy
pip install py-spy

# 生成CPU火焰图
py-spy record -o profile.svg --pid <backend-pid>
```

### 数据库性能分析
```bash
# 查看正在执行的查询
SHOW PROCESSLIST;

# 查看慢查询日志
mysqldumpslow -s t /var/log/mysql/slow.log

# 分析查询性能
EXPLAIN SELECT * FROM users WHERE ...;
```

### 前端性能分析
- 使用Chrome DevTools的Performance面板
- 分析Network瀑布图
- 检查LCP、FID、CLS等核心指标

---

## 附录：常用命令速查

### 系统命令
```bash
# 查看系统信息
uname -a
lsb_release -a

# 查看资源使用
top
htop
iostat
vmstat
df -h
free -h

# 网络相关
netstat -tlnp
ss -tlnp
tcpdump
traceroute
```

### Docker命令
```bash
# 查看容器
docker ps
docker ps -a

# 查看日志
docker logs <container-name>
docker logs -f --tail 100 <container-name>

# 进入容器
docker exec -it <container-name> sh
docker exec -it <container-name> bash

# 资源使用
docker stats
docker system df

# 清理
docker system prune -a
```

### MySQL命令
```bash
# 登录
mysql -u <username> -p

# 查看进程
SHOW PROCESSLIST;

# 查看慢查询
SHOW VARIABLES LIKE 'slow_query_log';
SHOW VARIABLES LIKE 'long_query_time';

# 查看数据库大小
SELECT table_schema AS "Database", 
ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) AS "Size (MB)" 
FROM information_schema.TABLES 
GROUP BY table_schema;
```

### Redis命令
```bash
# 登录
redis-cli

# 查看信息
INFO
INFO stats
INFO memory

# 查看慢查询
SLOWLOG GET 10

# 查看键空间
KEYS *  # 生产环境谨慎使用
SCAN 0
```

---

**紧急联系**:
- 运维值班电话: xxx-xxxxxxx
- 技术支持群: [企业微信/钉钉群链接]

*遇到无法解决的问题，请及时联系相关人员！*
