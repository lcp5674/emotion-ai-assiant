"""
情感分析服务 - 增强版
支持24种细粒度情绪分类和情绪强度检测
"""
import re
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass
from enum import Enum


class EmotionCategory(Enum):
    """细粒度情绪分类（24种）"""
    # 积极情绪
    JOY = "joy"  # 喜悦
    EXCITED = "excited"  # 兴奋
    GRATEFUL = "grateful"  # 感恩
    HOPEFUL = "hopeful"  # 充满希望
    PROUD = "proud"  # 自豪
    AMUSED = "amused"  # 被逗乐
    CONTENT = "content"  # 满足
    LOVE = "love"  # 爱
    
    # 消极情绪
    SAD = "sad"  # 悲伤
    ANGRY = "angry"  # 愤怒
    FRUSTRATED = "frustrated"  # 沮丧
    ANXIOUS = "anxious"  # 焦虑
    FEARFUL = "fearful"  # 害怕
    GUILTY = "guilty"  # 内疚
    ASHAMED = "ashamed"  # 羞愧
    LONELY = "lonely"  # 孤独
    
    # 中性情绪
    NEUTRAL = "neutral"  # 中性
    THINKING = "thinking"  # 思考
    CURIOUS = "curious"  # 好奇
    SURPRISED = "surprised"  # 惊讶
    CONFUSED = "confused"  # 困惑
    BORED = "bored"  # 无聊
    TIRED = "tired"  # 疲惫
    RELIEVED = "relieved"  # 松了一口气


@dataclass
class EmotionIntensity:
    """情绪强度"""
    level: int  # 1-5
    label: str  # "轻微" | "中等" | "强烈" | "非常强烈" | "极度"


