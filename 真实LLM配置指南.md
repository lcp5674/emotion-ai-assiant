# 使用真实大模型 API 配置指南

## 🔥 支持的大模型提供商

项目支持以下大模型 API，选择一个即可：

| 提供商 | 模型 | 特点 | 推荐场景 |
|--------|------|------|----------|
| **OpenAI** | GPT-3.5/GPT-4 | 性能强，全球最常用 | 通用对话 |
| **Anthropic** | Claude 3 | 长文本处理强，适合情感支持 | 情感陪伴 |
| **智谱 GLM** | GLM-4 | 中文优化好 | 中文场景 |
| **通义千问** | Qwen | 阿里自研，中文能力强 | 中文场景 |
| **腾讯混元** | Hunyuan | 腾讯自研 | 中文场景 |
| **百度文心** | ERNIE-4.0 | 百度自研 | 中文场景 |
| **讯飞星火** | Spark | 语音交互强 | 对话场景 |
| **字节豆包** | Doubao | 字节自研 | 对话场景 |
| **MiniMax** | abab5.5 | 海螺AI同款 | 对话场景 |

---

## 📝 配置步骤

### 步骤 1: 获取 API Key

#### OpenAI（GPT）
1. 访问 https://platform.openai.com/
2. 注册/登录账号
3. 进入 API Keys 页面
4. 创建新的 API Key
5. 建议设置使用额度限制

#### Anthropic（Claude）
1. 访问 https://console.anthropic.com/
2. 注册/登录账号
3. 进入 API Keys 页面
4. 创建新的 API Key

#### 智谱 GLM（推荐国内用户）
1. 访问 https://open.bigmodel.cn/
2. 注册/登录账号
3. 进入控制台
4. 创建 API Key

#### 通义千问（推荐国内用户）
1. 访问 https://dashscope.console.aliyun.com/
2. 注册/登录阿里云账号
3. 开通 DashScope 服务
4. 创建 API Key

#### 腾讯混元
1. 访问 https://console.cloud.tencent.com/hunyuan
2. 注册/登录腾讯云账号
3. 开通混元大模型服务
4. 创建 API Key

#### 百度文心
1. 访问 https://console.bce.baidu.com/
2. 注册/登录百度智能云账号
3. 开通文心一言服务
4. 创建 API Key

---

### 步骤 2: 创建配置文件

在 `backend` 目录下创建或编辑 `.env` 文件：

```bash
cd backend
cat > .env << 'EOF'
# 应用配置
APP_NAME=心灵伴侣AI
APP_VERSION=1.0.0
DEBUG=true

# 服务器
HOST=0.0.0.0
PORT=8000

# 数据库（轻量测试使用 SQLite）
DATABASE_URL=sqlite:///./emotion_ai.db

# Redis（开发环境可选）
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0

# JWT
SECRET_KEY=dev-secret-key-change-in-production-1234567890
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# ============================
# 大模型配置（选择其中一个）
# ============================

# 【方案1】OpenAI GPT（推荐国际用户）
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_MODEL=gpt-3.5-turbo  # 或 gpt-4

# 【方案2】Anthropic Claude（推荐情感陪伴）
# LLM_PROVIDER=anthropic
# ANTHROPIC_API_KEY=sk-ant-your-api-key-here
# ANTHROPIC_MODEL=claude-3-haiku-20240307  # 或 claude-3-sonnet-20240229

# 【方案3】智谱 GLM（推荐国内用户）
# LLM_PROVIDER=glm
# GLM_API_KEY=your-glm-api-key-here
# GLM_MODEL=glm-4

# 【方案4】通义千问（推荐国内用户）
# LLM_PROVIDER=qwen
# QWEN_API_KEY=your-qwen-api-key-here
# QWEN_MODEL=qwen-turbo

# 【方案5】腾讯混元
# LLM_PROVIDER=hunyuan
# HUNYUAN_API_KEY=your-hunyuan-api-key-here
# HUNYUAN_MODEL=hunyuan-pro

# 【方案6】百度文心
# LLM_PROVIDER=ernie
# ERNIE_API_KEY=your-ernie-api-key-here
# ERNIE_MODEL=ernie-4.0-8k

# ============================
# 其他配置
# ============================

# CORS
CORS_ORIGINS=["http://localhost:5173","http://localhost:3000"]
EOF
```

---

## 🎯 推荐配置

### 方案 1: OpenAI（国际用户）

```bash
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-api-key
OPENAI_MODEL=gpt-3.5-turbo  # 推荐，支持流式输出
```

**优势**: 
- 性能最强
- 支持流式输出
- 生态系统完善

**费用**: 
- GPT-3.5: $0.002/1K tokens（非常便宜）
- GPT-4: $0.03/1K tokens（较贵）

---

### 方案 2: 智谱 GLM（国内用户首选）

```bash
LLM_PROVIDER=glm
GLM_API_KEY=your-api-key
GLM_MODEL=glm-4
```

**优势**:
- 中文理解能力强
- 价格便宜
- 国内访问速度快
- 支持流式输出

**费用**: 
- GLM-4: ¥0.1/千tokens（性价比高）

---

### 方案 3: 通义千问（国内用户）

