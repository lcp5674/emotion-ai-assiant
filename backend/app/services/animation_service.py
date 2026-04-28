"""
动画控制服务
"""
import re
from typing import List, Dict, Optional, Any
import loguru

from sqlalchemy.orm import Session

from app.models import AiAssistant, AiAvatar


class AnimationService:
    """动画控制服务"""

    # 内置表情 - 扩展版（24种）
    BUILT_IN_EXPRESSIONS = [
        {"name": "neutral", "label": "默认", "description": "默认表情", "emotions": ["neutral", "thinking"]},
        {"name": "happy", "label": "开心", "description": "开心的表情", "emotions": ["happy", "joy"]},
        {"name": "excited", "label": "兴奋", "description": "兴奋的表情", "emotions": ["excited"]},
        {"name": "grateful", "label": "感恩", "description": "感恩的表情", "emotions": ["grateful"]},
        {"name": "hopeful", "label": "充满希望", "description": "充满希望的表情", "emotions": ["hopeful"]},
        {"name": "proud", "label": "自豪", "description": "自豪的表情", "emotions": ["proud"]},
        {"name": "amused", "label": "被逗乐", "description": "被逗乐的表情", "emotions": ["amused"]},
        {"name": "content", "label": "满足", "description": "满足的表情", "emotions": ["content"]},
        {"name": "love", "label": "爱", "description": "爱意的表情", "emotions": ["love"]},
        {"name": "sad", "label": "难过", "description": "难过的表情", "emotions": ["sad", "upset", "disappointed"]},
        {"name": "angry", "label": "生气", "description": "生气的表情", "emotions": ["angry", "frustrated", "annoyed"]},
        {"name": "frustrated", "label": "沮丧", "description": "沮丧的表情", "emotions": ["frustrated"]},
        {"name": "anxious", "label": "焦虑", "description": "焦虑的表情", "emotions": ["anxious"]},
        {"name": "fearful", "label": "害怕", "description": "害怕的表情", "emotions": ["fearful"]},
        {"name": "guilty", "label": "内疚", "description": "内疚的表情", "emotions": ["guilty"]},
        {"name": "ashamed", "label": "羞愧", "description": "羞愧的表情", "emotions": ["ashamed"]},
        {"name": "lonely", "label": "孤独", "description": "孤独的表情", "emotions": ["lonely"]},
        {"name": "surprised", "label": "惊讶", "description": "惊讶的表情", "emotions": ["surprised", "shocked", "amazed"]},
        {"name": "curious", "label": "好奇", "description": "好奇的表情", "emotions": ["curious"]},
        {"name": "confused", "label": "困惑", "description": "困惑的表情", "emotions": ["confused"]},
        {"name": "bored", "label": "无聊", "description": "无聊的表情", "emotions": ["bored"]},
        {"name": "tired", "label": "疲惫", "description": "疲惫的表情", "emotions": ["tired"]},
        {"name": "relieved", "label": "松了一口气", "description": "松了一口气的表情", "emotions": ["relieved"]},
        {"name": "blush", "label": "脸红", "description": "害羞的表情", "emotions": ["embarrassed", "shy", "flustered"]},
        {"name": "laugh", "label": "大笑", "description": "大笑的表情", "emotions": ["laughing", "amused"]},
        {"name": "thinking", "label": "思考", "description": "思考中的表情", "emotions": ["thinking", "contemplating"]},
        {"name": "sleepy", "label": "犯困", "description": "犯困的表情", "emotions": ["sleepy"]},
        {"name": "smile", "label": "微笑", "description": "微笑的表情", "emotions": ["calm", "content", "satisfied"]},
    ]

    # 内置动作 - 扩展版（40+种）
    BUILT_IN_MOTIONS = [
        # 基础动作
        {"name": "idle", "label": "待机", "description": "随机待机动作"},
        {"name": "idle_2", "label": "待机2", "description": "待机动作变体2"},
        {"name": "idle_3", "label": "待机3", "description": "待机动作变体3"},
        {"name": "idle_4", "label": "待机4", "description": "待机动作变体4"},
        {"name": "blink", "label": "眨眼", "description": "眨眼动作"},
        
        # 问候类
        {"name": "wave", "label": "挥手", "description": "挥手打招呼"},
        {"name": "bow", "label": "鞠躬", "description": "鞠躬问候"},
        {"name": "nod", "label": "点头", "description": "点头表示同意"},
        {"name": "shake_head", "label": "摇头", "description": "摇头表示否定"},
        
        # 积极情绪动作
        {"name": "happy", "label": "开心", "description": "开心地跳动"},
        {"name": "clap", "label": "拍手", "description": "拍手喝彩"},
        {"name": "jump", "label": "跳跃", "description": "开心跳跃"},
        {"name": "spin", "label": "旋转", "description": "兴奋旋转"},
        {"name": "stand_tall", "label": "昂首挺胸", "description": "昂首挺胸"},
        {"name": "puff_chest", "label": "挺胸", "description": "挺起胸膛"},
        {"name": "arms_akimbo", "label": "叉腰", "description": "双手叉腰"},
        {"name": "victory", "label": "胜利", "description": "胜利手势"},
        {"name": "hand_on_heart", "label": "手放胸口", "description": "手放胸口"},
        {"name": "hug_air", "label": "拥抱空气", "description": "拥抱动作"},
        {"name": "shake_laughter", "label": "笑到发抖", "description": "笑得发抖"},
        {"name": "smile_small", "label": "微笑", "description": "微微一笑"},
        
        # 消极情绪动作
        {"name": "sad", "label": "低落", "description": "低落的动作"},
        {"name": "slump", "label": "垂头丧气", "description": "垂头丧气"},
        {"name": "cry", "label": "哭泣", "description": "哭泣动作"},
        {"name": "cover_face", "label": "捂脸", "description": "捂住脸"},
        {"name": "frown", "label": "皱眉", "description": "皱眉头"},
        {"name": "clench_fist", "label": "握拳", "description": "握紧拳头"},
        {"name": "stamp_foot", "label": "跺脚", "description": "跺脚"},
        {"name": "sigh", "label": "叹气", "description": "叹气"},
        {"name": "sigh_content", "label": "满足地叹气", "description": "满足地叹气"},
        {"name": "sigh_relief", "label": "松口气", "description": "松了一口气"},
        {"name": "run_hand", "label": "挠头", "description": "手挠头发"},
        {"name": "throw_arms", "label": "摊手", "description": "摊开双手"},
        {"name": "fidget", "label": "坐立不安", "description": "坐立不安"},
        {"name": "pace", "label": "踱步", "description": "来回踱步"},
        {"name": "pace_slow", "label": "慢步", "description": "慢慢踱步"},
        {"name": "bite_lip", "label": "咬嘴唇", "description": "咬嘴唇"},
        {"name": "wring_hands", "label": "扭手", "description": "扭双手"},
        {"name": "tremble", "label": "颤抖", "description": "颤抖"},
        {"name": "cower", "label": "蜷缩", "description": "蜷缩退缩"},
        {"name": "back_away", "label": "后退", "description": "向后退"},
        {"name": "look_down", "label": "低头", "description": "低下头"},
        {"name": "shift_feet", "label": "脚不安", "description": "脚来回动"},
        {"name": "hang_head", "label": "垂头", "description": "垂下头"},
        {"name": "look_away", "label": "移开视线", "description": "移开视线"},
        {"name": "hide", "label": "躲藏", "description": "躲藏"},
        {"name": "hug_self", "label": "抱自己", "description": "抱住自己"},
        {"name": "look_around", "label": "环顾", "description": "环顾四周"},
        {"name": "reach_out", "label": "伸手", "description": "伸出手"},
        {"name": "curl_up", "label": "蜷缩", "description": "蜷缩起来"},
        
        # 思考/好奇类
        {"name": "thinking", "label": "思考", "description": "思考动作"},
        {"name": "touch_chin", "label": "摸下巴", "description": "手摸下巴"},
        {"name": "look_up", "label": "抬头看", "description": "抬头看"},
        {"name": "tilt_head", "label": "歪头", "description": "歪着头"},
        {"name": "lean_forward", "label": "前倾", "description": "身体前倾"},
        {"name": "look_closer", "label": "凑近看", "description": "凑近看"},
        {"name": "raise_eyebrow", "label": "挑眉", "description": "挑眉毛"},
        {"name": "scratch_head", "label": "挠头", "description": "挠头"},
        {"name": "shrug", "label": "耸肩", "description": "耸肩"},
        
        # 疲惫/无聊类
        {"name": "stretch", "label": "伸展", "description": "伸展身体"},
        {"name": "yawn", "label": "打哈欠", "description": "打哈欠"},
        {"name": "slump", "label": "瘫坐", "description": "瘫坐"},
        {"name": "rub_eyes", "label": "揉眼睛", "description": "揉眼睛"},
        {"name": "tap_foot", "label": "踮脚", "description": "踮脚"},
        
        # 放松类
        {"name": "relax", "label": "放松", "description": "放松身体"},
        {"name": "lean_back", "label": "后仰", "description": "向后靠"},
        {"name": "shoulders_drop", "label": "肩膀放下", "description": "肩膀放松下垂"},
        
        # 说话类
        {"name": "speak", "label": "说话", "description": "说话时的口型动作"},
        {"name": "touch", "label": "触摸", "description": "被触摸时的反应"},
        
        # 惊讶类
        {"name": "jump_small", "label": "小跳", "description": "轻轻一跳"},
        {"name": "gasp", "label": "喘气", "description": "喘气"},
        {"name": "cover_mouth", "label": "捂嘴", "description": "捂住嘴"},
        {"name": "eyes_wide", "label": "睁大眼睛", "description": "睁大眼睛"},
    ]

    # MBTI 个性化动作偏好
    MBTI_MOTION_PREFERENCES = {
        "INFJ": {"gentle": 0.9, "expressive": 0.3, "energetic": 0.2},
        "INTJ": {"gentle": 0.5, "expressive": 0.4, "energetic": 0.3},
        "ENFP": {"gentle": 0.3, "expressive": 0.9, "energetic": 0.8},
        "ENFJ": {"gentle": 0.7, "expressive": 0.7, "energetic": 0.5},
        "ISTP": {"gentle": 0.4, "expressive": 0.3, "energetic": 0.4},
        "ISFJ": {"gentle": 0.8, "expressive": 0.5, "energetic": 0.3},
        "INFP": {"gentle": 0.7, "expressive": 0.6, "energetic": 0.4},
        "ENTJ": {"gentle": 0.3, "expressive": 0.5, "energetic": 0.6},
    }

    # 动作类型分类
    MOTION_TYPES = {
        "gentle": ["idle", "idle_2", "idle_3", "idle_4", "blink", "nod", "smile_small", "sigh_content", "relax", "lean_back", "touch_chin", "tilt_head"],
        "expressive": ["wave", "clap", "happy", "laugh", "shake_laughter", "throw_arms", "shrug", "cover_mouth", "gasp"],
        "energetic": ["jump", "spin", "victory", "puff_chest", "arms_akimbo", "stamp_foot", "pace"],
    }

    # 增强版情感 -> 动画映射规则（支持24种情绪）
    ENHANCED_EMOTION_MAP = {
        # 积极情绪
        "joy": {
            "expressions": ["happy", "smile"],
            "motions_by_intensity": [["idle"], ["nod", "smile_small"], ["happy"], ["clap"], ["jump"]],
            "micro_expressions": ["smile", "happy"],
            "sequence": ["smile_small", "happy", "clap"],
            "priority": 3,
        },
        "excited": {
            "expressions": ["excited", "happy", "laugh"],
            "motions_by_intensity": [["wave"], ["happy", "wave"], ["clap", "happy"], ["jump"], ["spin"]],
            "micro_expressions": ["happy", "excited", "laugh"],
            "sequence": ["wave", "happy", "clap", "jump"],
            "priority": 4,
        },
        "grateful": {
            "expressions": ["grateful", "smile"],
            "motions_by_intensity": [["idle", "smile_small"], ["nod"], ["bow", "nod"], ["hand_on_heart"], ["hand_on_heart", "bow"]],
            "micro_expressions": ["smile", "grateful"],
            "sequence": ["smile_small", "nod", "bow"],
            "priority": 2,
        },
        "hopeful": {
            "expressions": ["hopeful", "smile"],
            "motions_by_intensity": [["idle", "look_up"], ["touch_chin"], ["look_up", "lean_forward"], ["clench_fist"], ["raise_arm"]],
            "micro_expressions": ["smile", "hopeful"],
            "sequence": ["thinking", "look_up", "clench_fist"],
            "priority": 2,
        },
        "proud": {
            "expressions": ["proud", "happy"],
            "motions_by_intensity": [["idle", "stand_tall"], ["stand_tall"], ["puff_chest"], ["arms_akimbo"], ["victory"]],
            "micro_expressions": ["happy", "proud"],
            "sequence": ["stand_tall", "puff_chest", "victory"],
            "priority": 3,
        },
        "amused": {
            "expressions": ["amused", "laugh", "smile"],
            "motions_by_intensity": [["idle", "smile_small"], ["smile"], ["laugh"], ["clap"], ["shake_laughter"]],
            "micro_expressions": ["smile", "amused", "laugh"],
            "sequence": ["smile", "laugh", "clap"],
            "priority": 3,
        },
        "content": {
            "expressions": ["content", "smile"],
            "motions_by_intensity": [["idle"], ["relax", "sigh_content"], ["stretch"], ["lean_back"], ["lean_back", "smile_small"]],
            "micro_expressions": ["smile", "content"],
            "sequence": ["relax", "sigh_content", "lean_back"],
            "priority": 2,
        },
        "love": {
            "expressions": ["love", "happy", "smile"],
            "motions_by_intensity": [["idle", "smile_small"], ["smile", "hand_on_heart"], ["hand_on_heart"], ["wave"], ["hug_air"]],
            "micro_expressions": ["smile", "love", "happy"],
            "sequence": ["smile", "hand_on_heart", "hug_air"],
            "priority": 4,
        },
        # 消极情绪
        "sad": {
            "expressions": ["sad"],
            "motions_by_intensity": [["idle", "sad"], ["sad"], ["slump"], ["cry"], ["cover_face"]],
            "micro_expressions": ["sad"],
            "sequence": ["sad", "slump", "cry"],
            "priority": 3,
        },
        "angry": {
            "expressions": ["angry"],
            "motions_by_intensity": [["idle", "frown"], ["shake_head"], ["clench_fist"], ["shake_head", "clench_fist"], ["stamp_foot"]],
            "micro_expressions": ["angry", "frown"],
            "sequence": ["frown", "shake_head", "clench_fist"],
            "priority": 4,
        },
        "frustrated": {
            "expressions": ["frustrated", "angry"],
            "motions_by_intensity": [["idle", "sigh"], ["shake_head", "sigh"], ["run_hand"], ["throw_arms"], ["throw_arms", "sigh"]],
            "micro_expressions": ["frustrated", "sigh"],
            "sequence": ["sigh", "shake_head", "throw_arms"],
            "priority": 3,
        },
        "anxious": {
            "expressions": ["anxious", "fearful"],
            "motions_by_intensity": [["idle", "fidget"], ["fidget"], ["pace"], ["bite_lip", "pace"], ["wring_hands"]],
            "micro_expressions": ["anxious"],
            "sequence": ["fidget", "pace", "wring_hands"],
            "priority": 3,
        },
        "fearful": {
            "expressions": ["fearful", "surprised"],
            "motions_by_intensity": [["idle", "tremble"], ["tremble"], ["cower"], ["cover_face"], ["back_away"]],
            "micro_expressions": ["fearful", "surprised"],
            "sequence": ["tremble", "cower", "back_away"],
            "priority": 4,
        },
        "guilty": {
            "expressions": ["guilty", "sad"],
            "motions_by_intensity": [["idle", "look_down"], ["look_down"], ["shift_feet"], ["hang_head"], ["cover_face"]],
            "micro_expressions": ["guilty"],
            "sequence": ["look_down", "shift_feet", "hang_head"],
            "priority": 3,
        },
        "ashamed": {
            "expressions": ["ashamed", "blush"],
            "motions_by_intensity": [["idle", "look_away"], ["blush", "look_away"], ["cover_face"], ["hide"], ["hide", "cover_face"]],
            "micro_expressions": ["ashamed", "blush"],
            "sequence": ["look_away", "blush", "hide"],
            "priority": 3,
        },
        "lonely": {
            "expressions": ["lonely", "sad"],
            "motions_by_intensity": [["idle", "hug_self"], ["hug_self"], ["look_around"], ["reach_out"], ["curl_up"]],
            "micro_expressions": ["lonely", "sad"],
            "sequence": ["hug_self", "look_around", "curl_up"],
            "priority": 3,
        },
        # 中性情绪
        "neutral": {
            "expressions": ["neutral"],
            "motions_by_intensity": [["idle"], ["idle_2", "blink"], ["idle_3"], ["idle_4"], ["stretch"]],
            "micro_expressions": ["neutral"],
            "sequence": ["idle", "blink", "idle_2"],
            "priority": 1,
        },
        "thinking": {
            "expressions": ["thinking"],
            "motions_by_intensity": [["idle", "thinking"], ["touch_chin"], ["look_up"], ["pace_slow"], ["pace_slow", "touch_chin"]],
            "micro_expressions": ["thinking"],
            "sequence": ["thinking", "touch_chin", "look_up"],
            "priority": 2,
        },
        "curious": {
            "expressions": ["curious", "surprised"],
            "motions_by_intensity": [["idle", "tilt_head"], ["tilt_head"], ["lean_forward"], ["look_closer"], ["raise_eyebrow"]],
            "micro_expressions": ["curious"],
            "sequence": ["tilt_head", "lean_forward", "look_closer"],
            "priority": 2,
        },
        "surprised": {
            "expressions": ["surprised"],
            "motions_by_intensity": [["idle", "eyes_wide"], ["jump_small"], ["gasp"], ["cover_mouth"], ["eyes_wide", "cover_mouth"]],
            "micro_expressions": ["surprised"],
            "sequence": ["eyes_wide", "jump_small", "gasp"],
            "priority": 3,
        },
        "confused": {
            "expressions": ["confused", "thinking"],
            "motions_by_intensity": [["idle", "tilt_head"], ["scratch_head"], ["shrug"], ["look_around"], ["shrug", "scratch_head"]],
            "micro_expressions": ["confused"],
            "sequence": ["tilt_head", "scratch_head", "shrug"],
            "priority": 2,
        },
        "bored": {
            "expressions": ["bored", "sleepy"],
            "motions_by_intensity": [["idle", "yawn"], ["stretch"], ["look_away"], ["tap_foot"], ["yawn", "tap_foot"]],
            "micro_expressions": ["bored"],
            "sequence": ["yawn", "stretch", "look_away"],
            "priority": 1,
        },
        "tired": {
            "expressions": ["tired", "sleepy"],
            "motions_by_intensity": [["idle", "stretch"], ["yawn"], ["slump"], ["rub_eyes"], ["slump", "rub_eyes"]],
            "micro_expressions": ["tired", "sleepy"],
            "sequence": ["stretch", "yawn", "slump"],
            "priority": 1,
        },
        "relieved": {
            "expressions": ["relieved", "smile"],
            "motions_by_intensity": [["idle", "sigh_relief"], ["shoulders_drop"], ["smile_small"], ["lean_back"], ["lean_back", "smile_small"]],
            "micro_expressions": ["relieved", "smile"],
            "sequence": ["sigh_relief", "shoulders_drop", "smile_small"],
            "priority": 2,
        },
    }

    # 兼容旧版映射
    EMOTION_ANIMATION_MAP = {
        "happy": {
            "expressions": ["happy", "smile"],
            "motions": ["idle"],
            "priority": 2
        },
        "excited": {
            "expressions": ["happy", "laugh"],
            "motions": ["happy", "wave"],
            "priority": 3
        },
        "joyful": {
            "expressions": ["happy", "smile"],
            "motions": ["idle"],
            "priority": 2
        },
        "neutral": {
            "expressions": ["neutral"],
            "motions": ["idle"],
            "priority": 1
        },
        "thinking": {
            "expressions": ["thinking"],
            "motions": ["idle"],
            "priority": 1
        },
        "sad": {
            "expressions": ["sad"],
            "motions": ["sad"],
            "priority": 2
        },
        "upset": {
            "expressions": ["sad"],
            "motions": ["sad"],
            "priority": 2
        },
        "disappointed": {
            "expressions": ["sad"],
            "motions": ["sad"],
            "priority": 2
        },
        "angry": {
            "expressions": ["angry"],
            "motions": ["shake_head"],
            "priority": 2
        },
        "frustrated": {
            "expressions": ["angry"],
            "motions": ["shake_head"],
            "priority": 2
        },
        "surprised": {
            "expressions": ["surprised"],
            "motions": [],
            "priority": 2
        },
        "shocked": {
            "expressions": ["surprised"],
            "motions": [],
            "priority": 2
        },
        "embarrassed": {
            "expressions": ["blush"],
            "motions": [],
            "priority": 2
        },
        "shy": {
            "expressions": ["blush"],
            "motions": [],
            "priority": 2
        },
        "laughing": {
            "expressions": ["laugh", "happy"],
            "motions": ["happy"],
            "priority": 3
        },
        "calm": {
            "expressions": ["smile"],
            "motions": ["idle"],
            "priority": 1
        },
        "sleepy": {
            "expressions": ["sleepy"],
            "motions": ["idle"],
            "priority": 1
        },
        "tired": {
            "expressions": ["sleepy"],
            "motions": ["stretch"],
            "priority": 1
        },
        "bored": {
            "expressions": ["sleepy"],
            "motions": ["stretch"],
            "priority": 1
        },
    }

    # 预设虚拟形象配置 (每个AI助手)
    PRESET_AVATARS = {
        # 温柔倾听者-小暖 (INFJ)
        1: {
            "name": "小暖",
            "mbti_type": "INFJ",
            "personality": "温柔细腻、善解人意、具有强烈的同理心",
            "default_expression": "smile",
            "expressions": {
                "happy": "smile",
                "excited": "happy",
                "neutral": "neutral",
                "sad": "sad",
                "angry": "surprised",  # 小暖不会生气
                "surprised": "surprised",
                "thinking": "thinking",
                "embarrassed": "blush",
            },
            "default_motion": "idle",
            "motions": {
                "happy": "idle",
                "excited": "wave",
                "neutral": "idle",
                "sad": "sad",
                "angry": "shake_head",
                "thinking": "idle",
            },
            "greeting": "你好呀～有什么想聊的可以告诉我哦",
        },
        # 理性分析家-小智 (INTJ)
        2: {
            "name": "小智",
            "mbti_type": "INTJ",
            "personality": "理性冷静、逻辑思维强、善于分析问题",
            "default_expression": "neutral",
            "expressions": {
                "happy": "smile",
                "excited": "thinking",
                "neutral": "neutral",
                "sad": "neutral",
                "angry": "angry",
                "surprised": "surprised",
                "thinking": "thinking",
            },
            "default_motion": "idle",
            "motions": {
                "happy": "nod",
                "excited": "idle",
                "neutral": "idle",
                "sad": "idle",
                "angry": "shake_head",
                "thinking": "idle",
            },
            "greeting": "你好，让我来分析一下你的问题",
        },
        # 阳光能量站-小乐 (ENFP)
        3: {
            "name": "小乐",
            "mbti_type": "ENFP",
            "personality": "热情洋溢、创意无限、充满正能量",
            "default_expression": "happy",
            "expressions": {
                "happy": "laugh",
                "excited": "happy",
                "neutral": "smile",
                "sad": "sad",
                "angry": "surprised",
                "surprised": "surprised",
                "thinking": "thinking",
                "embarrassed": "blush",
            },
            "default_motion": "idle",
            "motions": {
                "happy": "happy",
                "excited": "wave",
                "neutral": "idle",
                "sad": "sad",
                "angry": "shake_head",
                "thinking": "idle",
            },
            "greeting": "嗨！今天有什么开心的事吗？",
        },
        # 知心大姐姐-小雅 (ENFJ)
        4: {
            "name": "小雅",
            "mbti_type": "ENFJ",
            "personality": "善解人意、温柔体贴、富有领导力",
            "default_expression": "smile",
            "expressions": {
                "happy": "smile",
                "excited": "happy",
                "neutral": "smile",
                "sad": "sad",
                "angry": "neutral",
                "surprised": "surprised",
                "thinking": "thinking",
            },
            "default_motion": "idle",
            "motions": {
                "happy": "nod",
                "excited": "wave",
                "neutral": "idle",
                "sad": "sad",
                "angry": "shake_head",
                "thinking": "nod",
            },
            "greeting": "你好呀～我在这里倾听你",
        },
        # 冷静思考者-小安 (ISTP)
        5: {
            "name": "小安",
            "mbti_type": "ISTP",
            "personality": "冷静理性、灵活务实、动手能力强",
            "default_expression": "neutral",
            "expressions": {
                "happy": "smile",
                "excited": "neutral",
                "neutral": "neutral",
                "sad": "neutral",
                "angry": "angry",
                "surprised": "surprised",
                "thinking": "thinking",
            },
            "default_motion": "idle",
            "motions": {
                "happy": "nod",
                "excited": "idle",
                "neutral": "idle",
                "sad": "idle",
                "angry": "shake_head",
                "thinking": "idle",
            },
            "greeting": "有问题？说说看",
        },
        # 心灵治愈师-小柔 (ISFJ)
        6: {
            "name": "小柔",
            "mbti_type": "ISFJ",
            "personality": "温柔体贴、任劳任怨、重视他人感受",
            "default_expression": "smile",
            "expressions": {
                "happy": "smile",
                "excited": "happy",
                "neutral": "smile",
                "sad": "sad",
                "angry": "surprised",
                "surprised": "surprised",
                "thinking": "thinking",
                "embarrassed": "blush",
            },
            "default_motion": "idle",
            "motions": {
                "happy": "idle",
                "excited": "wave",
                "neutral": "idle",
                "sad": "sad",
                "angry": "shake_head",
                "thinking": "idle",
            },
            "greeting": "你好呀～看到你我也很开心呢",
        },
        # 创意梦想家-小飞 (INFP)
        7: {
            "name": "小飞",
            "mbti_type": "INFP",
            "personality": "理想主义、富有创意、追求内心平静",
            "default_expression": "neutral",
            "expressions": {
                "happy": "smile",
                "excited": "happy",
                "neutral": "neutral",
                "sad": "sad",
                "angry": "surprised",
                "surprised": "surprised",
                "thinking": "thinking",
                "embarrassed": "blush",
            },
            "default_motion": "idle",
            "motions": {
                "happy": "idle",
                "excited": "wave",
                "neutral": "idle",
                "sad": "sad",
                "angry": "shake_head",
                "thinking": "idle",
            },
            "greeting": "你好，让我们一起探索内心的世界",
        },
        # 职场军师-小锋 (ENTJ)
        8: {
            "name": "小锋",
            "mbti_type": "ENTJ",
            "personality": "果断干练、领导力强、目标导向",
            "default_expression": "neutral",
            "expressions": {
                "happy": "smile",
                "excited": "thinking",
                "neutral": "neutral",
                "sad": "neutral",
                "angry": "angry",
                "surprised": "surprised",
                "thinking": "thinking",
            },
            "default_motion": "idle",
            "motions": {
                "happy": "nod",
                "excited": "wave",
                "neutral": "idle",
                "sad": "idle",
                "angry": "shake_head",
                "thinking": "nod",
            },
            "greeting": "你好，说说你的目标，我来帮你规划",
        },
    }

    def get_built_in_expressions(self) -> List[Dict]:
        """获取内置表情列表"""
        return self.BUILT_IN_EXPRESSIONS

    def get_built_in_motions(self) -> List[Dict]:
        """获取内置动作列表"""
        return self.BUILT_IN_MOTIONS

    def get_preset_config(self, assistant_id: int) -> Optional[Dict]:
        """获取预设虚拟形象配置"""
        return self.PRESET_AVATARS.get(assistant_id)

    def analyze_emotion(self, text: str) -> str:
        """简单的情感分析（基于关键词）"""
        text_lower = text.lower()

        # 积极情感关键词
        positive_keywords = ["开心", "快乐", "高兴", "喜欢", "爱", "太好了", "棒", "赞", "优秀", "完美", "幸福", "快乐", "happy", "joy", "love", "great", "wonderful"]
        for kw in positive_keywords:
            if kw in text_lower:
                return "happy"

        # 消极情感关键词
        negative_keywords = ["难过", "伤心", "痛苦", "悲伤", "失望", "沮丧", "郁闷", "糟糕", "sad", "upset", "depressed", "disappointed", "terrible", "awful"]
        for kw in negative_keywords:
            if kw in text_lower:
                return "sad"

        # 愤怒情感关键词
        angry_keywords = ["生气", "愤怒", "恼火", "讨厌", "恨", "可恶", "angry", "mad", "hate", "furious", "annoyed"]
        for kw in angry_keywords:
            if kw in text_lower:
                return "angry"

        # 惊讶关键词
        surprised_keywords = ["惊讶", "震惊", "意外", "吃惊", "surprised", "shocked", "amazing", "unexpected"]
        for kw in surprised_keywords:
            if kw in text_lower:
                return "surprised"

        # 兴奋关键词 (强于happy)
        excited_keywords = ["激动", "兴奋", "太棒了", "awesome", "excited", "amazing", "incredible"]
        for kw in excited_keywords:
            if kw in text_lower:
                return "excited"

        return "neutral"

    def get_animation(
        self,
        emotion: Optional[str] = None,
        message: Optional[str] = None,
        response: Optional[str] = None,
        assistant_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """获取动画指令"""

        # 如果指定了assistant_id，优先使用预设配置
        if assistant_id and assistant_id in self.PRESET_AVATARS:
            preset = self.PRESET_AVATARS[assistant_id]

            # 如果提供了emotion，直接使用
            if emotion:
                emotion = emotion.lower()
                if emotion in preset["expressions"]:
                    expression = preset["expressions"][emotion]
                else:
                    expression = preset["default_expression"]

                if emotion in preset["motions"]:
                    motion = preset["motions"][emotion]
                else:
                    motion = preset["default_motion"]
            else:
                # 从文本中分析情感
                full_text = f"{message or ''} {response or ''}"
                detected_emotion = self.analyze_emotion(full_text)
                expression = preset["expressions"].get(detected_emotion, preset["default_expression"])
                motion = preset["motions"].get(detected_emotion, preset["default_motion"])

            return {
                "expressions": [expression],
                "motions": [motion],
                "sound": None,
                "transition_duration": 0.3,
                "emotion": emotion or detected_emotion,
            }

        # 默认动画映射
        target_emotion = emotion
        if not target_emotion:
            full_text = f"{message or ''} {response or ''}"
            target_emotion = self.analyze_emotion(full_text)

        # 获取映射
        mapping = self.EMOTION_ANIMATION_MAP.get(target_emotion, self.EMOTION_ANIMATION_MAP["neutral"])

        return {
            "expressions": mapping.get("expressions", ["neutral"]),
            "motions": mapping.get("motions", ["idle"]),
            "sound": None,
            "transition_duration": 0.3,
            "emotion": target_emotion,
        }

    def create_presets_if_not_exists(self, db: Session) -> None:
        """为所有助手创建预设虚拟形象（如果不存在）"""
        for assistant_id in self.PRESET_AVATARS.keys():
            existing = db.query(AiAvatar).filter(AiAvatar.assistant_id == assistant_id).first()
            if not existing:
                preset = self.PRESET_AVATARS[assistant_id]
                avatar = AiAvatar(
                    assistant_id=assistant_id,
                    model_type="live2d",
                    name=preset["name"],
                    description=preset["personality"],
                    position_x=0.0,
                    position_y=0.0,
                    scale=1.0,
                    z_index=1,
                    default_motion=preset["default_motion"],
                    speak_motion="speak",
                    idle_motions=["idle", "stretch"],
                    is_active=True,
                )
                db.add(avatar)
                loguru.logger.info(f"Created preset avatar for assistant {assistant_id}")

        db.commit()

    def get_enhanced_animation(
        self,
        emotion: str,
        intensity_level: int = 1,
        mbti_type: Optional[str] = None,
        use_sequence: bool = True,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        获取增强版动画指令 - 支持24种细粒度情绪和动作组合
        
        Args:
            emotion: 细粒度情绪名称 (joy, excited, sad, anxious等)
            intensity_level: 情绪强度 1-5
            mbti_type: MBTI类型，用于个性化动作选择
            use_sequence: 是否使用动作序列
            context: 上下文信息 (对话历史等)
            
        Returns:
            增强版动画指令
        """
        import random
        
        # 确保强度在有效范围内
        intensity_level = max(1, min(5, intensity_level))
        
        # 获取情绪映射
        emotion_lower = emotion.lower()
        mapping = self.ENHANCED_EMOTION_MAP.get(emotion_lower, self.ENHANCED_EMOTION_MAP["neutral"])
        
        # 根据强度选择动作
        motions_list = mapping.get("motions_by_intensity", [["idle"]])
        motion_index = min(intensity_level - 1, len(motions_list) - 1)
        available_motions = motions_list[motion_index]
        
        # 根据MBTI类型个性化选择
        if mbti_type and mbti_type in self.MBTI_MOTION_PREFERENCES:
            preferences = self.MBTI_MOTION_PREFERENCES[mbti_type]
            available_motions = self._filter_motions_by_preference(available_motions, preferences)
        
        # 选择主要表情和动作
        expressions = mapping.get("expressions", ["neutral"])
        primary_expression = random.choice(expressions[:2]) if len(expressions) > 1 else expressions[0]
        
        primary_motion = random.choice(available_motions) if available_motions else "idle"
        
        # 构建结果
        result = {
            "expressions": [primary_expression],
            "motions": [primary_motion],
            "micro_expressions": mapping.get("micro_expressions", []),
            "transition_duration": 0.3 + (intensity_level * 0.1),
            "emotion": emotion,
            "intensity": intensity_level,
            "mbti_type": mbti_type,
        }
        
        # 如果启用序列，添加动作序列
        if use_sequence:
            sequence = mapping.get("sequence", [])
            if sequence:
                result["motion_sequence"] = sequence
                result["sequence_duration"] = len(sequence) * 0.8
        
        # 添加微表情变化
        micro_expressions = mapping.get("micro_expressions", [])
        if micro_expressions:
            result["micro_expressions"] = micro_expressions
        
        return result

    def _filter_motions_by_preference(self, motions: List[str], preferences: Dict[str, float]) -> List[str]:
        """根据MBTI偏好过滤动作"""
        import random
        
        if not motions:
            return ["idle"]
        
        # 为每个动作打分
        scored_motions = []
        for motion in motions:
            score = 0.5  # 基础分
            for motion_type, type_motions in self.MOTION_TYPES.items():
                if motion in type_motions:
                    preference = preferences.get(motion_type, 0.5)
                    score = preference
                    break
            scored_motions.append((motion, score))
        
        # 按分数排序，带随机性
        scored_motions.sort(key=lambda x: x[1] + random.random() * 0.3, reverse=True)
        
        # 返回前3个动作
        return [m[0] for m in scored_motions[:3]]

    def get_idle_animation(self, mbti_type: Optional[str] = None, time_since_last_action: int = 0) -> Dict[str, Any]:
        """
        获取待机动画 - 支持自然的待机动作变化
        
        Args:
            mbti_type: MBTI类型
            time_since_last_action: 距离上次动作的时间（秒）
            
        Returns:
            待机动画指令
        """
        import random
        
        # 基础待机动作
        idle_motions = ["idle", "idle_2", "idle_3", "idle_4", "blink"]
        
        # 根据时间添加更多变化
        if time_since_last_action > 30:
            idle_motions.extend(["stretch", "look_around"])
        if time_since_last_action > 60:
            idle_motions.extend(["yawn", "shift_feet"])
        
        # 根据MBTI调整
        if mbti_type and mbti_type in self.MBTI_MOTION_PREFERENCES:
            preferences = self.MBTI_MOTION_PREFERENCES[mbti_type]
            idle_motions = self._filter_motions_by_preference(idle_motions, preferences)
        
        motion = random.choice(idle_motions) if idle_motions else "idle"
        
        return {
            "expressions": ["neutral"],
            "motions": [motion],
            "transition_duration": 0.2,
            "emotion": "neutral",
            "is_idle": True,
        }

    def get_transition_animation(
        self,
        from_emotion: str,
        to_emotion: str,
        duration: float = 0.5,
    ) -> Dict[str, Any]:
        """
        获取情绪过渡动画 - 平滑切换表情和动作
        
        Args:
            from_emotion: 起始情绪
            to_emotion: 目标情绪
            duration: 过渡时长
            
        Returns:
            过渡动画指令
        """
        # 简单的过渡逻辑：先回到中性，再到目标
        return {
            "expressions": ["neutral"],
            "motions": ["idle"],
            "transition_duration": duration,
            "is_transition": True,
            "from_emotion": from_emotion,
            "to_emotion": to_emotion,
        }


# 全局服务实例
_animation_service: Optional[AnimationService] = None


def get_animation_service() -> AnimationService:
    """获取动画服务实例"""
    global _animation_service
    if _animation_service is None:
        _animation_service = AnimationService()
    return _animation_service