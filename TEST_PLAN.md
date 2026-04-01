# 心灵伴侣AI - 测试计划

**文档版本**: V1.0
**编制日期**: 2026-03-31
**状态**: 待执行

---

## 目录

1. [测试概述](#1-测试概述)
2. [测试策略](#2-测试策略)
3. [测试环境](#3-测试环境)
4. [单元测试](#4-单元测试)
5. [集成测试](#5-集成测试)
6. [端到端测试](#6-端到端测试)
7. [性能测试](#7-性能测试)
8. [安全测试](#8-安全测试)
9. [兼容性测试](#9-兼容性测试)
10. [测试执行计划](#10-测试执行计划)

---

## 1. 测试概述

### 1.1 测试目标

- 确保核心功能正确实现
- 验证系统安全性和稳定性
- 保证性能满足商用要求
- 达到企业级系统质量标准

### 1.2 测试范围

| 模块 | 优先级 | 测试深度 |
|------|--------|----------|
| 用户认证 | P0 | 完整 |
| MBTI测试 | P0 | 完整 |
| AI对话 | P0 | 完整 |
| 情感日记 | P1 | 基本 |
| 知识库 | P1 | 基本 |
| 会员系统 | P1 | 基本 |
| 管理后台 | P1 | 基本 |

### 1.3 质量标准

| 指标 | 目标值 |
|------|--------|
| 单元测试覆盖率 | ≥85% |
| 集成测试通过率 | 100% |
| 关键API响应时间 | <2s (P50), <3s (P99) |
| 并发用户支持 | ≥1000 |
| 安全漏洞 | 0高危, 0中危 |

---

## 2. 测试策略

### 2.1 测试金字塔

```
        /\
       /E2E\        10% - 端到端测试
      /------\
     /集成测试\     30% - 集成测试
    /----------\
   /  单元测试   \   60% - 单元测试
  /--------------\
```

### 2.2 测试工具选型

| 测试类型 | 工具 |
|----------|------|
| 后端单元测试 | pytest |
| 后端API测试 | pytest + httpx |
| 前端单元测试 | Vitest |
| 前端组件测试 | React Testing Library |
| E2E测试 | Playwright |
| 性能测试 | Locust |
| 安全测试 | OWASP ZAP, Bandit |

---

## 3. 测试环境

### 3.1 环境配置

```yaml
# 测试环境 docker-compose.test.yml
version: '3.8'

services:
  mysql_test:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: test_root
      MYSQL_DATABASE: emotion_ai_test
    tmpfs:
      - /var/lib/mysql
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 5s
      timeout: 5s
      retries: 10

  redis_test:
    image: redis:7-alpine
    tmpfs:
      - /data
```

### 3.2 测试配置

```python
# backend/tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.database import Base, get_db
from app.core.config import settings

# 使用SQLite内存数据库进行测试
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function")
def db_session():
    """数据库会话fixture"""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """测试客户端fixture"""
    def _get_db_override():
        yield db_session

    app.dependency_overrides[get_db] = _get_db_override
    return TestClient(app)


@pytest.fixture
def test_user(db_session):
    """测试用户fixture"""
    from app.models import User
    from app.core.security import get_password_hash

    user = User(
        phone="13800138000",
        nickname="测试用户",
        password_hash=get_password_hash("Test@123456"),
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def auth_headers(client, test_user):
    """认证token fixture"""
    response = client.post("/api/v1/auth/login", json={
        "phone": "13800138000",
        "password": "Test@123456"
    })
    data = response.json()
    return {"Authorization": f"Bearer {data['access_token']}"}
```

---

## 4. 单元测试

### 4.1 后端单元测试结构

```
backend/tests/
├── conftest.py
├── fixtures/
│   ├── __init__.py
│   ├── user.py
│   ├── mbti.py
│   └── chat.py
├── unit/
│   ├── __init__.py
│   ├── test_security.py
│   ├── test_mbti_service.py
│   ├── test_chat_service.py
│   ├── test_member_service.py
│   ├── test_content_filter.py
│   └── test_llm_factory.py
├── integration/
│   ├── __init__.py
│   ├── test_api_auth.py
│   ├── test_api_mbti.py
│   ├── test_api_chat.py
│   ├── test_api_diary.py
│   └── test_api_admin.py
└── e2e/
    └── test_user_journey.py
```

### 4.2 核心单元测试用例

#### 4.2.1 安全工具测试

```python
# backend/tests/unit/test_security.py
import pytest
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_token,
    generate_verify_code,
    mask_phone,
)


def test_password_hash_and_verify():
    """测试密码哈希和验证"""
    password = "Test@123456"
    hashed = get_password_hash(password)

    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("WrongPassword", hashed)


def test_access_token_creation_and_validation():
    """测试访问令牌创建和验证"""
    data = {"sub": "1"}
    token = create_access_token(data)

    payload = verify_token(token)
    assert payload["sub"] == "1"
    assert payload["type"] == "access"


def test_refresh_token_creation_and_validation():
    """测试刷新令牌创建和验证"""
    data = {"sub": "1"}
    token = create_refresh_token(data)

    payload = decode_token(token)
    assert payload["sub"] == "1"
    assert payload["type"] == "refresh"


def test_invalid_token_validation():
    """测试无效令牌验证"""
    from fastapi import HTTPException

    with pytest.raises(HTTPException):
        verify_token("invalid.token.here")


def test_verify_code_generation():
    """测试验证码生成"""
    code = generate_verify_code(6)
    assert len(code) == 6
    assert code.isdigit()


def test_phone_masking():
    """测试手机号脱敏"""
    assert mask_phone("13800138000") == "138****8000"
    assert mask_phone("12345") == "12345"  # 不足11位不处理
```

#### 4.2.2 MBTI服务测试

```python
# backend/tests/unit/test_mbti_service.py
import pytest
from app.services.mbti_service import MbtiService, seed_assistants
from app.models.mbti import MbtiType


def test_mbti_question_seeding(db_session):
    """测试MBTI题目初始化"""
    service = MbtiService()
    service.seed_questions(db_session, force=True)

    questions = service.get_questions(db_session)
    assert len(questions) == 48

    # 验证各维度题目数量
    ei_questions = service.get_questions(db_session, dimension="EI")
    assert len(ei_questions) == 12


def test_mbti_result_calculation(db_session):
    """测试MBTI结果计算"""
    service = MbtiService()
    service.seed_questions(db_session, force=True)

    questions = service.get_questions(db_session)

    # 构建答案 - 全部选A
    answers = [
        {"question_id": q.id, "answer": "A"}
        for q in questions
    ]

    result = service.calculate_result(db_session, user_id=1, answers=answers)

    assert "mbti_type" in result
    assert result["mbti_type"] in [t.value for t in MbtiType]
    assert "ei_score" in result
    assert "sn_score" in result
    assert "tf_score" in result
    assert "jp_score" in result
    assert "personality" in result
    assert "strengths" in result


def test_assistant_seeding(db_session):
    """测试AI助手初始化"""
    seed_assistants(db_session)

    from app.models import AiAssistant
    assistants = db_session.query(AiAssistant).all()
    assert len(assistants) >= 8


def test_recommended_assistants(db_session):
    """测试推荐助手获取"""
    from app.services.mbti_service import seed_assistants
    seed_assistants(db_session)

    service = MbtiService()
    assistants = service.get_recommended_assistants(db_session)
    assert len(assistants) > 0

    # 按MBTI类型筛选
    intj_assistants = service.get_recommended_assistants(
        db_session, mbti_type="INTJ"
    )
    for a in intj_assistants:
        assert a.mbti_type.value == "INTJ"
```

#### 4.2.3 对话服务测试

```python
# backend/tests/unit/test_chat_service.py
import pytest
from app.services.chat_service import ChatService


@pytest.mark.asyncio
async def test_create_conversation(db_session, test_user):
    """测试创建对话"""
    service = ChatService()

    conversation = await service.create_conversation(
        db=db_session,
        user_id=test_user.id,
        assistant_id=1,
        title="测试对话"
    )

    assert conversation.id is not None
    assert conversation.user_id == test_user.id
    assert conversation.title == "测试对话"


def test_get_conversations(db_session, test_user):
    """测试获取对话列表"""
    service = ChatService()

    # 创建几个对话
    import asyncio
    asyncio.run(service.create_conversation(db_session, test_user.id, 1, "对话1"))
    asyncio.run(service.create_conversation(db_session, test_user.id, 1, "对话2"))

    conversations = service.get_conversations(db_session, test_user.id)
    assert len(conversations) == 2


def test_collect_message(db_session, test_user):
    """测试收藏消息"""
    from app.models import Conversation, Message
    from app.models.chat import MessageType

    # 创建测试数据
    conv = Conversation(
        user_id=test_user.id,
        session_id="test_session",
        assistant_id=1,
        title="测试"
    )
    db_session.add(conv)
    db_session.flush()

    msg = Message(
        conversation_id=conv.id,
        role="assistant",
        content="测试消息",
        message_type=MessageType.TEXT,
        is_collected=False
    )
    db_session.add(msg)
    db_session.commit()

    service = ChatService()
    result = service.collect_message(db_session, test_user.id, msg.id)

    assert result is True

    # 验证
    db_session.refresh(msg)
    assert msg.is_collected is True
```

#### 4.2.4 LLM工厂测试

```python
# backend/tests/unit/test_llm_factory.py
import pytest
from app.services.llm.factory import get_llm_provider, chat
from app.services.llm.providers import MockProvider


def test_get_mock_provider():
    """测试获取Mock Provider"""
    from app.core.config import settings
    settings.LLM_PROVIDER = "mock"

    provider = get_llm_provider()
    assert isinstance(provider, MockProvider)


@pytest.mark.asyncio
async def test_mock_chat():
    """测试Mock聊天"""
    from app.core.config import settings
    settings.LLM_PROVIDER = "mock"

    response = await chat([{"role": "user", "content": "你好"}])
    assert isinstance(response, str)
    assert len(response) > 0


@pytest.mark.asyncio
async def test_mock_emotional_response():
    """测试Mock情绪响应"""
    from app.core.config import settings
    settings.LLM_PROVIDER = "mock"

    # 测试难过响应
    sad_response = await chat([{"role": "user", "content": "我今天很难过"}])
    assert "难过" in sad_response or "理解" in sad_response

    # 测试焦虑响应
    anxious_response = await chat([{"role": "user", "content": "我感到很焦虑"}])
    assert "焦虑" in anxious_response or "深呼吸" in anxious_response


def test_provider_map_complete():
    """测试Provider映射完整性"""
    from app.services.llm.providers import PROVIDER_MAP

    expected_providers = [
        "mock", "openai", "anthropic", "glm", "qwen",
        "minimax", "ernie", "hunyuan", "spark", "doubao", "siliconflow"
    ]

    for provider_name in expected_providers:
        assert provider_name in PROVIDER_MAP
```

#### 4.2.5 内容过滤测试

```python
# backend/tests/unit/test_content_filter.py
import pytest
from app.services.content_filter import get_content_filter


@pytest.mark.asyncio
async def test_keyword_filter():
    """测试关键词过滤"""
    content_filter = get_content_filter()

    # 测试正常内容
    passed, blocked = await content_filter.check_text("你好，今天天气不错")
    assert passed is True
    assert blocked is None

    # 测试敏感内容
    # 这里需要根据实际敏感词库进行测试
    passed, blocked = await content_filter.check_text("一些敏感词汇")
    # 结果取决于具体实现


def test_get_blocked_response():
    """测试获取拦截响应"""
    content_filter = get_content_filter()
    response = content_filter.get_blocked_response()
    assert isinstance(response, str)
    assert len(response) > 0
```

### 4.3 前端单元测试

```typescript
// frontend/web/src/__tests__/utils/security.test.ts
import { maskPhone, validatePhone, validatePassword } from '../../utils/security'

describe('Security utils', () => {
  describe('maskPhone', () => {
    it('should mask Chinese phone number correctly', () => {
      expect(maskPhone('13800138000')).toBe('138****8000')
    })

    it('should return original if length is not 11', () => {
      expect(maskPhone('12345')).toBe('12345')
      expect(maskPhone('')).toBe('')
    })
  })

  describe('validatePhone', () => {
    it('should validate correct phone numbers', () => {
      expect(validatePhone('13800138000')).toBe(true)
      expect(validatePhone('15912345678')).toBe(true)
    })

    it('should reject invalid phone numbers', () => {
      expect(validatePhone('12345')).toBe(false)
      expect(validatePhone('')).toBe(false)
      expect(validatePhone('abcdefghijk')).toBe(false)
    })
  })

  describe('validatePassword', () => {
    it('should validate strong passwords', () => {
      expect(validatePassword('Test@123456')).toBe(true)
    })

    it('should reject weak passwords', () => {
      expect(validatePassword('123456')).toBe(false)
      expect(validatePassword('password')).toBe(false)
    })
  })
})

// frontend/web/src/__tests__/components/LoadingContainer.test.tsx
import { render, screen } from '@testing-library/react'
import { LoadingContainer } from '../../components/LoadingContainer'

describe('LoadingContainer', () => {
  it('renders loading indicator when loading', () => {
    render(<LoadingContainer loading={true} />)
    expect(screen.getByRole('status')).toBeInTheDocument()
  })

  it('renders children when not loading', () => {
    render(
      <LoadingContainer loading={false}>
        <div data-testid="content">Content</div>
      </LoadingContainer>
    )
    expect(screen.getByTestId('content')).toBeInTheDocument()
  })
})

// frontend/web/src/__tests__/stores/auth.test.ts
import { act, renderHook } from '@testing-library/react'
import { useAuthStore } from '../../stores'

describe('Auth Store', () => {
  beforeEach(() => {
    localStorage.clear()
  })

  it('initializes with unauthenticated state', () => {
    const { result } = renderHook(() => useAuthStore())
    expect(result.current.isAuthenticated).toBe(false)
    expect(result.current.user).toBe(null)
  })

  it('sets user correctly on login', () => {
    const { result } = renderHook(() => useAuthStore())

    act(() => {
      result.current.setUser({
        id: 1,
        phone: '13800138000',
        nickname: '测试用户',
      })
      result.current.setTokens('access-token', 'refresh-token')
    })

    expect(result.current.isAuthenticated).toBe(true)
    expect(result.current.user?.nickname).toBe('测试用户')
  })

  it('clears user correctly on logout', () => {
    const { result } = renderHook(() => useAuthStore())

    act(() => {
      result.current.setUser({
        id: 1,
        phone: '13800138000',
        nickname: '测试用户',
      })
      result.current.logout()
    })

    expect(result.current.isAuthenticated).toBe(false)
    expect(result.current.user).toBe(null)
  })
})
```

---

## 5. 集成测试

### 5.1 认证API测试

```python
# backend/tests/integration/test_api_auth.py
import pytest


def test_send_verify_code(client):
    """测试发送验证码"""
    response = client.post("/api/v1/auth/send_code", json={
        "phone": "13800138000"
    })
    assert response.status_code == 200
    assert "message" in response.json()


def test_register_new_user(client):
    """测试新用户注册"""
    # 先发送验证码
    client.post("/api/v1/auth/send_code", json={"phone": "13800138000"})

    # 注册 (debug模式下验证码不严格验证)
    response = client.post("/api/v1/auth/register", json={
        "phone": "13800138000",
        "password": "Test@123456",
        "code": "123456",
        "nickname": "新用户"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert "user" in data


def test_login_success(client, test_user):
    """测试登录成功"""
    response = client.post("/api/v1/auth/login", json={
        "phone": "13800138000",
        "password": "Test@123456"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["phone"] == "13800138000"


def test_login_wrong_password(client, test_user):
    """测试密码错误"""
    response = client.post("/api/v1/auth/login", json={
        "phone": "13800138000",
        "password": "WrongPassword"
    })
    assert response.status_code == 401


def test_get_current_user(client, auth_headers):
    """测试获取当前用户信息"""
    response = client.get("/api/v1/auth/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "phone" in data
    assert "nickname" in data


def test_refresh_token(client, test_user):
    """测试刷新令牌"""
    # 先登录获取refresh token
    login_response = client.post("/api/v1/auth/login", json={
        "phone": "13800138000",
        "password": "Test@123456"
    })
    refresh_token = login_response.json()["refresh_token"]

    # 使用refresh token获取新的access token
    response = client.post("/api/v1/auth/refresh", json={
        "refresh_token": refresh_token
    })
    assert response.status_code == 200
    assert "access_token" in response.json()
```

### 5.2 MBTI API测试

```python
# backend/tests/integration/test_api_mbti.py
import pytest


def test_get_mbti_questions(client):
    """测试获取MBTI题目"""
    response = client.get("/api/v1/mbti/questions")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "questions" in data
    assert data["total"] == 48


def test_get_mbti_questions_by_dimension(client):
    """测试按维度获取题目"""
    response = client.get("/api/v1/mbti/questions?dimension=EI")
    assert response.status_code == 200
    data = response.json()
    assert all(q["dimension"] == "EI" for q in data["questions"])


def test_start_mbti_test(client, auth_headers):
    """测试开始MBTI测试"""
    response = client.post("/api/v1/mbti/start", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data
    assert data["total_questions"] == 48


def test_submit_mbti_test(client, auth_headers):
    """测试提交MBTI测试答案"""
    # 先获取题目
    questions_resp = client.get("/api/v1/mbti/questions")
    questions = questions_resp.json()["questions"]

    # 构建答案
    answers = [
        {"question_id": q["id"], "answer": "A"}
        for q in questions
    ]

    # 提交答案
    response = client.post("/api/v1/mbti/submit", json={
        "answers": answers
    }, headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert "mbti_type" in data
    assert "ei_score" in data
    assert "personality" in data


def test_get_mbti_result(client, auth_headers):
    """测试获取MBTI结果"""
    # 先完成测试
    questions_resp = client.get("/api/v1/mbti/questions")
    questions = questions_resp.json()["questions"]
    answers = [{"question_id": q["id"], "answer": "A"} for q in questions]
    client.post("/api/v1/mbti/submit", json={"answers": answers}, headers=auth_headers)

    # 获取结果
    response = client.get("/api/v1/mbti/result", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "mbti_type" in data


def test_get_assistants(client):
    """测试获取AI助手列表"""
    response = client.get("/api/v1/mbti/assistants")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "list" in data


def test_get_assistant_detail(client):
    """测试获取AI助手详情"""
    # 先获取列表
    list_resp = client.get("/api/v1/mbti/assistants")
    assistants = list_resp.json()["list"]

    if assistants:
        assistant_id = assistants[0]["id"]
        response = client.get(f"/api/v1/mbti/assistants/{assistant_id}")
        assert response.status_code == 200
        assert "name" in response.json()
```

### 5.3 对话API测试

```python
# backend/tests/integration/test_api_chat.py
import pytest


def test_create_conversation(client, auth_headers):
    """测试创建对话"""
    response = client.post("/api/v1/chat/create", json={
        "assistant_id": 1,
        "title": "测试对话"
    }, headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data
    assert data["title"] == "测试对话"


def test_get_conversations(client, auth_headers):
    """测试获取对话列表"""
    # 先创建一个对话
    client.post("/api/v1/chat/create", json={
        "assistant_id": 1,
        "title": "测试对话"
    }, headers=auth_headers)

    # 获取列表
    response = client.get("/api/v1/chat/conversations", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "list" in data


def test_send_chat_message(client, auth_headers):
    """测试发送聊天消息"""
    # 先创建对话
    create_resp = client.post("/api/v1/chat/create", json={
        "assistant_id": 1,
        "title": "测试对话"
    }, headers=auth_headers)
    session_id = create_resp.json()["session_id"]

    # 发送消息
    response = client.post("/api/v1/chat/send", json={
        "session_id": session_id,
        "content": "你好"
    }, headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert "user_message" in data
    assert "assistant_message" in data


def test_get_chat_history(client, auth_headers):
    """测试获取对话历史"""
    # 先创建对话并发送消息
    create_resp = client.post("/api/v1/chat/create", json={
        "assistant_id": 1,
        "title": "测试对话"
    }, headers=auth_headers)
    session_id = create_resp.json()["session_id"]

    client.post("/api/v1/chat/send", json={
        "session_id": session_id,
        "content": "你好"
    }, headers=auth_headers)

    # 获取历史
    response = client.get(f"/api/v1/chat/history/{session_id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "list" in data
```

### 5.4 情感日记API测试

```python
# backend/tests/integration/test_api_diary.py
import pytest
from datetime import date


def test_create_diary(client, auth_headers):
    """测试创建日记"""
    today = date.today().isoformat()
    response = client.post("/api/v1/diary/create", json={
        "date": today,
        "mood_score": 8,
        "content": "今天心情不错",
        "category": "生活",
        "tags": "开心,工作"
    }, headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["content"] == "今天心情不错"


def test_get_diary_list(client, auth_headers):
    """测试获取日记列表"""
    # 先创建日记
    today = date.today().isoformat()
    client.post("/api/v1/diary/create", json={
        "date": today,
        "mood_score": 7,
        "content": "测试日记"
    }, headers=auth_headers)

    # 获取列表
    response = client.get("/api/v1/diary/list", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "data" in data


def test_get_diary_detail(client, auth_headers):
    """测试获取日记详情"""
    # 先创建日记
    today = date.today().isoformat()
    create_resp = client.post("/api/v1/diary/create", json={
        "date": today,
        "mood_score": 7,
        "content": "测试日记详情"
    }, headers=auth_headers)
    diary_id = create_resp.json()["id"]

    # 获取详情
    response = client.get(f"/api/v1/diary/{diary_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["content"] == "测试日记详情"


def test_update_diary(client, auth_headers):
    """测试更新日记"""
    # 先创建日记
    today = date.today().isoformat()
    create_resp = client.post("/api/v1/diary/create", json={
        "date": today,
        "mood_score": 7,
        "content": "原始内容"
    }, headers=auth_headers)
    diary_id = create_resp.json()["id"]

    # 更新
    response = client.put(f"/api/v1/diary/{diary_id}", json={
        "content": "更新后的内容",
        "mood_score": 9
    }, headers=auth_headers)

    assert response.status_code == 200
    assert response.json()["content"] == "更新后的内容"


def test_delete_diary(client, auth_headers):
    """测试删除日记"""
    # 先创建日记
    today = date.today().isoformat()
    create_resp = client.post("/api/v1/diary/create", json={
        "date": today,
        "mood_score": 7,
        "content": "要删除的日记"
    }, headers=auth_headers)
    diary_id = create_resp.json()["id"]

    # 删除
    response = client.delete(f"/api/v1/diary/{diary_id}", headers=auth_headers)
    assert response.status_code == 200

    # 验证已删除
    get_resp = client.get(f"/api/v1/diary/{diary_id}", headers=auth_headers)
    assert get_resp.status_code == 404


def test_get_diary_stats(client, auth_headers):
    """测试获取日记统计"""
    response = client.get("/api/v1/diary/stats", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "total_count" in data
    assert "current_streak" in data
    assert "avg_mood" in data


def test_create_mood_record(client, auth_headers):
    """测试创建心情记录"""
    response = client.post("/api/v1/diary/mood", json={
        "mood_score": 8,
        "note": "感觉不错"
    }, headers=auth_headers)

    assert response.status_code == 200
    assert "id" in response.json()


def test_get_tags(client, auth_headers):
    """测试获取标签列表"""
    response = client.get("/api/v1/diary/tags", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)
```

### 5.5 管理后台API测试

```python
# backend/tests/integration/test_api_admin.py
import pytest


def test_admin_config_requires_auth(client):
    """测试管理配置需要认证"""
    response = client.get("/api/v1/admin/config")
    assert response.status_code in [401, 403]


def test_admin_config_requires_admin_role(client, auth_headers):
    """测试管理配置需要管理员角色"""
    # 普通用户访问应该被拒绝
    response = client.get("/api/v1/admin/config", headers=auth_headers)
    assert response.status_code == 403


def test_admin_config_as_admin(client, db_session):
    """测试管理员访问配置"""
    from app.models import User
    from app.core.security import get_password_hash

    # 创建管理员用户
    admin = User(
        phone="13900139000",
        nickname="管理员",
        password_hash=get_password_hash("Admin@123456"),
        is_active=True,
        is_admin=True,
    )
    db_session.add(admin)
    db_session.commit()

    # 登录获取token
    login_resp = client.post("/api/v1/auth/login", json={
        "phone": "13900139000",
        "password": "Admin@123456"
    })
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 访问管理配置
    response = client.get("/api/v1/admin/config", headers=headers)
    assert response.status_code == 200
```

---

## 6. 端到端测试

### 6.1 Playwright E2E测试

```typescript
// frontend/web/e2e/auth.spec.ts
import { test, expect } from '@playwright/test'

test.describe('Authentication Flow', () => {
  test('should allow user to register', async ({ page }) => {
    await page.goto('/register')

    // 填写注册表单
    await page.fill('input[name="phone"]', '13800138000')
    await page.fill('input[name="nickname"]', '测试用户')
    await page.fill('input[name="password"]', 'Test@123456')
    await page.fill('input[name="code"]', '123456')

    // 点击发送验证码
    await page.click('button:has-text("发送验证码")')

    // 点击注册
    await page.click('button:has-text("注册")')

    // 应该跳转到首页
    await expect(page).toHaveURL('/')
    await expect(page.locator('text=测试用户')).toBeVisible()
  })

  test('should allow user to login and logout', async ({ page }) => {
    // 先注册一个用户
    await page.goto('/register')
    await page.fill('input[name="phone"]', '13900139000')
    await page.fill('input[name="nickname"]', '登录测试')
    await page.fill('input[name="password"]', 'Test@123456')
    await page.fill('input[name="code"]', '123456')
    await page.click('button:has-text("注册")')

    // 退出登录
    await page.goto('/profile')
    await page.click('button:has-text("退出登录")')

    // 重新登录
    await page.goto('/login')
    await page.fill('input[name="phone"]', '13900139000')
    await page.fill('input[name="password"]', 'Test@123456')
    await page.click('button:has-text("登录")')

    await expect(page).toHaveURL('/')
  })
})

// frontend/web/e2e/mbti.spec.ts
import { test, expect } from '@playwright/test'

test.describe('MBTI Test Flow', () => {
  test('should complete MBTI test and see result', async ({ page }) => {
    // 登录
    await page.goto('/login')
    await page.fill('input[name="phone"]', '13800138000')
    await page.fill('input[name="password"]', 'Test@123456')
    await page.click('button:has-text("登录")')

    // 进入MBTI测试
    await page.goto('/mbti')

    // 回答所有48道题
    for (let i = 0; i < 48; i++) {
      await page.click('button:has-text("A.")')
    }

    // 应该看到结果页面
    await expect(page).toHaveURL('/mbti/result')
    await expect(page.locator('text=你的MBTI类型')).toBeVisible()
    await expect(page.locator('text=性格描述')).toBeVisible()
  })

  test('should see recommended assistants', async ({ page }) => {
    await page.goto('/assistants')
    await expect(page.locator('[data-testid="assistant-card"]').first()).toBeVisible()
  })
})

// frontend/web/e2e/chat.spec.ts
import { test, expect } from '@playwright/test'

test.describe('Chat Flow', () => {
  test('should start a conversation and send message', async ({ page }) => {
    // 登录
    await page.goto('/login')
    await page.fill('input[name="phone"]', '13800138000')
    await page.fill('input[name="password"]', 'Test@123456')
    await page.click('button:has-text("登录")')

    // 选择助手并开始对话
    await page.goto('/assistants')
    await page.click('[data-testid="assistant-card"] >> button:has-text("开始对话")')

    // 发送消息
    await page.fill('textarea', '你好')
    await page.click('button:has-text("发送")')

    // 应该看到回复
    await expect(page.locator('text=谢谢你的分享').or(page.locator('text=我在这里'))).toBeVisible()
  })

  test('should see conversation history', async ({ page }) => {
    // 登录
    await page.goto('/login')
    await page.fill('input[name="phone"]', '13800138000')
    await page.fill('input[name="password"]', 'Test@123456')
    await page.click('button:has-text("登录")')

    // 进入对话页面
    await page.goto('/chat')

    // 应该看到侧边栏对话列表
    await expect(page.locator('text=对话列表')).toBeVisible()
  })
})

// frontend/web/e2e/diary.spec.ts
import { test, expect } from '@playwright/test'

test.describe('Diary Flow', () => {
  test('should create a diary entry', async ({ page }) => {
    // 登录
    await page.goto('/login')
    await page.fill('input[name="phone"]', '13800138000')
    await page.fill('input[name="password"]', 'Test@123456')
    await page.click('button:has-text("登录")')

    // 进入日记页面
    await page.goto('/diary')

    // 创建新日记
    await page.click('button:has-text("写日记")')

    await page.fill('textarea[name="content"]', '今天是美好的一天')
    await page.selectOption('select[name="mood"]', '8')
    await page.click('button:has-text("保存")')

    // 应该看到日记列表中有新条目
    await expect(page).toHaveURL('/diary')
    await expect(page.locator('text=今天是美好的一天')).toBeVisible()
  })

  test('should see diary stats', async ({ page }) => {
    await page.goto('/diary/stats')
    await expect(page.locator('text=总记录')).toBeVisible()
    await expect(page.locator('text=连续记录')).toBeVisible()
    await expect(page.locator('text=平均心情')).toBeVisible()
  })
})
```

---

## 7. 性能测试

### 7.1 Locust性能测试

```python
# backend/locustfile.py
from locust import HttpUser, task, between
import random

class EmotionAIUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        """用户开始时执行"""
        # 注册或登录
        self.client.post("/api/v1/auth/send_code", json={"phone": f"138{random.randint(10000000, 99999999)}"})

        register_resp = self.client.post("/api/v1/auth/register", json={
            "phone": f"138{random.randint(10000000, 99999999)}",
            "password": "Test@123456",
            "code": "123456",
            "nickname": f"测试用户{random.randint(1, 10000)}"
        })
        self.token = register_resp.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}

        # 获取MBTI题目
        self.questions = self.client.get("/api/v1/mbti/questions").json()["questions"]

    @task(3)
    def get_home(self):
        """访问首页"""
        self.client.get("/")

    @task(2)
    def get_mbti_questions(self):
        """获取MBTI题目"""
        self.client.get("/api/v1/mbti/questions")

    @task(1)
    def submit_mbti_test(self):
        """提交MBTI测试"""
        answers = [
            {"question_id": q["id"], "answer": random.choice(["A", "B"])}
            for q in self.questions
        ]
        self.client.post("/api/v1/mbti/submit", json={"answers": answers}, headers=self.headers)

    @task(4)
    def send_chat_message(self):
        """发送聊天消息"""
        # 创建对话
        create_resp = self.client.post("/api/v1/chat/create", json={
            "assistant_id": 1,
            "title": "性能测试对话"
        }, headers=self.headers)
        session_id = create_resp.json()["session_id"]

        # 发送消息
        messages = ["你好", "今天心情不错", "能和我聊聊吗", "我有些困扰"]
        self.client.post("/api/v1/chat/send", json={
            "session_id": session_id,
            "content": random.choice(messages)
        }, headers=self.headers)

    @task(2)
    def get_conversations(self):
        """获取对话列表"""
        self.client.get("/api/v1/chat/conversations", headers=self.headers)

    @task(1)
    def get_diary_list(self):
        """获取日记列表"""
        self.client.get("/api/v1/diary/list", headers=self.headers)
```

### 7.2 性能测试场景

| 场景 | 并发用户 | 持续时间 | 目标 |
|------|----------|----------|------|
| 轻负载 | 10 | 5分钟 | P99 < 1s |
| 中负载 | 50 | 10分钟 | P99 < 2s |
| 高负载 | 200 | 10分钟 | P99 < 3s |
| 峰值负载 | 500 | 2分钟 | 错误率 < 1% |
| 稳定性测试 | 100 | 30分钟 | 无崩溃 |

---

## 8. 安全测试

### 8.1 安全测试清单

| 测试项 | 工具/方法 | 预期结果 |
|--------|-----------|----------|
| SQL注入 | 手动测试 + Bandit | 无注入漏洞 |
| XSS攻击 | 手动测试 + OWASP ZAP | 无XSS漏洞 |
| CSRF攻击 | 手动测试 | CSRF防护有效 |
| 认证绕过 | 手动测试 | 无法绕过 |
| 敏感数据泄露 | 代码审计 | 无明文敏感数据 |
| 依赖漏洞 | safety + npm audit | 无高危漏洞 |
| 速率限制 | 手动测试 | 限流有效 |
| 文件上传 | 手动测试 | 无法上传恶意文件 |

### 8.2 Python安全扫描

```bash
# 使用Bandit扫描
bandit -r backend/app/ -f json -o bandit-report.json

# 使用Safety检查依赖
cd backend
safety check --full-report

# 使用pip-audit
pip-audit
```

### 8.3 前端安全扫描

```bash
cd frontend/web
npm audit --audit-level=high

# 使用ESLint安全规则
npm run lint
```

### 8.4 OWASP ZAP扫描

```yaml
# zap-scan.yml
---
context:
  name: "Emotion AI"
  urls:
    - "http://localhost:8000"
  includePaths:
    - "http://localhost:8000/api.*"
  excludePaths:
    - "http://localhost:8000/api/v1/admin.*"

spider:
  maxDepth: 3
  maxChildren: 10

scanner:
  attackOnStart: true
  maxRuleDurationInMins: 5
```

---

## 9. 兼容性测试

### 9.1 浏览器兼容性

| 浏览器 | 最低版本 | 测试状态 |
|--------|----------|----------|
| Chrome | 90+ | ⏳ |
| Firefox | 88+ | ⏳ |
| Safari | 14+ | ⏳ |
| Edge | 90+ | ⏳ |
| 移动端Safari | iOS 14+ | ⏳ |
| Chrome Mobile | Android 10+ | ⏳ |

### 9.2 屏幕尺寸兼容性

| 设备类型 | 分辨率范围 |
|----------|-----------|
| 移动端 | 320px - 768px |
| 平板 | 768px - 1024px |
| 桌面 | 1024px - 1920px |
| 大屏 | 1920px+ |

---

## 10. 测试执行计划

### 10.1 测试时间表

| 阶段 | 任务 | 负责人 | 预计时间 |
|------|------|--------|----------|
| Week 1 | 测试框架搭建 | 后端/测试 | 2天 |
| Week 1 | 后端单元测试编写 | 后端/测试 | 3天 |
| Week 2 | 后端集成测试编写 | 后端/测试 | 3天 |
| Week 2 | 前端单元测试编写 | 前端/测试 | 2天 |
| Week 3 | E2E测试编写 | 测试 | 2天 |
| Week 3 | 性能测试执行 | 测试/后端 | 2天 |
| Week 3 | 安全测试执行 | 安全 | 1天 |
| Week 3 | 缺陷修复与回归 | 全团队 | 2天 |

### 10.2 测试通过标准

- 单元测试覆盖率 ≥ 85%
- 所有集成测试通过
- 关键E2E测试通过
- 性能测试达到目标指标
- 安全测试无高危和中危漏洞
- 兼容性测试覆盖主要浏览器

---

**文档结束**
