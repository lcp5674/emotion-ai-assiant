# macOS 本地部署指南（无需 Docker）

## 📋 前置条件

### 1. 检查系统工具

首先检查是否已安装必要的工具：

```bash
# 检查 Python
python3 --version

# 检查 Node.js
node --version

# 检查 npm
npm --version

# 检查 Homebrew
brew --version
```

### 2. 安装缺失工具

如果系统缺少工具，按以下顺序安装：

#### 2.1 安装 Homebrew（如果没有）

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

#### 2.2 安装 Python 3.10+

```bash
brew install python@3.10
python3 --version  # 确认版本
```

#### 2.3 安装 Node.js 18+

```bash
brew install node@18
node --version  # 确认版本
```

---

## 🚀 快速开始（推荐方式）

项目已经提供了完整的开发环境脚本，只需一条命令即可启动所有服务：

```bash
# 进入项目目录
cd /System/Volumes/Data/data/GitCode/emotion-ai-assiant

# 赋予执行权限
chmod +x scripts/dev.sh

# 启动所有服务（会提示输入密码）
./scripts/dev.sh start
```

### 脚本功能

| 命令 | 说明 |
|------|------|
| `./dev.sh start` | 启动所有服务 |
| `./dev.sh stop` | 停止所有服务 |
| `./dev.sh restart` | 重启所有服务 |
| `./dev.sh status` | 查看服务状态 |
| `./dev.sh logs` | 查看日志 |
| `./dev.sh clean` | 清理环境 |

---

## 📝 详细安装步骤（可选）

如果上述快速开始失败，按以下步骤手动部署：

### 步骤 1: 创建 Python 虚拟环境

```bash
cd backend

# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 升级 pip
pip install --upgrade pip
```

### 步骤 2: 安装后端依赖

```bash
# 安装依赖（可能需要几分钟）
pip install -r requirements.txt
```

**注意**: 如果遇到安装错误，尝试：
```bash
# 对于 macOS ARM 芯片，可能需要安装编译工具
xcode-select --install

# 对于某些包安装失败，可以尝试
pip install -r requirements.txt --no-cache-dir
```

### 步骤 3: 安装前端依赖

```bash
cd frontend/web

# 安装依赖
npm install
```

### 步骤 4: 配置环境变量

创建配置文件：

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

# Redis（可选，开发环境可跳过）
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0

# JWT
SECRET_KEY=dev-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# 大模型（使用 Mock）
LLM_PROVIDER=mock

# 向量数据库（使用内存）
VECTOR_DB_TYPE=memory

# CORS
CORS_ORIGINS=["http://localhost:5173","http://localhost:3000"]
EOF
```

### 步骤 5: 初始化数据库

```bash
# 激活虚拟环境
source venv/bin/activate

# 尝试运行数据库迁移（如果需要）
alembic upgrade head

# 或者创建表（如果使用 SQLite）
python -c "from app.core.database import init_db; init_db()"
```

### 步骤 6: 启动后端服务

```bash
# 激活虚拟环境
source venv/bin/activate

# 启动服务（开发模式）
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 步骤 7: 启动前端服务

新开一个终端窗口：

```bash
cd frontend/web

# 启动开发服务器
npm run dev
```

---

## 🎯 访问应用

启动成功后，在浏览器中访问：

| 服务 | 地址 |
|------|------|
| 前端页面 | http://localhost:5173 |
| 后端 API | http://localhost:8000 |
| API 文档 | http://localhost:8000/docs |
| 健康检查 | http://localhost:8000/health |

---

## 🧪 测试功能

### 1. 健康检查

```bash
curl http://localhost:8000/health
```

### 2. 发送验证码（登录测试）

```bash
curl -X POST http://localhost:8000/api/v1/auth/send_code \
  -H "Content-Type: application/json" \
  -d '{"phone": "13800138000"}'
```

### 3. 注册测试

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "13800138000",
    "password": "Test123456",
    "code": "123456",
    "nickname": "测试用户"
  }'
```

---

## 🔧 常见问题排查

### 问题 1: 端口被占用

```bash
# 查找占用端口的进程
lsof -i:8000
lsof -i:5173

# 杀死进程
kill -9 <PID>
```

### 问题 2: Python 包安装失败

```bash
# 更新 pip
pip install --upgrade pip

# 尝试安装单个包
pip install <package-name>

# 使用国内镜像
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
```

### 问题 3: Node.js 包安装失败

```bash
# 清理缓存
npm cache clean --force

# 重新安装
rm -rf node_modules
npm install

# 使用国内镜像
npm config set registry https://registry.npmmirror.com
npm install
```

### 问题 4: 数据库连接错误

```bash
# 确保使用 SQLite
export DATABASE_URL=sqlite:///./emotion_ai.db

# 或者创建数据库文件
touch emotion_ai.db
```

### 问题 5: Redis 连接错误

对于开发环境，可以忽略 Redis 或使用内存模拟：

```bash
# 在 .env 中设置
REDIS_HOST=localhost
REDIS_PORT=6379
# 注释掉或留空
# REDIS_PASSWORD=
```

---

## 📊 环境配置说明

### 开发模式配置（轻量）

```bash
# 数据库
DATABASE_URL=sqlite:///./emotion_ai.db

# Redis（可选）
REDIS_HOST=localhost
REDIS_PORT=6379

# LLM（使用 Mock）
LLM_PROVIDER=mock

# 向量数据库（使用内存）
VECTOR_DB_TYPE=memory
```

### 生产模式配置（需要 MySQL + Redis）

```bash
# 数据库
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=emotion_ai
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/emotion_ai

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your_password

# LLM（使用真实 API）
LLM_PROVIDER=openai  # 或 anthropic/glm/qwen
OPENAI_API_KEY=your_api_key
```

---

## 🎨 前端开发

### 开发模式

```bash
cd frontend/web

# 启动开发服务器（热重载）
npm run dev

# 构建生产版本
npm run build

# 预览生产版本
npm run preview
```

### 可用脚本

| 命令 | 说明 |
|------|------|
| `npm run dev` | 启动开发服务器 |
| `npm run build` | 构建生产版本 |
| `npm run preview` | 预览生产版本 |
| `npm run lint` | 代码检查 |
| `npm run format` | 代码格式化 |

---

## 🛠️ 后端开发

### 开发模式

```bash
cd backend
source venv/bin/activate

# 启动服务器（热重载）
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 运行测试
pytest tests/ -v

# 代码检查
flake8 app/
```

### 可用命令

| 命令 | 说明 |
|------|------|
| `uvicorn app.main:app --reload` | 启动开发服务器 |
| `pytest tests/ -v` | 运行测试 |
| `alembic upgrade head` | 数据库迁移 |
| `alembic revision --autogenerate` | 创建迁移 |

---

## 📚 其他资源

### API 文档

启动服务后访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 项目文档

- 架构审查报告: `架构审查报告.md`
- 项目概览: `项目概览与需求.md`
- 测试指南: `测试与质量保障.md`

---

## 🎉 完成！

现在你已经成功在 macOS 上部署了 Emotion AI Assistant 项目。可以开始：

1. 🌐 访问前端页面进行 UI 测试
2. 📡 使用 API 文档进行接口测试
3. 💻 进行功能开发和调试
4. 🧪 运行单元测试

祝你开发愉快！🎨
