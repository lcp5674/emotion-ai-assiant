"""
情绪-动作组合引擎
支持动作序列、并行动作、微表情、过渡效果
"""
import random
import time
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum


class MotionType(Enum):
    """动作类型"""
    PRIMARY = "primary"  # 主要动作
    SECONDARY = "secondary"  # 次要动作
    MICRO = "micro"  # 微动作
    IDLE = "idle"  # 待机动画
    TRANSITION = "transition"  # 过渡动画


class EmotionIntensity(Enum):
    """情绪强度"""
    SLIGHT = 1  # 轻微
    MODERATE = 2  # 中等
    STRONG = 3  # 强烈
    VERY_STRONG = 4  # 非常强烈
    EXTREME = 5  # 极度


@dataclass
class MotionFrame:
    """动作帧 - 用于序列动画"""
    motion: str
    expression: Optional[str] = None
    duration: float = 0.5  # 持续时间（秒）
    transition_in: float = 0.1  # 进入过渡
    transition_out: float = 0.1  # 退出过渡
    motion_type: MotionType = MotionType.PRIMARY
    weight: float = 1.0  # 权重（用于混合）


@dataclass
class AnimationState:
    """动画状态"""
    current_emotion: str = "neutral"
    current_intensity: int = 1
    current_expression: str = "neutral"
    current_motion: str = "idle"
    last_update_time: float = field(default_factory=time.time)
    motion_history: List[Tuple[str, float]] = field(default_factory=list)  # (motion_name, timestamp)
    idle_counter: int = 0