```bash
LLM_PROVIDER=qwen
QWEN_API_KEY=your-api-key
QWEN_MODEL=qwen-turbo
```

**优势**:
- 阿里自研，技术实力强
- 中文能力优秀
- 价格实惠
- 国内访问速度快

**费用**: 
- Qwen-turbo: ¥0.008/千tokens（非常便宜）

---

## 🧪 验证配置

### 1. 启动后端

```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. 测试 API

打开浏览器访问 API 文档：http://localhost:8000/docs

测试对话接口：

```bash
curl -X POST http://localhost:8000/api/v1/chat/send \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "content": "你好，今天心情不错",
    "assistant_id": 1
  }'
```

### 3. 检查日志

如果出现 LLM 相关错误，查看日志：

```bash
tail -f logs/backend.log
```

常见错误：
- `API key invalid`: API Key 错误或未设置
- `rate limit exceeded`: 请求频率超限
- `model not found`: 模型名称错误

---

## 💡 性能优化建议

### 1. 使用流式输出（推荐）

所有支持的模型都支持流式输出，可以提升用户体验：

```json
{
  "stream": true
}
```

### 2. 选择合适的模型

| 场景 | 推荐模型 | 原因 |
|------|----------|------|
| 开发测试 | GPT-3.5 / GLM-3 | 便宜、快速 |
| 生产环境 | GPT-4 / GLM-4 | 性能强 |
| 情感对话 | Claude 3 | 理解能力强 |
| 中文场景 | GLM-4 / Qwen | 中文优化好 |

### 3. 控制 token 数量

在 `.env` 中设置最大 token 数：

```bash
MAX_TOKENS=2000  # 最大回复长度
```

### 4. 使用缓存

启用 Redis 缓存可以减少 API 调用：

```bash
REDIS_HOST=localhost
REDIS_PORT=6379
```

---

## 🔒 安全注意事项

### 1. 保护 API Key

```bash
# 不要提交到 Git
echo ".env" >> .gitignore

# 使用环境变量
export OPENAI_API_KEY=sk-your-key
```

### 2. 设置使用限额

在各大平台设置 API 使用限额，避免超额扣费：

- OpenAI: https://platform.openai.com/account/billing/limits
- 智谱: 控制台设置
- 通义千问: 控制台设置

### 3. 监控使用量

定期检查 API 使用量：

```bash
# OpenAI
curl https://api.openai.com/v1/usage \
  -H "Authorization: Bearer YOUR_API_KEY"
```

---

## 📊 费用对比

| 模型 | 输入费用 | 输出费用 | 相对成本 |
|------|----------|----------|----------|
| GPT-3.5-turbo | $0.0015/1K | $0.002/1K | 1x |
| GPT-4 | $0.03/1K | $0.06/1K | 20x |
| Claude 3 Haiku | $0.00025/1K | $0.00125/1K | 0.8x |
| GLM-4 | ¥0.1/千tokens | ¥0.1/千tokens | ~$0.014/1K |
| Qwen-turbo | ¥0.008/千tokens | ¥0.008/千tokens | ~$0.001/1K |

---

## 🚀 快速启动（国内用户）

推荐使用 **智谱 GLM** 或 **通义千问**：

```bash
# 1. 获取 API Key（免费额度）
# 智谱: https://open.bigmodel.cn/
# 通义: https://dashscope.console.aliyun.com/

# 2. 编辑 backend/.env
nano backend/.env

# 3. 取消注释对应的配置
LLM_PROVIDER=glm  # 或 qwen
GLM_API_KEY=your-key  # 或 QWEN_API_KEY

# 4. 重启服务
./scripts/dev.sh restart

# 5. 测试对话
curl -X POST http://localhost:8000/api/v1/chat/send \
  -H "Content-Type: application/json" \
  -d '{"content": "你好", "assistant_id": 1}'
```

---

## ❓ 常见问题

### Q1: API Key 如何获取？

查看各大平台官方文档，通常需要：
1. 注册账号
2. 实名认证
3. 开通服务
4. 创建 API Key

### Q2: 如何切换不同模型？

修改 `.env` 文件中的配置：

```bash
# 切换到智谱
LLM_PROVIDER=glm
GLM_API_KEY=your-key

# 切换到 OpenAI
LLM_PROVIDER=openai
OPENAI_API_KEY=your-key
```

重启服务即可生效。

### Q3: API 调用失败怎么办？

1. 检查 API Key 是否正确
2. 检查网络连接
3. 查看日志：`tail -f logs/backend.log`
4. 确认账户余额充足

### Q4: 如何降低费用？

1. 使用更便宜的模型（如 GPT-3.5）
2. 减少 token 数量
3. 启用缓存（Redis）
4. 设置每日使用限额

### Q5: 支持语音对话吗？

讯飞 Spark 模型支持语音识别和合成，可以实现语音对话。

---

## 🎉 开始使用

按照以上配置完成后，你的 Emotion AI Assistant 就可以使用真实的大模型进行智能对话了！

推荐顺序：
1. **开发测试**: 智谱 GLM / 通义千问（便宜、快速）
2. **生产环境**: 根据需求选择 OpenAI GPT-4 / Claude 3 / GLM-4

祝使用愉快！🌟
