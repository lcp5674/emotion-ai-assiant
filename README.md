# 心灵伴侣AI (Emotion AI Assistant)

一个基于MBTI人格测试的AI情感陪伴助手，使用RAG + 大模型技术提供个性化的情感支持。

## 项目概述

心灵伴侣AI是一个智能情感助手产品，核心功能包括：

- **MBTI人格测试**：专业48题MBTI测试，了解用户性格特点
- **AI情感对话**：基于用户MBTI类型，匹配个性化AI助手
- **RAG知识库**：结合心理学知识的智能问答
- **多模型支持**：预留OpenAI、Claude、GLM等多厂商接口

## 技术栈

### 后端
- Python 3.11+
- FastAPI - Web框架
- SQLAlchemy - ORM
- MySQL - 主数据库
- Redis - 缓存
- 大模型：OpenAI / Claude / GLM / Qwen / MiniMax
- 向量数据库：Milvus / Qdrant (可选)

### 前端
- React 18 + TypeScript
- Ant Design - UI组件库
- Zustand - 状态管理
- Vite - 构建工具
- React Router - 路由

## 快速开始

### 本地开发

#### 1. 克隆项目
```bash
git clone <repository-url>
cd emotion-ai-assistant
```

#### 2. 后端启动

```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 复制环境配置
cp .env.example .env
# 编辑 .env 配置数据库等信息

# 启动服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

后端服务启动后访问 http://localhost:8000/docs 查看API文档

#### 3. 前端启动

```bash
cd frontend/web

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端服务启动后访问 http://localhost:5173

### Docker部署

```bash
# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f
```

服务地址：
- 前端：http://localhost
- 后端API：http://localhost/api
- API文档：http://localhost/docs

## 项目结构

```
emotion-ai-assistant/
├── backend/                    # 后端服务
│   ├── app/
│   │   ├── api/               # API路由
│   │   │   └── v1/           # API v1版本
│   │   │       ├── auth.py   # 认证接口
│   │   │       ├── user.py   # 用户接口
│   │   │       ├── mbti.py   # MBTI测试接口
│   │   │       ├── chat.py   # 对话接口
│   │   │       ├── knowledge.py # 知识库接口
│   │   │       └── member.py # 会员接口
│   │   ├── core/              # 核心配置
│   │   │   ├── config.py      # 配置管理
│   │   │   ├── security.py    # 安全工具
│   │   │   └── database.py    # 数据库连接
│   │   ├── models/            # 数据模型
│   │   ├── schemas/           # Pydantic schemas
│   │   ├── services/          # 业务逻辑
│   │   │   ├── llm/           # 大模型服务
│   │   │   ├── rag/           # RAG服务
│   │   │   ├── mbti_service.py
│   │   │   └── chat_service.py
│   │   └── main.py            # 应用入口
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/                   # 前端应用
│   └── web/
│       ├── src/
│       │   ├── api/           # API调用
│       │   ├── components/    # 组件
│       │   ├── views/         # 页面
│       │   ├── router/        # 路由
│       │   └── stores/        # 状态管理
│       └── package.json
│
└── docker-compose.yml         # 容器编排
```

## 核心API

### 认证接口
- `POST /api/v1/auth/register` - 用户注册
- `POST /api/v1/auth/login` - 用户登录
- `POST /api/v1/auth/send_code` - 发送验证码
- `GET /api/v1/auth/me` - 获取当前用户

### MBTI接口
- `GET /api/v1/mbti/questions` - 获取测试题目
- `POST /api/v1/mbti/start` - 开始测试
- `POST /api/v1/mbti/submit` - 提交答案
- `GET /api/v1/mbti/result` - 获取结果
- `GET /api/v1/mbti/assistants` - 获取AI助手列表

### 对话接口
- `POST /api/v1/chat/send` - 发送消息
- `GET /api/v1/chat/conversations` - 对话列表
- `GET /api/v1/chat/history/{session_id}` - 对话历史

### 知识库接口
- `GET /api/v1/knowledge/articles` - 文章列表
- `GET /api/v1/knowledge/articles/{id}` - 文章详情
- `GET /api/v1/knowledge/banners` - Banner列表

## 配置说明

### 大模型配置

在 `.env` 文件中配置：

```env
# 使用模拟服务 (开发测试)
LLM_PROVIDER=mock

# 或使用 OpenAI
LLM_PROVIDER=openai
OPENAI_API_KEY=your-api-key

# 或使用 Anthropic Claude
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=your-api-key

# 或使用智谱GLM
LLM_PROVIDER=glm
GLM_API_KEY=your-api-key

# 或使用阿里通义千问
LLM_PROVIDER=qwen
QWEN_API_KEY=your-api-key
```

## 功能特性

### 已实现
- ✅ 用户注册登录 (手机号 + 验证码)
- ✅ JWT认证
- ✅ MBTI 48题测试
- ✅ MBTI结果计算与报告
- ✅ AI助手匹配推荐
- ✅ AI对话 (RAG + 大模型)
- ✅ 知识库文章
- ✅ 会员系统 (基础)
- ✅ Docker部署

### 规划中
- ⏳ WebSocket实时对话
- ⏳ 情感日记功能
- ⏳ 语音输入/播报
- ⏳ 完整支付流程
- ⏳ 管理后台

## 开发指南

### 添加新的API

1. 在 `app/api/v1/` 下创建或修改路由文件
2. 定义Pydantic Schema (在 `app/schemas/`)
3. 实现业务逻辑 (在 `app/services/`)

### 添加新的大模型Provider

1. 在 `app/services/llm/providers/` 创建新Provider类
2. 实现 `chat` 和 `chat_stream` 方法
3. 在 `PROVIDER_MAP` 中注册

## 许可证

MIT License