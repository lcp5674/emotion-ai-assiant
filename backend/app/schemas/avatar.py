"""
虚拟形象Schemas
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


# ============ 虚拟形象 Schemas ============

class AiAvatarBase(BaseModel):
    """虚拟形象基础配置"""
    model_type: str = Field(default="live2d", description="模型类型: live2d 或 vrm")
    name: Optional[str] = None
    description: Optional[str] = None
    position_x: float = 0.0
    position_y: float = 0.0
    scale: float = 1.0
    z_index: int = 1
    default_motion: str = "idle"
    speak_motion: str = "speak"
    idle_motions: Optional[List[str]] = None


class AiAvatarCreate(AiAvatarBase):
    """创建虚拟形象"""
    assistant_id: int


class AiAvatarUpdate(BaseModel):
    """更新虚拟形象"""
    model_type: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    live2d_model_url: Optional[str] = None
    live2d_texture_urls: Optional[List[str]] = None
    live2d_motion_groups: Optional[Dict[str, List[str]]] = None
    live2d_expression_map: Optional[Dict[str, str]] = None
    vrm_model_url: Optional[str] = None
    position_x: Optional[float] = None
    position_y: Optional[float] = None
    scale: Optional[float] = None
    z_index: Optional[int] = None
    default_motion: Optional[str] = None
    speak_motion: Optional[str] = None
    idle_motions: Optional[List[str]] = None
    is_active: Optional[bool] = None


class Live2DConfig(BaseModel):
    """Live2D模型配置"""
    model_url: Optional[str] = None
    texture_urls: List[str] = []
    motion_groups: Dict[str, List[str]] = {}
    expression_map: Dict[str, str] = {}


class VRMConfig(BaseModel):
    """VRM模型配置"""
    model_url: Optional[str] = None


class AiAvatarResponse(BaseModel):
    """虚拟形象响应"""
    id: int
    assistant_id: int
    model_type: str
    name: Optional[str]
    description: Optional[str]

    # Live2D配置
    live2d_model_url: Optional[str]
    live2d_texture_urls: Optional[List[str]]
    live2d_motion_groups: Optional[Dict[str, List[str]]]
    live2d_expression_map: Optional[Dict[str, str]]

    # VRM配置
    vrm_model_url: Optional[str]

    # 位置与缩放
    position_x: float
    position_y: float
    scale: float
    z_index: int

    # 动作配置
    default_motion: str
    speak_motion: str
    idle_motions: Optional[List[str]]

    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============ 动画状态 Schemas ============

class AnimationStateBase(BaseModel):
    """动画状态基础"""
    current_expression: str = "neutral"
    current_motion: str = "idle"
    is_speaking: bool = False
    transition_duration: float = 0.3


class AnimationStateUpdate(BaseModel):
    """更新动画状态"""
    current_expression: Optional[str] = None
    current_motion: Optional[str] = None
    is_speaking: Optional[bool] = None
    transition_duration: Optional[float] = None


class AnimationStateResponse(BaseModel):
    """动画状态响应"""
    id: int
    user_id: int
    assistant_id: int
    current_expression: str
    current_motion: str
    is_speaking: bool
    transition_duration: float
    updated_at: datetime

    class Config:
        from_attributes = True


# ============ 动画请求 Schemas ============

class AnimationRequest(BaseModel):
    """动画请求"""
    assistant_id: Optional[int] = None  # 助手ID
    message: Optional[str] = None
    response: Optional[str] = None
    emotion: Optional[str] = None  # happy, neutral, sad, angry, surprised, excited
    force_expression: Optional[str] = None  # 强制指定表情
    force_motion: Optional[str] = None  # 强制指定动作


class MotionGroup(BaseModel):
    """动作组"""
    name: str
    motions: List[str]


class ExpressionConfig(BaseModel):
    """表情配置"""
    expression: str
    description: str
    applicable_emotions: List[str]


class AnimationResponse(BaseModel):
    """动画响应"""
    expressions: List[str] = []
    motions: List[str] = []
    sound: Optional[str] = None
    duration: Optional[float] = None
    transition_duration: float = 0.3


class AvatarListResponse(BaseModel):
    """虚拟形象列表响应"""
    total: int
    list: List[AiAvatarResponse]


class BuiltInExpression(BaseModel):
    """内置表情"""
    name: str
    label: str
    description: str
    emotions: List[str]


class BuiltInMotion(BaseModel):
    """内置动作"""
    name: str
    label: str
    description: str


class AvatarConfigResponse(BaseModel):
    """虚拟形象配置响应（包含内置表情和动作）"""
    expressions: List[BuiltInExpression]
    motions: List[BuiltInMotion]


# ============ 预设虚拟形象 Schemas ============

class PresetAvatar(BaseModel):
    """预设虚拟形象"""
    assistant_id: int
    assistant_name: str
    mbti_type: str
    personality: str
    default_expression: str
    expressions: Dict[str, str]  # emotion -> expression
    default_motion: str
    motions: Dict[str, str]  # emotion -> motion