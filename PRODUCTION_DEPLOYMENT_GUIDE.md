# AI情感助手生产环境部署指南

## 版本信息
- 版本: v1.0
- 更新日期: 2024-01-01
- 适用环境: 生产环境

---

## 目录
1. [部署前准备](#部署前准备)
2. [环境配置](#环境配置)
3. [一键部署](#一键部署)
4. [SSL证书配置](#ssl证书配置)
5. [部署验证](#部署验证)
6. [监控配置](#监控配置)
7. [防火墙配置](#防火墙配置)
8. [安全加固](#安全加固)
9. [验收标准](#验收标准)
10. [常见问题](#常见问题)

---

## 1. 部署前准备

### 1.1 硬件要求
| 配置档次 | CPU | 内存 | 磁盘 | 支持用户量 |
|----------|-----|------|------|------------|
| 基础版 | 2核 | 4GB | 50GB SSD | <1000 |
| 标准版 | 4核 | 8GB | 100GB SSD | 1000-5000 |
| 企业版 | 8核 | 16GB | 200GB SSD | 5000-20000 |
| 集群版 | 16核+ | 32GB+ | 500GB SSD+ | >20000 |

### 1.2 软件要求
- 操作系统: Ubuntu 20.04 LTS / 22.04 LTS（推荐）或 CentOS 7/8
- Docker Engine >= 20.10.0
- Docker Compose >= 2.0.0
- 内核版本 >= 5.4

### 1.3 网络要求
- 公网IP地址
- 域名解析到服务器IP
- 开放80和443端口（HTTP/HTTPS）
- 如需远程管理，开放22端口（SSH）
- 服务器可以访问公网（用于拉取镜像和证书颁发）

### 1.4 准备工作清单
✅ 服务器已创建并可以SSH登录
✅ 域名已购买并解析到服务器IP
✅  SSL证书邮箱已准备（用于Let's Encrypt）
✅  LLM API密钥已申请（OpenAI/百度文心/阿里通义等）
✅  所有密码已准备（数据库、Redis、监控等）

---

## 2. 环境配置

### 2.1 系统初始化（Ubuntu）
```bash
# 更新系统
apt update && apt upgrade -y

# 安装必要工具
apt install -y curl wget git vim htop net-tools

# 配置时区
timedatectl set-timezone Asia/Shanghai

# 关闭Swap（推荐）
swapoff -a
sed -i '/ swap / s/^\(.*\)$/#\1/g' /etc/fstab
```

### 2.2 安装Docker
```bash
# 安装Docker依赖
apt install -y apt-transport-https ca-certificates curl gnupg-agent software-properties-common

# 添加Docker GPG密钥
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# 添加Docker源
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

# 安装Docker
apt update && apt install -y docker-ce docker-ce-cli containerd.io

# 安装Docker Compose
curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# 验证安装
docker --version
docker-compose --version

# 配置Docker镜像加速（可选，推荐国内使用）
cat > /etc/docker/daemon.json << EOF
{
  "registry-mirrors": ["https://registry.docker-cn.com", "https://mirror.baidubce.com"],
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "100m",
    "max-file": "3"
  }
}
EOF

# 重启Docker
systemctl daemon-reload
systemctl restart docker
systemctl enable docker
```

### 2.3 下载项目代码
```bash
# 克隆项目
git clone <your-repository-url>
cd emotion-ai-assiant

# 切换到生产分支
git checkout main
```

---

## 3. 一键部署

### 3.1 配置环境变量
```bash
# 复制环境变量模板
cp .env.example .env

# 编辑环境变量文件（必须修改所有标记为your_strong的配置项）
vim .env
```

### 3.2 环境变量说明
```env
# 基础配置
TZ=Asia/Shanghai                          # 时区，保持默认
HTTP_PORT=80                              # HTTP端口，保持默认
HTTPS_PORT=443                            # HTTPS端口，保持默认

# 数据库配置（必须修改）
MYSQL_ROOT_PASSWORD=你的强密码             # MySQL root密码，至少16位
MYSQL_DATABASE=emotion_ai                 # 数据库名，保持默认
MYSQL_USER=emotion_ai                     # 数据库用户名，保持默认
MYSQL_PASSWORD=你的强密码                  # 数据库用户密码，至少16位

# Redis配置（必须修改）
REDIS_PASSWORD=你的强密码                  # Redis密码，至少16位

# 后端配置（必须修改）
SECRET_KEY=32位随机字符串                  # 应用密钥，使用openssl rand -hex 16生成
BACKEND_WORKERS=4                         # 后端工作进程数，建议为CPU核心数的2倍
LLM_PROVIDER=mock                         # LLM提供商：mock/openai/baidu/aliyun等
LLM_API_KEY=你的LLM API密钥                # LLM API密钥
LLM_BASE_URL=https://api.example.com/v1   # LLM API地址

# 前端配置
VITE_API_BASE_URL=/api                    # API基础路径，保持默认

# 监控配置（必须修改）
GRAFANA_PASSWORD=你的强密码                # Grafana管理员密码，至少16位

# 备份配置
BACKUP_RETENTION_DAYS=7                   # 备份保留天数
BACKUP_DIR=./deploy/backup                # 备份目录
BACKUP_CRON=0 2 * * *                     # 备份时间，默认凌晨2点

# SSL配置
DOMAIN=your-domain.com                    # 你的域名，如 ai.example.com
SSL_EMAIL=your-email@example.com          # 你的邮箱，用于证书通知
```

### 3.3 生成密钥示例
```bash
# 生成32位随机SECRET_KEY
openssl rand -hex 16

# 生成强密码示例
openssl rand -base64 16
```

### 3.4 执行一键部署
```bash
# 给部署脚本添加执行权限（已预置）
# chmod +x deploy/scripts/*.sh

# 执行一键部署
sudo ./deploy/scripts/deploy.sh
```

部署过程大约需要5-10分钟，请耐心等待。部署完成后会显示访问地址。

---

## 4. SSL证书配置

### 4.1 自动配置（推荐）
部署完成后执行SSL配置脚本：
```bash
./deploy/scripts/manage.sh ssl
```

脚本会自动完成：
- 安装Certbot工具
- 申请Let's Encrypt免费证书
- 配置HTTPS
- 设置自动续期

### 4.2 验证HTTPS配置
```bash
# 访问测试
curl -v https://your-domain.com/health

# 检查证书有效期
openssl s_client -connect your-domain.com:443 -servername your-domain.com | openssl x509 -noout -dates
```

---

## 5. 部署验证

### 5.1 服务状态检查
```bash
# 查看所有服务状态
./deploy/scripts/manage.sh status

# 预期所有服务状态都是Up
```

### 5.2 健康检查
```bash
# 执行全面健康检查
./deploy/scripts/manage.sh health

# 预期输出：
# ✓ 后端服务正常
# ✓ Nginx服务正常
```

### 5.3 功能验证
1. **访问前端**: 在浏览器打开 https://your-domain.com，应该能正常显示网站
2. **注册登录**: 测试用户注册和登录功能
3. **聊天功能**: 测试AI聊天功能是否正常
4. **上传功能**: 测试头像上传等功能

### 5.4 日志检查
```bash
# 检查是否有错误日志
./deploy/scripts/manage.sh logs backend | grep ERROR
./deploy/scripts/manage.sh logs nginx | grep error
```

---

## 6. 监控配置

### 6.1 开启Grafana访问（可选）
编辑Nginx配置文件 `deploy/nginx/conf.d/emotion-ai.conf`，取消Grafana相关配置的注释：
```nginx
location /grafana/ {
    proxy_pass http://grafana:3000/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    # 访问控制，只允许特定IP访问
    allow 192.168.1.0/24;
    allow your-ip-address;
    deny all;
}
```

重启Nginx：
```bash
./deploy/scripts/manage.sh restart nginx
```

### 6.2 Grafana使用
- 访问地址: https://your-domain.com/grafana/
- 用户名: admin
- 密码: 你在.env文件中配置的GRAFANA_PASSWORD

### 6.3 配置告警
在Grafana中配置告警规则和通知渠道，支持：
- 邮件告警
- 企业微信/钉钉/飞书机器人
- 短信告警

---

## 7. 防火墙配置

### 7.1 UFW配置（Ubuntu）
```bash
# 启用UFW
ufw enable

# 允许必要端口
ufw allow 22/tcp    # SSH
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS

# 查看状态
ufw status
```

### 7.2 Firewalld配置（CentOS）
```bash
# 启动firewalld
systemctl start firewalld
systemctl enable firewalld

# 开放端口
firewall-cmd --permanent --add-port=22/tcp
firewall-cmd --permanent --add-port=80/tcp
firewall-cmd --permanent --add-port=443/tcp

# 重载配置
firewall-cmd --reload

# 查看状态
firewall-cmd --list-all
```

### 7.3 云服务商安全组
记得在云服务商控制台配置安全组，开放相应端口。

---

## 8. 安全加固

### 8.1 SSH安全配置
```bash
# 编辑SSH配置
vim /etc/ssh/sshd_config

# 修改以下配置
Port 22                           # 建议修改为非默认端口
PermitRootLogin no                # 禁止root用户登录
PasswordAuthentication no         # 禁止密码登录，使用密钥登录
PubkeyAuthentication yes          # 启用公钥认证

# 重启SSH服务
systemctl restart sshd
```

### 8.2 安装fail2ban防止暴力破解
```bash
apt install -y fail2ban
systemctl enable fail2ban
systemctl start fail2ban
```

### 8.3 定期安全更新
```bash
# 配置自动安全更新
apt install -y unattended-upgrades
dpkg-reconfigure unattended-upgrades
```

---

## 9. 验收标准

部署完成后，需满足以下验收标准：

✅ 所有服务正常运行，无异常退出
✅ 网站可以通过HTTPS正常访问
✅ SSL证书配置正确，浏览器显示安全锁
✅ 用户注册、登录、聊天功能正常
✅ 上传功能正常
✅ 数据库自动备份已配置
✅ SSL证书自动续期已配置
✅ 监控系统正常运行
✅ 防火墙配置正确，仅开放必要端口
✅ 系统资源使用正常（CPU<70%, 内存<70%, 磁盘<70%）
✅ 所有密码均为强密码，无默认密码
✅ 运维手册和故障排查文档齐全

---

## 10. 常见问题

### Q: 部署脚本运行失败怎么办？
A: 查看部署日志，日志位置在 `deploy/logs/` 目录下，根据错误信息修复问题后重新运行脚本。

### Q: SSL证书申请失败怎么办？
A: 检查以下几点：
1. 域名是否正确解析到服务器IP
2. 80端口是否开放，没有被防火墙拦截
3. 服务器是否可以访问公网
4. 邮箱地址是否正确

### Q: 如何修改配置？
A: 修改 `.env` 文件后，需要重启服务生效：
```bash
./deploy/scripts/manage.sh restart
```

### Q: 如何查看服务日志？
A: 使用管理脚本：
```bash
# 查看所有日志
./deploy/scripts/manage.sh logs

# 查看特定服务日志
./deploy/scripts/manage.sh logs backend
```

### Q: 如何备份数据？
A: 系统会自动每日备份，也可以手动备份：
```bash
./deploy/scripts/manage.sh backup
```

### Q: 如何升级版本？
A: 使用更新命令：
```bash
./deploy/scripts/manage.sh update
```

---

## 技术支持
- 运维手册: 参见 `OPERATION_MANUAL.md`
- 故障排查: 参见 `TROUBLESHOOTING_GUIDE.md`
- 技术支持: [联系邮箱/电话]

**部署完成后，请妥善保管好 .env 文件和备份数据！**