class EmotionKeywords:
    """情绪关键词库"""
    
    # 积极情绪关键词
    POSITIVE_WORDS = {
        EmotionCategory.JOY: ["开心", "高兴", "快乐", "幸福", "喜悦", "愉快", "开心极了", "乐",
                              "happy", "joy", "delighted", "pleased", "blissful"],
        EmotionCategory.EXCITED: ["激动", "兴奋", "热血沸腾", "亢奋", "心潮澎湃", "迫不及待",
                                  "excited", "thrilled", "ecstatic", "enthusiastic"],
        EmotionCategory.GRATEFUL: ["感谢", "感恩", "感激", "谢谢", "幸好", "多亏",
                                    "grateful", "thankful", "appreciative"],
        EmotionCategory.HOPEFUL: ["希望", "期待", "憧憬", "乐观", "有信心", "相信",
                                  "hopeful", "optimistic", "expectant"],
        EmotionCategory.PROUD: ["自豪", "骄傲", "得意", "成就感", "了不起",
                                "proud", "accomplished", "triumphant"],
        EmotionCategory.AMUSED: ["好笑", "有趣", "逗乐", "哈哈", "笑死", "好玩",
                                  "amused", "funny", "hilarious", "entertained"],
        EmotionCategory.CONTENT: ["满足", "安心", "踏实", "惬意", "舒服", "挺好",
                                  "content", "satisfied", "peaceful", "at ease"],
        EmotionCategory.LOVE: ["爱", "喜欢", "喜欢上", "心动", "甜蜜", "温暖",
                              "love", "adore", "cherish", "affectionate"],
    }
    
    # 消极情绪关键词
    NEGATIVE_WORDS = {
        EmotionCategory.SAD: ["难过", "伤心", "悲伤", "痛苦", "难受", "心碎", "失落",
                              "sad", "sorrowful", "grieving", "heartbroken"],
        EmotionCategory.ANGRY: ["生气", "愤怒", "恼火", "气愤", "怒", "火大", "不爽",
                                "angry", "furious", "enraged", "irritated"],
        EmotionCategory.FRUSTRATED: ["沮丧", "失望", "郁闷", "不顺心", "糟糕", "烦",
                                      "frustrated", "disappointed", "discouraged"],
        EmotionCategory.ANXIOUS: ["焦虑", "担心", "紧张", "不安", "忐忑", "忧心",
                                  "anxious", "worried", "nervous", "apprehensive"],
        EmotionCategory.FEARFUL: ["害怕", "恐惧", "恐慌", "可怕", "吓人", "不敢",
                                  "fearful", "scared", "afraid", "terrified"],
        EmotionCategory.GUILTY: ["内疚", "愧疚", "对不起", "抱歉", "后悔", "自责",
                                  "guilty", "remorseful", "regretful"],
        EmotionCategory.ASHAMED: ["羞愧", "丢脸", "尴尬", "不好意思", "羞于",
                                   "ashamed", "embarrassed", "humiliated"],
        EmotionCategory.LONELY: ["孤独", "寂寞", "孤单", "一个人", "没人陪",
                                  "lonely", "isolated", "alone"],
    }
    
    # 中性情绪关键词
    NEUTRAL_WORDS = {
        EmotionCategory.NEUTRAL: ["嗯", "哦", "好吧", "随便", "都行",
                                  "neutral", "okay", "fine", "whatever"],
        EmotionCategory.THINKING: ["想想", "思考", "考虑", "琢磨", "让我想想",
                                    "thinking", "wondering", "contemplating"],
        EmotionCategory.CURIOUS: ["好奇", "想知道", "问问", "什么", "怎么",
                                  "curious", "wondering", "inquisitive"],
        EmotionCategory.SURPRISED: ["惊讶", "震惊", "意外", "哇", "天哪",
                                     "surprised", "shocked", "amazed", "wow"],
        EmotionCategory.CONFUSED: ["困惑", "不懂", "不明白", "糊涂", "搞不清",
                                    "confused", "puzzled", "perplexed"],
        EmotionCategory.BORED: ["无聊", "没劲", "没意思", "枯燥", "乏味",
                                "bored", "tedious", "dull"],
        EmotionCategory.TIRED: ["累", "疲惫", "疲倦", "困", "不想动",
                                "tired", "exhausted", "fatigued", "sleepy"],
        EmotionCategory.RELIEVED: ["松了口气", "放心了", "还好", "幸好",
                                    "relieved", "thank goodness", "whew"],
    }


# 否定词列表
NEGATION_WORDS = [
    '不', '没', '不是', '不会', '不能', '不要', '不太', '并未',
    '一点都', '绝不', '从未', '尚未', '未', '莫', '别', '休',
    'non', 'no', 'not', "n't", 'never', 'neither', 'nobody', 'nothing',
]

# 程度词及其强化倍数
DEGREE_WORDS = {
    '非常': 1.5, '极其': 1.8, '特别': 1.5, '十分': 1.5,
    '超': 1.6, '格外': 1.4, '及其': 1.7, '极为': 1.8, '太': 1.4,
    '好': 1.3, '真': 1.3, '实在': 1.3, '确实': 1.2, '的确': 1.2,
    '相当': 1.3, '颇为': 1.2, '尤其': 1.4, '最': 1.8, '最为': 1.8,
    '更': 1.2, '更加': 1.3, '越': 1.2, '越来越': 1.3,
    '略微': 0.5, '稍微': 0.5, '有点': 0.7, '有些': 0.7,
    '一点': 0.6, '一点点': 0.4, '略': 0.5, '微微': 0.4,
}

# 反问句模式
RHETORICAL_PATTERNS = [
    r'^(怎么|怎能|怎么可能|怎能会|为何|为什么|难道|岂不是)',
    r'[吗|呢|吧|啊]$',
    r'这不是.+吗',
    r'难道不.+吗',
    r'何必要|何必',
]


