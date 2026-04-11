#!/bin/bash
set -e

# SSL证书自动配置脚本
# 使用Let's Encrypt自动颁发和续期证书

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$PROJECT_ROOT"

# 加载环境变量
if [ ! -f ".env" ]; then
    echo -e "${RED}错误: 未找到 .env 文件，请先运行部署脚本${NC}"
    exit 1
fi
source .env

echo -e "${GREEN}=============================================${NC}"
echo -e "${GREEN}SSL证书自动配置脚本${NC}"
echo -e "${GREEN}=============================================${NC}"
echo ""

# 检查必要配置
if [ -z "$DOMAIN" ] || [ "$DOMAIN" == "your-domain.com" ]; then
    echo -e "${RED}错误: 请在 .env 文件中配置 DOMAIN 为您的实际域名${NC}"
    exit 1
fi

if [ -z "$SSL_EMAIL" ] || [ "$SSL_EMAIL" == "your-email@example.com" ]; then
    echo -e "${RED}错误: 请在 .env 文件中配置 SSL_EMAIL 为您的邮箱地址${NC}"
    exit 1
fi

echo -e "${YELLOW}域名: ${DOMAIN}${NC}"
echo -e "${YELLOW}邮箱: ${SSL_EMAIL}${NC}"
echo ""

# 检查80端口是否开放
echo -e "${YELLOW}检查80端口是否开放...${NC}"
if ! curl -s "http://${DOMAIN}/.well-known/ping" --connect-timeout 5 > /dev/null; then
    echo -e "${YELLOW}⚠️  无法访问80端口，请确保:${NC}"
    echo -e "  1. 域名 ${DOMAIN} 已解析到本服务器IP"
    echo -e "  2. 防火墙已开放80端口"
    echo -e "  3. Nginx服务正在运行"
    read -p "确认已完成上述配置？(y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# 安装certbot
echo -e "${YELLOW}1. 安装Certbot...${NC}"
if ! command -v certbot &> /dev/null; then
    if command -v apt-get &> /dev/null; then
        apt-get update
        apt-get install -y certbot
    elif command -v yum &> /dev/null; then
        yum install -y certbot
    else
        echo -e "${RED}错误: 无法自动安装Certbot，请手动安装${NC}"
        exit 1
    fi
fi
echo -e "${GREEN}✓ Certbot 安装完成${NC}"
echo ""

# 创建ACME挑战目录
echo -e "${YELLOW}2. 创建ACME挑战目录...${NC}"
mkdir -p /var/www/acme
chown -R www-data:www-data /var/www/acme
echo -e "${GREEN}✓ ACME目录创建完成${NC}"
echo ""

# 颁发证书
echo -e "${YELLOW}3. 申请SSL证书...${NC}"
certbot certonly --webroot -w /var/www/acme \
    -d "${DOMAIN}" \
    --email "${SSL_EMAIL}" \
    --agree-tos \
    --non-interactive \
    --expand

if [ ! -f "/etc/letsencrypt/live/${DOMAIN}/fullchain.pem" ]; then
    echo -e "${RED}错误: 证书颁发失败${NC}"
    exit 1
fi
echo -e "${GREEN}✓ SSL证书颁发成功${NC}"
echo ""

# 复制证书到项目目录
echo -e "${YELLOW}4. 复制证书到项目目录...${NC}"
mkdir -p "deploy/ssl/live/${DOMAIN}"
cp -L /etc/letsencrypt/live/${DOMAIN}/fullchain.pem "deploy/ssl/live/${DOMAIN}/"
cp -L /etc/letsencrypt/live/${DOMAIN}/privkey.pem "deploy/ssl/live/${DOMAIN}/"
chmod -R 600 "deploy/ssl/live/${DOMAIN}/"
echo -e "${GREEN}✓ 证书复制完成${NC}"
echo ""

# 生成HTTPS配置
echo -e "${YELLOW}5. 生成HTTPS配置...${NC}"
# 替换模板变量
sed "s/\${DOMAIN}/${DOMAIN}/g" deploy/nginx/conf.d/emotion-ai.https.conf.template > deploy/nginx/conf.d/emotion-ai.conf
# 删除HTTP配置
rm -f deploy/nginx/conf.d/emotion-ai.http.conf
echo -e "${GREEN}✓ HTTPS配置生成完成${NC}"
echo ""

# 重启Nginx服务
echo -e "${YELLOW}6. 重启Nginx服务...${NC}"
docker-compose -f docker-compose.prod.yml restart nginx

# 等待Nginx重启
sleep 5

# 验证HTTPS
echo -e "${YELLOW}7. 验证HTTPS配置...${NC}"
if curl -s "https://${DOMAIN}/health" --connect-timeout 10 | grep -q "ok"; then
    echo -e "${GREEN}✓ HTTPS配置验证通过${NC}"
else
    echo -e "${RED}错误: HTTPS配置验证失败，请检查Nginx日志${NC}"
    exit 1
fi
echo ""

# 配置自动续期
echo -e "${YELLOW}8. 配置证书自动续期...${NC}"
# 添加续期钩子
cat > /etc/letsencrypt/renewal-hooks/post/deploy-emotion-ai.sh << EOF
#!/bin/bash
# SSL证书续期后自动部署到AI情感助手
cp -L /etc/letsencrypt/live/${DOMAIN}/fullchain.pem ${PROJECT_ROOT}/deploy/ssl/live/${DOMAIN}/
cp -L /etc/letsencrypt/live/${DOMAIN}/privkey.pem ${PROJECT_ROOT}/deploy/ssl/live/${DOMAIN}/
chmod -R 600 ${PROJECT_ROOT}/deploy/ssl/live/${DOMAIN}/
docker-compose -f ${PROJECT_ROOT}/docker-compose.prod.yml restart nginx
EOF

chmod +x /etc/letsencrypt/renewal-hooks/post/deploy-emotion-ai.sh

# 测试自动续期
certbot renew --dry-run

echo -e "${GREEN}✓ 自动续期配置完成${NC}"
echo ""

# 完成提示
echo -e "${GREEN}=============================================${NC}"
echo -e "${GREEN}✅ SSL证书配置完成！${NC}"
echo -e "${GREEN}=============================================${NC}"
echo ""
echo -e "${YELLOW}访问地址: https://${DOMAIN}${NC}"
echo ""
echo -e "${YELLOW}证书信息:${NC}"
echo -e "  证书路径: /etc/letsencrypt/live/${DOMAIN}/"
echo -e "  有效期: 90天，系统会自动续期"
echo -e "  续期检查: 每天自动运行2次${NC}"
echo ""
echo -e "${GREEN}HTTPS已成功配置，您的网站现在可以安全访问了！${NC}"
