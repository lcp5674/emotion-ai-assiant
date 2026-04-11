# AI情感助手快速开始指南

## 🚀 30分钟快速部署生产环境

### 前提条件
1. 一台安装了Ubuntu 20.04+的服务器
2. 一个已解析到服务器IP的域名
3. SSH root权限登录服务器

---

## 步骤1：系统初始化（5分钟）

登录服务器后执行：
```bash
# 更新系统
apt update && apt upgrade -y

# 安装必要工具
apt install -y curl git
```

---

## 步骤2：安装Docker（5分钟）

```bash
# 自动安装Docker脚本
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# 安装Docker Compose
curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# 验证安装
docker --version
docker-compose --version
```

---

## 步骤3：下载项目代码（2分钟）

```bash
git clone <your-project-repository>
cd emotion-ai-assiant
```

---

## 步骤4：配置环境变量（5分钟）

```bash
# 复制配置模板
cp .env.example .env

# 编辑配置文件
vim .env
```

**必须修改的配置项**：
```env
# 数据库密码（至少16位随机字符串）
MYSQL_ROOT_PASSWORD=your_strong_password
MYSQL_PASSWORD=your_strong_password

# Redis密码（至少16位随机字符串）
REDIS_PASSWORD=your_strong_password

# 应用密钥（32位随机字符串，用openssl rand -hex 16生成）
SECRET_KEY=your_32_character_secret_key

# LLM配置（如果不需要可以保持mock）
LLM_PROVIDER=mock
LLM_API_KEY=your_llm_api_key

# Grafana监控密码
GRAFANA_PASSWORD=your_strong_password

# 你的域名和邮箱
DOMAIN=your-domain.com
SSL_EMAIL=your-email@example.com
```

生成随机密钥示例：
```bash
# 生成32位SECRET_KEY
openssl rand -hex 16

# 生成强密码
openssl rand -base64 16
```

---

## 步骤5：一键部署（10分钟）

```bash
# 执行部署脚本
sudo ./deploy/scripts/deploy.sh
```

等待部署完成，看到✅部署完成的提示说明成功。

---

## 步骤6：配置SSL证书（3分钟）

```bash
# 自动配置HTTPS
./deploy/scripts/manage.sh ssl
```

脚本会自动申请并配置Let's Encrypt免费证书，支持自动续期。

---

## ✅ 部署完成！

现在你可以访问：
- 🌐 网站地址：`https://your-domain.com`
- 🔧 健康检查：`https://your-domain.com/health`
- 📊 监控面板：`https://your-domain.com/grafana/`（需要先配置Nginx）

---

## 基础运维命令

### 查看服务状态
```bash
./deploy/scripts/manage.sh status
```

### 查看服务日志
```bash
# 查看所有日志
./deploy/scripts/manage.sh logs

# 查看后端日志
./deploy/scripts/manage.sh logs backend
```

### 重启服务
```bash
# 重启所有服务
./deploy/scripts/manage.sh restart

# 重启单个服务
./deploy/scripts/manage.sh restart backend
```

### 手动备份
```bash
./deploy/scripts/manage.sh backup
```

### 系统更新
```bash
./deploy/scripts/manage.sh update
```

### 健康检查
```bash
./deploy/scripts/manage.sh health
```

---

## 常用操作

### 如何修改配置？
1. 编辑 `.env` 文件
2. 重启服务生效：`./deploy/scripts/manage.sh restart`

### 如何查看备份文件？
备份文件默认存储在 `deploy/backup/` 目录下。

### 如何升级到最新版本？
```bash
./deploy/scripts/manage.sh update
```

### 如何恢复数据？
```bash
./deploy/scripts/manage.sh restore
```

---

## 常见问题

### Q: 部署失败怎么办？
A: 查看部署日志 `deploy/logs/`，根据错误提示修复后重新运行部署脚本。

### Q: 网站打不开怎么办？
A: 
1. 检查域名是否解析正确
2. 检查防火墙是否开放80/443端口
3. 查看服务状态：`./deploy/scripts/manage.sh status`
4. 查看错误日志：`./deploy/scripts/manage.sh logs`

### Q: SSL证书申请失败？
A: 确保80端口开放，域名正确解析到服务器IP。

### Q: 如何关闭服务？
```bash
./deploy/scripts/manage.sh stop
```

---

## 文档索引
- 📖 **生产部署指南**: `PRODUCTION_DEPLOYMENT_GUIDE.md`
- 🔧 **运维手册**: `OPERATION_MANUAL.md`
- ❌ **故障排查指南**: `TROUBLESHOOTING_GUIDE.md`
- 🏗️ **架构说明**: `DEPLOYMENT_ARCHITECTURE.md`

---

## 技术支持
如遇到问题，请查看故障排查指南或联系技术支持。

🎉 **恭喜！您的AI情感助手已经成功部署上线！**
