# 赛博生命2D虚拟形象系统设计方案

## 1. 项目概述

为情感AI助手系统增加"赛博生命"功能，让AI助手拥有可视化的2D虚拟形象（Live2D/VRM），支持：

- **可视化的AI伴侣**: 2D动态立绘，有四肢、五官、表情
- **沉浸式互动**: 助手会根据对话内容产生相应的动画反馈
- **多模态交互**: 文字、语音、表情、动作

## 2. 技术选型

### 2.1 虚拟形象格式

| 格式 | 用途 | 前端渲染库 |
|------|------|-----------|
| **Live2D** | 2D立绘，细腻的表情变化 | live2d.js / pixi-live2d |
| **VRM** | 3D模型，灵活的动作 | three.js + VRMLoader |

### 2.2 前端技术栈

- **React 18** + TypeScript
- **Pixi.js** - 2D渲染引擎
- **@pixi/live2d** - Live2D模型渲染
- **Three.js** - VRM模型渲染
- **WebSocket** - 实时动画同步

## 3. 系统架构

```
┌─────────────────────────────────────────────────────────┐
│                      Frontend                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │  ChatView   │  │ Live2DRender│  │ VRMRenderer │     │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘     │
│         │                │                │              │
│         └────────────────┼────────────────┘              │
│                          ▼                               │
│                  ┌───────────────┐                       │
│                  │ AvatarController│                     │
│                  └───────┬───────┘                       │
└──────────────────────────┼──────────────────────────────┘
                           │ WebSocket
┌──────────────────────────┼──────────────────────────────┐
│                      Backend                             │
│                  ┌───────┴───────┐                       │
│                  │ AnimationService│                     │
│                  └───────┬───────┘                       │
│         ┌────────────────┼────────────────┐              │
│         ▼                ▼                ▼              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │
│  │ EmotionAnalyzer│  │ ActionSelector│  │ AssetManager│     │
│  └─────────────┘  └─────────────┘  └─────────────┘      │
└──────────────────────────────────────────────────────────┘
```

## 4. 数据模型

### 4.1 虚拟形象配置 (AiAvatar)

```python
class AiAvatar(Base):
    """AI助手虚拟形象配置"""
    id: int
    assistant_id: int  # 关联的AI助手

    # Live2D配置
    live2d_model_url: Optional[str]  # Live2D模型文件(.moc3)
    live2d_texture_urls: JSON  # 纹理图片列表
    live2d_motion_groups: JSON  # 动作分组

    # VRM配置
    vrm_model_url: Optional[str]  # VRM模型文件

    # 基础配置
    name: str
    description: Optional[str]

    # 表情映射
    expression_map: JSON  # 情感->表情映射

    # 动作配置
    default_motion: str  # 默认待机动作
    speak_motion: str   # 说话时的动作
    idle_motions: JSON  # 随机待机动作列表

    # 位置与缩放
    position_x: float = 0.0
    position_y: float = 0.0
    scale: float = 1.0
    z_index: int = 1

    is_active: bool = True
```

### 4.2 动画状态 (AnimationState)

```python
class AnimationState(Base):
    """动画状态记录"""
    id: int
    user_id: int
    assistant_id: int

    # 当前状态
    current_expression: str  # 当前表情
    current_motion: str     # 当前动作

    # 过渡配置
    transition_duration: float = 0.3  # 过渡时长(秒)

    updated_at: datetime
```

## 5. API设计

### 5.1 虚拟形象管理

```
GET    /api/v1/avatar/{assistant_id}     获取助手虚拟形象配置
POST   /api/v1/avatar/upload             上传自定义虚拟形象
PUT    /api/v1/avatar/{id}               更新虚拟形象配置
DELETE /api/v1/avatar/{id}               删除虚拟形象
```

### 5.2 动画控制

```
WebSocket /ws/avatar/{assistant_id}      实时动画同步

// 消息格式
{
    "type": "expression" | "motion" | "emotion",
    "data": {
        "expression": "happy",
        "motion": "wave",
        "emotion": "excited"
    },
    "timestamp": 1234567890
}
```

### 5.3 情感分析 -> 动画映射

```
POST   /api/v1/avatar/animate            根据内容获取动画指令
Body: {
    "message": "用户消息",
    "response": "AI回复内容",
    "emotion": "happy|neutral|sad|angry|excited"
}
Response: {
    "expressions": ["smile", "blush"],
    "motions": ["wave", "happy"],
    "sound": null
}
```

## 6. 前端组件设计

### 6.1 AvatarCanvas 组件

```tsx
interface AvatarCanvasProps {
  modelUrl: string;
  modelType: 'live2d' | 'vrm';
  position?: { x: number; y: number };
  scale?: number;
  onLoad?: () => void;
  onError?: (error: Error) => void;
}
```

功能：
- 加载并渲染虚拟形象
- 处理模型切换
- 支持拖拽移动位置
- 支持滚轮缩放

### 6.2 AvatarController 组件

```tsx
interface AvatarControllerProps {
  assistantId: number;
  avatarUrl: string;
  onEmotionChange?: (emotion: string) => void;
}
```

功能：
- 管理动画状态
- 与后端WebSocket通信
- 处理用户交互（点击、触摸）
- 协调聊天与动画同步

### 6.3 ExpressionSelector 组件

功能：
- 显示可用表情列表
- 预览表情效果
- 快捷切换表情