class EnhancedSentimentService:
    """增强版情感分析服务"""

    def __init__(self):
        self._snownlp = None
        self._initialized = False

    def _initialize(self):
        """延迟初始化 snownlp"""
        if self._initialized:
            return

        try:
            from snownlp import SnowNLP
            self._snownlp = SnowNLP
            self._initialized = True
            print("Snownlp 情感分析模块加载成功!")
        except ImportError:
            print("snownlp 库未安装，使用规则匹配作为后备方案")
            self._initialized = True  # 标记已初始化(以后备模式)

    @property
    def snownlp(self):
        if not self._initialized:
            self._initialize()
        return self._snownlp

    def _calculate_intensity(self, score: float, has_degree: bool = False, degree_multiplier: float = 1.0) -> EmotionIntensity:
        """根据分数计算情绪强度"""
        # 应用程度词倍数
        adjusted_score = min(1.0, score * degree_multiplier)
        
        if adjusted_score < 0.2:
            return EmotionIntensity(level=1, label="轻微")
        elif adjusted_score < 0.4:
            return EmotionIntensity(level=2, label="中等")
        elif adjusted_score < 0.6:
            return EmotionIntensity(level=3, label="强烈")
        elif adjusted_score < 0.8:
            return EmotionIntensity(level=4, label="非常强烈")
        else:
            return EmotionIntensity(level=5, label="极度")

    def _detect_negation_and_degree(self, text: str, keyword_pos: int) -> Tuple[bool, float]:
        """检测关键词前后的否定词和程度词"""
        before_text = text[max(0, keyword_pos - 15):keyword_pos]
        
        has_negation = any(neg in before_text for neg in NEGATION_WORDS)
        
        degree_multiplier = 1.0
        for deg, mult in DEGREE_WORDS.items():
            if deg in before_text:
                degree_multiplier = max(degree_multiplier, mult)
        
        return has_negation, degree_multiplier

    def _rule_based_analyze(self, text: str) -> Dict[str, Any]:
        """基于规则的细粒度情感分析"""
        if not text or not text.strip():
            return self._neutral_result()

        text = text.strip()
        text_lower = text.lower()
        
        emotion_scores: Dict[EmotionCategory, float] = {}
        keyword_count = 0
        
        # 检测积极情绪
        for emotion, keywords in EmotionKeywords.POSITIVE_WORDS.items():
            for keyword in keywords:
                if keyword in text_lower:
                    keyword_pos = text_lower.find(keyword)
                    has_negation, degree_mult = self._detect_negation_and_degree(text, keyword_pos)
                    
                    base_score = 0.3 + (0.1 * keyword_count)  # 多个关键词累加
                    if has_negation:
                        base_score = -base_score
                    
                    emotion_scores[emotion] = emotion_scores.get(emotion, 0) + base_score
                    keyword_count += 1
        
        # 检测消极情绪
        for emotion, keywords in EmotionKeywords.NEGATIVE_WORDS.items():
            for keyword in keywords:
                if keyword in text_lower:
                    keyword_pos = text_lower.find(keyword)
                    has_negation, degree_mult = self._detect_negation_and_degree(text, keyword_pos)
                    
                    base_score = -0.3 - (0.1 * keyword_count)
                    if has_negation:
                        base_score = -base_score
                    
                    emotion_scores[emotion] = emotion_scores.get(emotion, 0) + base_score
                    keyword_count += 1
        
        # 检测中性情绪
        for emotion, keywords in EmotionKeywords.NEUTRAL_WORDS.items():
            for keyword in keywords:
                if keyword in text_lower:
                    emotion_scores[emotion] = emotion_scores.get(emotion, 0) + 0.2
                    keyword_count += 1
        
        # 检测反问句
        is_rhetorical = any(re.search(p, text) for p in RHETORICAL_PATTERNS)
        if is_rhetorical:
            # 反问句反转主要情绪
            for emotion in list(emotion_scores.keys()):
                emotion_scores[emotion] *= -0.8
        
        # 找出得分最高的情绪
        if emotion_scores:
            primary_emotion = max(emotion_scores.items(), key=lambda x: abs(x[1]))
            emotion, score = primary_emotion
            
            # 计算情绪强度
            intensity = self._calculate_intensity(abs(score), keyword_count > 1)
            
            return self._format_result(emotion, score, intensity)
        else:
            return self._neutral_result()

    def _neutral_result(self) -> Dict[str, Any]:
        """返回中性结果"""
        return {
            'label': 'neutral',
            'emotion': EmotionCategory.NEUTRAL.value,
            'emotion_category': 'neutral',
            'expression': 'neutral',
            'motion': 'idle',
            'intensity': {'level': 1, 'label': '轻微'},
            'confidence': 0.5,
            'secondary_emotions': [],
        }

    def _format_result(self, emotion: EmotionCategory, score: float, intensity: EmotionIntensity) -> Dict[str, Any]:
        """格式化输出结果"""
        # 确定情绪大类
        if emotion in EmotionKeywords.POSITIVE_WORDS:
            emotion_category = 'positive'
        elif emotion in EmotionKeywords.NEGATIVE_WORDS:
            emotion_category = 'negative'
        else:
            emotion_category = 'neutral'
        
        # 根据情绪和强度选择表情和动作
        expression, motion = self._get_expression_and_motion(emotion, intensity.level)
        
        # 计算置信度
        confidence = min(0.95, 0.4 + abs(score) * 0.5)
        
        return {
            'label': emotion_category,
            'emotion': emotion.value,
            'emotion_category': emotion_category,
            'expression': expression,
            'motion': motion,
            'intensity': {'level': intensity.level, 'label': intensity.label},
            'confidence': confidence,
            'secondary_emotions': self._get_secondary_emotions(emotion),
        }

    def _get_expression_and_motion(self, emotion: EmotionCategory, intensity: int) -> Tuple[str, str]:
        """根据情绪和强度获取表情和动作"""
        # 表情映射
        expression_map = {
            # 积极情绪
            EmotionCategory.JOY: 'happy',
            EmotionCategory.EXCITED: 'excited',
            EmotionCategory.GRATEFUL: 'smile',
            EmotionCategory.HOPEFUL: 'hopeful',
            EmotionCategory.PROUD: 'proud',
            EmotionCategory.AMUSED: 'laugh',
            EmotionCategory.CONTENT: 'smile',
            EmotionCategory.LOVE: 'love',
            
            # 消极情绪
            EmotionCategory.SAD: 'sad',
            EmotionCategory.ANGRY: 'angry',
            EmotionCategory.FRUSTRATED: 'frustrated',
            EmotionCategory.ANXIOUS: 'anxious',
            EmotionCategory.FEARFUL: 'fearful',
            EmotionCategory.GUILTY: 'guilty',
            EmotionCategory.ASHAMED: 'ashamed',
            EmotionCategory.LONELY: 'lonely',
            
            # 中性情绪
            EmotionCategory.NEUTRAL: 'neutral',
            EmotionCategory.THINKING: 'thinking',
            EmotionCategory.CURIOUS: 'curious',
            EmotionCategory.SURPRISED: 'surprised',
            EmotionCategory.CONFUSED: 'confused',
            EmotionCategory.BORED: 'bored',
            EmotionCategory.TIRED: 'tired',
            EmotionCategory.RELIEVED: 'relieved',
        }
        
        # 动作映射（根据强度变化）
        motion_map = {
            # 积极情绪
            EmotionCategory.JOY: ['idle', 'nod', 'happy', 'clap', 'jump'],
            EmotionCategory.EXCITED: ['idle', 'wave', 'happy', 'clap', 'spin'],
            EmotionCategory.GRATEFUL: ['idle', 'nod', 'bow', 'wave', 'clap'],
            EmotionCategory.HOPEFUL: ['idle', 'thinking', 'look_up', 'clench_fist', 'raise_arm'],
            EmotionCategory.PROUD: ['idle', 'stand_tall', 'puff_chest', 'arms_akimbo', 'victory'],
            EmotionCategory.AMUSED: ['idle', 'smile', 'laugh', 'clap', 'shake_laughter'],
            EmotionCategory.CONTENT: ['idle', 'relax', 'sigh_content', 'stretch', 'lean_back'],
            EmotionCategory.LOVE: ['idle', 'smile', 'hand_on_heart', 'wave', 'hug_air'],
            
            # 消极情绪
            EmotionCategory.SAD: ['idle', 'sad', 'slump', 'cry', 'cover_face'],
            EmotionCategory.ANGRY: ['idle', 'frown', 'shake_head', 'clench_fist', 'stamp_foot'],
            EmotionCategory.FRUSTRATED: ['idle', 'sigh', 'shake_head', 'run_hand', 'throw_arms'],
            EmotionCategory.ANXIOUS: ['idle', 'fidget', 'pace', 'bite_lip', 'wring_hands'],
            EmotionCategory.FEARFUL: ['idle', 'tremble', 'cower', 'cover_face', 'back_away'],
            EmotionCategory.GUILTY: ['idle', 'look_down', 'shift_feet', 'hang_head', 'cover_face'],
            EmotionCategory.ASHAMED: ['idle', 'blush', 'look_away', 'cover_face', 'hide'],
            EmotionCategory.LONELY: ['idle', 'hug_self', 'look_around', 'reach_out', 'curl_up'],
            
            # 中性情绪
            EmotionCategory.NEUTRAL: ['idle', 'blink', 'idle_2', 'idle_3', 'idle_4'],
            EmotionCategory.THINKING: ['idle', 'thinking', 'touch_chin', 'look_up', 'pace_slow'],
            EmotionCategory.CURIOUS: ['idle', 'tilt_head', 'lean_forward', 'look_closer', 'raise_eyebrow'],
            EmotionCategory.SURPRISED: ['idle', 'jump_small', 'gasp', 'cover_mouth', 'eyes_wide'],
            EmotionCategory.CONFUSED: ['idle', 'tilt_head', 'scratch_head', 'shrug', 'look_around'],
            EmotionCategory.BORED: ['idle', 'yawn', 'stretch', 'look_away', 'tap_foot'],
            EmotionCategory.TIRED: ['idle', 'stretch', 'yawn', 'slump', 'rub_eyes'],
            EmotionCategory.RELIEVED: ['idle', 'sigh_relief', 'shoulders_drop', 'smile_small', 'lean_back'],
        }
        
        expression = expression_map.get(emotion, 'neutral')
        motions = motion_map.get(emotion, ['idle'])
        motion_index = min(intensity - 1, len(motions) - 1)
        motion = motions[motion_index]
        
        return expression, motion

    def _get_secondary_emotions(self, primary_emotion: EmotionCategory) -> List[str]:
        """获取次要情绪列表"""
        secondary_map = {
            # 积极情绪的次要情绪
            EmotionCategory.JOY: [EmotionCategory.CONTENT.value, EmotionCategory.AMUSED.value],
            EmotionCategory.EXCITED: [EmotionCategory.JOY.value, EmotionCategory.PROUD.value],
            EmotionCategory.GRATEFUL: [EmotionCategory.CONTENT.value, EmotionCategory.JOY.value],
            EmotionCategory.HOPEFUL: [EmotionCategory.OPTIMISTIC.value if hasattr(EmotionCategory, 'OPTIMISTIC') else EmotionCategory.THINKING.value, EmotionCategory.CURIOUS.value],
            EmotionCategory.PROUD: [EmotionCategory.JOY.value, EmotionCategory.CONFIDENT.value if hasattr(EmotionCategory, 'CONFIDENT') else EmotionCategory.CONTENT.value],
            EmotionCategory.AMUSED: [EmotionCategory.JOY.value, EmotionCategory.SURPRISED.value],
            EmotionCategory.CONTENT: [EmotionCategory.JOY.value, EmotionCategory.RELIEVED.value],
            EmotionCategory.LOVE: [EmotionCategory.JOY.value, EmotionCategory.GRATEFUL.value],
            
            # 消极情绪的次要情绪
            EmotionCategory.SAD: [EmotionCategory.LONELY.value, EmotionCategory.FRUSTRATED.value],
            EmotionCategory.ANGRY: [EmotionCategory.FRUSTRATED.value, EmotionCategory.SURPRISED.value],
            EmotionCategory.FRUSTRATED: [EmotionCategory.SAD.value, EmotionCategory.ANGRY.value],
            EmotionCategory.ANXIOUS: [EmotionCategory.FEARFUL.value, EmotionCategory.CONFUSED.value],
            EmotionCategory.FEARFUL: [EmotionCategory.ANXIOUS.value, EmotionCategory.SURPRISED.value],
            EmotionCategory.GUILTY: [EmotionCategory.SAD.value, EmotionCategory.ASHAMED.value],
            EmotionCategory.ASHAMED: [EmotionCategory.GUILTY.value, EmotionCategory.LONELY.value],
            EmotionCategory.LONELY: [EmotionCategory.SAD.value, EmotionCategory.BORED.value],
        }
        
        return secondary_map.get(primary_emotion, [])

    def analyze(self, text: str) -> Dict[str, Any]:
        """
        分析文本情感 - 增强版
        
        Args:
            text: 输入文本

        Returns:
            情感分析结果 {
                label: 'positive' | 'negative' | 'neutral',
                emotion: 细粒度情绪名称,
                emotion_category: 情绪大类,
                expression: 表情名称,
                motion: 动作名称,
                intensity: {level: 1-5, label: 强度描述},
                confidence: 置信度,
                secondary_emotions: 次要情绪列表,
            }
        """
        if not text or not text.strip():
            return self._neutral_result()

        text = text.strip()

        # 如果 snownlp 可用，组合使用 snownlp 和规则
        if self.snownlp is not None:
            try:
                s = self.snownlp(text)
                sentiment_score = s.sentiments  # 0-1 范围，0.5 是中性
                
                print(f"Snownlp情感分析: text={text[:30]}..., score={sentiment_score:.3f}")
                
                # 使用规则分析获取细粒度情绪
                rule_result = self._rule_based_analyze(text)
                
                # 结合两种结果
                rule_confidence = rule_result['confidence']
                if rule_confidence > 0.6:
                    # 规则分析置信度高，使用规则结果
                    return rule_result
                else:
                    # 否则，使用 snownlp 修正规则结果
                    return self._combine_results(rule_result, sentiment_score)
                    
            except Exception as e:
                print(f"Snownlp分析失败: {e}，使用规则匹配")
        
        # 后备：规则匹配
        return self._rule_based_analyze(text)

    def _combine_results(self, rule_result: Dict[str, Any], snownlp_score: float) -> Dict[str, Any]:
        """结合规则分析和snownlp的结果"""
        # 调整置信度
        rule_confidence = rule_result['confidence']
        snownlp_confidence = abs(snownlp_score - 0.5) * 2
        
        combined_confidence = (rule_confidence * 0.7 + snownlp_confidence * 0.3)
        
        # 如果snownlp和规则在情绪大类上有分歧，重新评估
        rule_category = rule_result['emotion_category']
        snownlp_category = 'positive' if snownlp_score > 0.6 else 'negative' if snownlp_score < 0.4 else 'neutral'
        
        if rule_category != snownlp_category and abs(snownlp_score - 0.5) > 0.3:
            # 分歧较大时，返回中性结果
            return self._neutral_result()
        
        rule_result['confidence'] = min(0.95, combined_confidence)
        return rule_result


# 单例
_sentiment_service: Optional[EnhancedSentimentService] = None


def get_sentiment_service() -> EnhancedSentimentService:
    """获取情感分析服务单例"""
    global _sentiment_service
    if _sentiment_service is None:
        _sentiment_service = EnhancedSentimentService()
    return _sentiment_service
