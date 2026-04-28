# AI情感助手 (Emotion AI Assistant)

一个基于MBTI人格测试的AI情感陪伴助手，使用RAG + 大模型技术提供个性化的情感支持。

## 项目概述

### 核心功能

| 模块 | 功能 | 状态 |
|------|------|------|
| MBTI测评 | 48题人格测试 | ✅ 已完成 |
| SBTI测评 | 34主题情感风格测试 | ✅ 已完成 |
| 依恋风格 | 10题依恋类型评估 | ✅ 已完成 |
| 深度画像 | 三维人格综合分析 | ✅ 已完成 |
| AI对话 | RAG增强智能回复 | ✅ 已完成 |
| 数据质量 | 时效性/完整性/一致性保障 | ✅ 已完成 |

### 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | React 18 + TypeScript + Ant Design + Zustand |
| 后端 | FastAPI + SQLAlchemy + MySQL + Redis |
| AI | RAG知识库 + LLM (OpenAI/Claude/GLM/Qwen) |
| 部署 | Docker Compose + Nginx |

## 快速开始

### Docker部署 (推荐)

```bash
# 克隆项目
git clone https://github.com/lcp5674/emotion-ai-assiant.git
cd emotion-ai-assiant

# 配置环境
cp .env.docker.example .env.docker
# 编辑 .env.docker 填入必要配置

# 一键部署
chmod +x deploy/deploy.sh
./deploy/deploy.sh
```

### 访问地址

| 服务 | 地址 |
|------|------|
| 前端 | http://localhost |
| 后端API | http://localhost/api/v1/health |
| API文档 | http://localhost/docs |

## 项目结构

```
emotion-ai-assiant/
├── backend/                    # 后端服务
│   ├── app/
│   │   ├── api/v1/           # API路由
│   │   ├── models/           # 数据模型
│   │   ├── schemas/          # Pydantic模型
│   │   ├── services/         # 业务服务
│   │   └── services/rag/     # RAG服务
│   └── tests/                # 测试 (56个文件)
├── frontend/web/              # 前端应用
│   ├── src/
│   │   ├── api/             # API调用
│   │   ├── stores/          # 状态管理
│   │   └── views/           # 页面组件
│   └── package.json
├── deploy/                    # 部署脚本 (8个脚本)
│   ├── deploy.sh            # 一键部署
│   ├── health_check.sh      # 健康检查
│   ├── backup.sh            # 数据库备份
│   └── ...
└── docker-compose.yml
```

## 核心API

### 测评模块

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/v1/sbti/questions` | GET | 获取SBTI题目 |
| `/api/v1/sbti/submit` | POST | 提交SBTI答案 |
| `/api/v1/sbti/result` | GET | 获取SBTI结果 |
| `/api/v1/attachment/questions` | GET | 获取依恋题目 |
| `/api/v1/attachment/submit` | POST | 提交依恋答案 |
| `/api/v1/profile/deep` | GET | 获取深度画像 |
| `/api/v1/profile/ai-partners` | GET | 获取AI伴侣推荐 |

### AI服务

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/v1/chat/send` | POST | 发送消息 |
| `/api/v1/chat/history` | GET | 对话历史 |
| `/api/v1/quality/score` | GET | 数据质量评分 |

## 文档导航

| 文档 | 说明 |
|------|------|
| [项目概览与需求.md](./项目概览与需求.md) | 产品需求、功能矩阵、实现报告 |
| [部署与运维指南.md](./部署与运维指南.md) | Docker部署、架构、备份恢复 |
| [商用化指南.md](./商用化指南.md) | 需求分析、Roadmap、准备清单 |
| [合规文档.md](./合规文档.md) | 隐私政策、用户协议、合规说明 |
| [测试与质量保障.md](./测试与质量保障.md) | 测试计划、用例、质量检查 |
| [项目总结报告.md](./项目总结报告.md) | 项目概述、架构、质量指标 |
| [运维支持手册.md](./运维支持手册.md) | 日常检查、故障处理、运维脚本 |

## 运维命令

```bash
# 部署
./deploy/deploy.sh

# 健康检查
./deploy/health_check.sh

# 查看日志
./deploy/logs.sh backend 100

# 数据库备份
./deploy/backup.sh

# 重启服务
./deploy/restart.sh backend
```

## 功能特性

### 已完成

- ✅ 用户注册登录 (手机号 + 验证码)
- ✅ JWT认证
- ✅ MBTI 48题测试
- ✅ SBTI 34主题测试
- ✅ 依恋风格测试
- ✅ 深度人格画像
- ✅ AI对话 (RAG + 大模型)
- ✅ 危机内容检测与转介
- ✅ 数据质量保障体系
- ✅ 一键Docker部署

### 开发中

- 🔄 微信支付集成
- 🔄 会员订阅系统
- 🔄 运营后台

## 许可证

MIT License