## 7. 动画系统设计

### 7.1 内置表情

| 表情 | 描述 | 适用场景 |
|------|------|---------|
| neutral | 默认表情 | 一般对话 |
| happy | 开心 | 积极回复、赞美 |
| sad | 难过 | 同情、安慰 |
| angry | 生气 | 不认同、批评 |
| surprised | 惊讶 | 意外、震惊 |
| blush | 脸红 | 害羞、不好意思 |
| laugh | 大笑 | 开心、幽默 |
| thinking | 思考 | 等待回复 |
| sleeping | 犯困 | 无聊、疲倦 |

### 7.2 内置动作

| 动作 | 描述 |
|------|------|
| idle | 随机待机 |
| wave | 挥手 |
| nod | 点头 |
| shake_head | 摇头 |
| happy | 开心跳动 |
| sad | 低头 |
| speak | 说话（口型） |
| touch | 被触摸反应 |

### 7.3 情感 -> 动画映射规则

```python
EMOTION_ANIMATION_MAP = {
    "happy": {
        "expressions": ["happy", "blush"],
        "motions": ["happy"],
        "priority": 2
    },
    "excited": {
        "expressions": ["happy", "surprised"],
        "motions": ["wave", "happy"],
        "priority": 3
    },
    "neutral": {
        "expressions": ["neutral"],
        "motions": ["idle"],
        "priority": 1
    },
    "sad": {
        "expressions": ["sad"],
        "motions": ["sad"],
        "priority": 2
    },
    "angry": {
        "expressions": ["angry"],
        "motions": ["shake_head"],
        "priority": 2
    },
    "surprised": {
        "expressions": ["surprised"],
        "motions": [],
        "priority": 2
    }
}
```

## 8. 实现计划

### Phase 1: 基础框架
- [ ] 后端：添加AiAvatar数据模型
- [ ] 后端：添加AnimationService服务
- [ ] 后端：添加虚拟形象管理API
- [ ] 前端：添加AvatarCanvas组件

### Phase 2: Live2D集成
- [ ] 前端：集成live2d.js库
- [ ] 前端：实现Live2D模型加载和渲染
- [ ] 前端：实现基础动画控制

### Phase 3: VRM支持（可选）
- [ ] 前端：集成three.js和VRMLoader
- [ ] 前端：实现VRM模型渲染

### Phase 4: 实时动画
- [ ] 后端：实现WebSocket动画服务
- [ ] 后端：情感分析 -> 动画映射
- [ ] 前端：WebSocket客户端集成

### Phase 5: 交互功能
- [ ] 前端：点击/触摸交互
- [ ] 前端：拖拽移动位置
- [ ] 前端：位置保存到后端

## 9. 预设虚拟形象

### 第一批预设形象（基于现有AI助手）

| 助手名称 | MBTI | 适合的风格 |
|----------|------|-----------|
| 温柔倾听者-小暖 | INFJ | 温柔、治愈系 |
| 理性分析家-小智 | INTJ | 冷静、理性 |
| 阳光能量站-小乐 | ENFP | 活泼、元气 |
| 知心大姐姐-小雅 | ENFJ | 温暖、大姐姐 |
| 冷静思考者-小安 | ISTP | 酷酷的、务实 |
| 心灵治愈师-小柔 | ISFJ | 柔软、温暖 |
| 创意梦想家-小飞 | INFP | 梦幻、诗意 |
| 职场军师-小锋 | ENTJ | 干练、领导力 |

## 10. 文件结构

```
backend/
├── app/
│   ├── models/
│   │   ├── avatar.py          # AiAvatar, AnimationState模型
│   │   └── __init__.py
│   ├── schemas/
│   │   ├── avatar.py          # Pydantic schemas
│   │   └── __init__.py
│   ├── api/v1/
│   │   ├── avatar.py          # 虚拟形象管理API
│   │   └── __init__.py
│   └── services/
│       ├── animation_service.py  # 动画控制服务
│       ├── emotion_analyzer.py   # 情感分析服务
│       └── __init__.py
├── assets/
│   ├── live2d/               # Live2D模型文件
│   │   └── templates/        # 预设模板
│   └── vrm/                  # VRM模型文件
│       └── templates/

frontend/web/
├── src/
│   ├── components/
│   │   ├── avatar/
│   │   │   ├── AvatarCanvas.tsx    # 渲染画布
│   │   │   ├── Live2DRenderer.tsx  # Live2D渲染器
│   │   │   ├── VRMRenderer.tsx     # VRM渲染器
│   │   │   ├── AvatarController.tsx # 控制器
│   │   │   └── index.ts
│   │   └── ...
│   ├── hooks/
│   │   ├── useAvatar.ts           # 虚拟形象hook
│   │   └── useAnimation.ts        # 动画控制hook
│   ├── stores/
│   │   └── avatarStore.ts         # 状态管理
│   └── assets/
│       └── live2d/                # 前端静态资源
```

## 11. 注意事项

1. **模型文件大小**: Live2D/VRM模型通常较大(10-50MB)，需要考虑加载优化
2. **移动端适配**: 需要处理移动端触摸交互
3. **性能优化**: 使用Web Worker处理模型加载
4. **跨域问题**: 模型文件需要配置正确的CORS头
5. **浏览器兼容性**: Live2D需要WebGL支持