class EmotionMotionEngine:
    """情绪-动作组合引擎"""

    def __init__(self):
        self.state = AnimationState()
        self._motion_cooldown = {}  # 动作冷却时间
        self._expression_cooldown = {}  # 表情冷却时间

    # 动作组合配置
    MOTION_COMBINATIONS = {
        # 开心组合
        "happy_joy": ["smile_small", "happy", "clap", "jump"],
        "happy_excited": ["wave", "happy", "clap", "spin"],
        # 悲伤组合
        "sad_simple": ["sad", "slump", "cry"],
        "sad_lonely": ["sad", "hug_self", "look_around", "curl_up"],
        # 愤怒组合
        "angry_light": ["frown", "shake_head"],
        "angry_strong": ["frown", "shake_head", "clench_fist", "stamp_foot"],
        # 思考组合
        "thinking_deep": ["thinking", "touch_chin", "look_up", "pace_slow"],
        # 好奇组合
        "curious_intense": ["tilt_head", "lean_forward", "look_closer", "raise_eyebrow"],
        # 惊讶组合
        "surprised_mild": ["eyes_wide", "jump_small"],
        "surprised_strong": ["eyes_wide", "jump_small", "gasp", "cover_mouth"],
    }

    # 微表情配置
    MICRO_EXPRESSIONS = {
        "positive": ["smile", "happy", "blink"],
        "negative": ["frown", "sad", "look_down"],
        "neutral": ["blink", "look_around"],
    }

    # 动作兼容性表 - 哪些动作可以并行
    COMPATIBLE_MOTIONS = {
        "idle": ["blink", "look_around", "smile_small"],
        "happy": ["clap", "wave", "smile"],
        "sad": ["cry", "cover_face"],
        "thinking": ["touch_chin", "look_up", "pace_slow"],
        "speaking": ["nod", "gesture", "smile"],
    }

    # 动作冷却时间（秒）
    MOTION_COOLDOWN_TIME = {
        "jump": 5.0,
        "spin": 8.0,
        "clap": 3.0,
        "stamp_foot": 10.0,
        "cry": 15.0,
        "laugh": 5.0,
    }

    def generate_motion_sequence(
        self,
        emotion: str,
        intensity: int,
        duration: float = 3.0,
        mbti_type: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> List[MotionFrame]:
        """
        生成动作序列
        
        Args:
            emotion: 情绪名称
            intensity: 情绪强度 1-5
            duration: 序列总时长
            mbti_type: MBTI类型
            context: 上下文信息
            
        Returns:
            动作帧列表
        """
        frames = []
        current_time = 0.0
        
        # 根据情绪和强度选择组合模板
        template = self._select_template(emotion, intensity)
        
        if not template:
            # 没有模板，创建简单序列
            frame = MotionFrame(
                motion="idle",
                expression="neutral",
                duration=duration,
                motion_type=MotionType.PRIMARY,
            )
            frames.append(frame)
            return frames
        
        # 计算每个动作的持续时间
        frame_duration = max(0.3, duration / len(template))
        
        for i, motion in enumerate(template):
            # 检查冷却
            if not self._can_play_motion(motion):
                continue
            
            # 选择表情
            expression = self._get_expression_for_motion(motion, emotion, intensity)
            
            # 创建帧
            frame = MotionFrame(
                motion=motion,
                expression=expression,
                duration=frame_duration,
                transition_in=0.1 if i > 0 else 0.2,
                transition_out=0.1 if i < len(template) - 1 else 0.3,
                motion_type=MotionType.PRIMARY if i == 0 else MotionType.SECONDARY,
            )
            frames.append(frame)
            current_time += frame_duration
            
            # 更新冷却
            self._update_cooldown(motion)
        
        # 添加微表情
        if len(frames) > 0:
            self._add_micro_expressions(frames, emotion)
        
        return frames

    def _select_template(self, emotion: str, intensity: int) -> List[str]:
        """根据情绪和强度选择组合模板"""
        emotion = emotion.lower()
        
        # 积极情绪模板
        if emotion in ["joy", "happy", "content"]:
            if intensity >= 4:
                return self.MOTION_COMBINATIONS.get("happy_joy", [])
            elif intensity >= 2:
                return ["smile_small", "happy", "clap"]
            else:
                return ["smile_small", "happy"]
        
        elif emotion == "excited":
            if intensity >= 4:
                return self.MOTION_COMBINATIONS.get("happy_excited", [])
            else:
                return ["wave", "happy", "clap"]
        
        # 消极情绪模板
        elif emotion == "sad":
            if intensity >= 4:
                return self.MOTION_COMBINATIONS.get("sad_simple", [])
            elif intensity >= 2:
                return ["sad", "slump"]
            else:
                return ["sad"]
        
        elif emotion == "lonely":
            if intensity >= 3:
                return self.MOTION_COMBINATIONS.get("sad_lonely", [])
            else:
                return ["sad", "hug_self"]
        
        elif emotion == "angry":
            if intensity >= 4:
                return self.MOTION_COMBINATIONS.get("angry_strong", [])
            elif intensity >= 2:
                return self.MOTION_COMBINATIONS.get("angry_light", [])
            else:
                return ["frown"]
        
        # 中性情绪模板
        elif emotion == "thinking":
            if intensity >= 3:
                return self.MOTION_COMBINATIONS.get("thinking_deep", [])
            else:
                return ["thinking", "touch_chin"]
        
        elif emotion == "curious":
            if intensity >= 3:
                return self.MOTION_COMBINATIONS.get("curious_intense", [])
            else:
                return ["tilt_head", "lean_forward"]
        
        elif emotion == "surprised":
            if intensity >= 4:
                return self.MOTION_COMBINATIONS.get("surprised_strong", [])
            else:
                return self.MOTION_COMBINATIONS.get("surprised_mild", [])
        
        # 默认模板
        return ["idle"]

    def _get_expression_for_motion(self, motion: str, emotion: str, intensity: int) -> str:
        """根据动作和情绪选择表情"""
        expression_map = {
            # 积极
            "smile_small": "smile",
            "happy": "happy",
            "clap": "happy",
            "jump": "excited",
            "wave": "happy",
            "laugh": "laugh",
            # 消极
            "sad": "sad",
            "slump": "sad",
            "cry": "sad",
            "frown": "angry",
            "shake_head": "angry",
            "clench_fist": "angry",
            # 中性
            "thinking": "thinking",
            "touch_chin": "thinking",
            "tilt_head": "curious",
            "surprised": "surprised",
        }
        
        return expression_map.get(motion, "neutral")

    def _can_play_motion(self, motion: str) -> bool:
        """检查动作是否在冷却中"""
        cooldown_time = self.MOTION_COOLDOWN_TIME.get(motion, 0)
        if cooldown_time == 0:
            return True
        
        last_played = self._motion_cooldown.get(motion, 0)
        return time.time() - last_played >= cooldown_time

    def _update_cooldown(self, motion: str) -> None:
        """更新动作冷却时间"""
        if motion in self.MOTION_COOLDOWN_TIME:
            self._motion_cooldown[motion] = time.time()

    def _add_micro_expressions(self, frames: List[MotionFrame], emotion: str) -> None:
        """向序列添加微表情"""
        if not frames:
            return
        
        # 确定情绪大类
        emotion_category = "neutral"
        if emotion in ["joy", "happy", "excited", "love", "content"]:
            emotion_category = "positive"
        elif emotion in ["sad", "angry", "fearful", "anxious"]:
            emotion_category = "negative"
        
        micros = self.MICRO_EXPRESSIONS.get(emotion_category, [])
        
        if micros and len(frames) > 1:
            # 在中间插入微表情帧
            insert_pos = len(frames) // 2
            micro_frame = MotionFrame(
                motion=frames[insert_pos].motion,  # 保持原有动作
                expression=random.choice(micros),
                duration=0.2,
                motion_type=MotionType.MICRO,
            )
            frames.insert(insert_pos, micro_frame)

    def generate_idle_sequence(
        self,
        mbti_type: Optional[str] = None,
        time_since_active: int = 0,
    ) -> List[MotionFrame]:
        """
        生成待机动画序列
        
        Args:
            mbti_type: MBTI类型
            time_since_active: 距离上次活跃的时间（秒）
            
        Returns:
            待机动画帧列表
        """
        frames = []
        
        # 基础待机
        idle_pool = ["idle", "idle_2", "idle_3", "idle_4", "blink"]
        
        # 根据时间增加变化
        if time_since_active > 30:
            idle_pool.extend(["stretch", "look_around", "shift_feet"])
        if time_since_active > 60:
            idle_pool.extend(["yawn", "smile_small", "sigh_content"])
        
        # 生成3-5个待机动作
        num_frames = random.randint(3, 5)
        for i in range(num_frames):
            motion = random.choice(idle_pool)
            frame = MotionFrame(
                motion=motion,
                expression="neutral",
                duration=random.uniform(1.0, 2.5),
                motion_type=MotionType.IDLE,
            )
            frames.append(frame)
        
        return frames

    def generate_transition(
        self,
        from_emotion: str,
        to_emotion: str,
        duration: float = 0.5,
    ) -> List[MotionFrame]:
        """
        生成情绪过渡序列
        
        Args:
            from_emotion: 起始情绪
            to_emotion: 目标情绪
            duration: 过渡时长
            
        Returns:
            过渡帧列表
        """
        frames = []
        
        # 过渡到中性
        frame1 = MotionFrame(
            motion="idle",
            expression="neutral",
            duration=duration * 0.4,
            transition_in=0.1,
            transition_out=0.1,
            motion_type=MotionType.TRANSITION,
        )
        frames.append(frame1)
        
        # 中性保持
        frame2 = MotionFrame(
            motion="idle",
            expression="neutral",
            duration=duration * 0.2,
            motion_type=MotionType.TRANSITION,
        )
        frames.append(frame2)
        
        return frames

    def get_compatible_motions(self, primary_motion: str) -> List[str]:
        """获取与主动作兼容的次动作列表"""
        for key, compatibles in self.COMPATIBLE_MOTIONS.items():
            if key in primary_motion or primary_motion in key:
                return compatibles
        return []

    def update_state(
        self,
        emotion: str,
        intensity: int,
        motion: str,
        expression: str,
    ) -> None:
        """更新引擎状态"""
        # 记录历史
        self.state.motion_history.append((motion, time.time()))
        # 只保留最近20个
        if len(self.state.motion_history) > 20:
            self.state.motion_history = self.state.motion_history[-20:]
        
        # 更新当前状态
        self.state.current_emotion = emotion
        self.state.current_intensity = intensity
        self.state.current_motion = motion
        self.state.current_expression = expression
        self.state.last_update_time = time.time()

    def get_state(self) -> Dict[str, Any]:
        """获取当前状态"""
        return {
            "current_emotion": self.state.current_emotion,
            "current_intensity": self.state.current_intensity,
            "current_expression": self.state.current_expression,
            "current_motion": self.state.current_motion,
            "time_since_update": time.time() - self.state.last_update_time,
            "recent_motions": [m[0] for m in self.state.motion_history[-5:]],
        }


# 单例
_engine_instance: Optional[EmotionMotionEngine] = None


def get_emotion_motion_engine() -> EmotionMotionEngine:
    """获取情绪-动作引擎单例"""
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = EmotionMotionEngine()
    return _engine_instance
