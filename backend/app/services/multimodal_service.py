"""
多模态交互服务
提供图片理解、表情反应、动图分享等多模态交互功能
"""
from typing import Dict, Any, Optional, List
import base64
import io
from datetime import datetime
from app.core.config import settings


class MultimodalService:
    """多模态交互服务"""
    
    def __init__(self):
        self.supported_image_formats = ['jpg', 'jpeg', 'png', 'gif', 'webp']
        self.max_image_size = 10 * 1024 * 1024  # 10MB
    
    def analyze_image(
        self,
        image_data: str,
        image_format: str,
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        分析用户上传的图片
        
        Args:
            image_data: base64编码的图片数据
            image_format: 图片格式
            user_id: 用户ID
            
        Returns:
            图片分析结果
        """
        # 验证图片格式
        if image_format.lower() not in self.supported_image_formats:
            return {
                "success": False,
                "error": "不支持的图片格式"
            }
        
        # 解码图片
        try:
            image_bytes = base64.b64decode(image_data)
        except Exception as e:
            return {
                "success": False,
                "error": "图片解码失败"
            }
        
        # 验证图片大小
        if len(image_bytes) > self.max_image_size:
            return {
                "success": False,
                "error": "图片大小超过限制"
            }
        
        # 这里调用图片分析AI服务
        # 实际项目中需要集成图片理解API
        
        # 模拟分析结果
        analysis_result = {
            "success": True,
            "image_type": "photo",
            "description": "这是一张生活照片",
            "emotional_tone": "positive",
            "suggested_reactions": ["😊", "🌟", "❤️"],
            "analysis_timestamp": datetime.utcnow().isoformat()
        }
        
        return analysis_result
    
    def get_emotional_reactions(
        self,
        emotion_context: Optional[str] = None,
        mood_level: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        根据情绪上下文获取合适的表情反应
        
        Args:
            emotion_context: 情绪上下文
            mood_level: 情绪级别
            
        Returns:
            表情反应列表
        """
        # 基础表情库
        reaction_library = [
            {"emoji": "😊", "name": "微笑", "moods": ["happy", "neutral"]},
            {"emoji": "😄", "name": "开心", "moods": ["happy", "very_happy"]},
            {"emoji": "❤️", "name": "爱心", "moods": ["happy", "very_happy"]},
            {"emoji": "🌟", "name": "星星", "moods": ["happy", "very_happy"]},
            {"emoji": "😌", "name": "平静", "moods": ["neutral"]},
            {"emoji": "🤔", "name": "思考", "moods": ["neutral"]},
            {"emoji": "😔", "name": "难过", "moods": ["sad", "very_sad"]},
            {"emoji": "🫂", "name": "拥抱", "moods": ["sad", "very_sad"]},
            {"emoji": "💪", "name": "加油", "moods": ["sad", "neutral", "happy"]},
            {"emoji": "🌈", "name": "彩虹", "moods": ["happy", "very_happy"]},
        ]
        
        # 根据情绪筛选
        if mood_level:
            mood_level = mood_level.lower()
            filtered_reactions = [
                r for r in reaction_library 
                if mood_level in r["moods"]
            ]
        else:
            filtered_reactions = reaction_library
        
        return filtered_reactions
    
    def generate_sticker_suggestion(
        self,
        conversation_context: str,
        user_mood: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        生成适合当前对话的动图/贴纸建议
        
        Args:
            conversation_context: 对话上下文
            user_mood: 用户情绪
            
        Returns:
            贴纸建议列表
        """
        # 贴纸库
        sticker_library = [
            {
                "id": "encouragement_1",
                "name": "加油打气",
                "category": "encouragement",
                "url": "/stickers/encouragement_1.gif",
                "tags": ["加油", "鼓励", "支持"]
            },
            {
                "id": "happy_1",
                "name": "开心庆祝",
                "category": "happy",
                "url": "/stickers/happy_1.gif",
                "tags": ["开心", "庆祝", "快乐"]
            },
            {
                "id": "comfort_1",
                "name": "温暖安慰",
                "category": "comfort",
                "url": "/stickers/comfort_1.gif",
                "tags": ["安慰", "温暖", "拥抱"]
            },
            {
                "id": "thinking_1",
                "name": "认真思考",
                "category": "thinking",
                "url": "/stickers/thinking_1.gif",
                "tags": ["思考", "认真", "专注"]
            },
        ]
        
        # 根据上下文关键词匹配
        suggestions = []
        context_lower = conversation_context.lower()
        
        for sticker in sticker_library:
            # 检查是否有匹配的标签
            if any(tag in context_lower for tag in sticker["tags"]):
                suggestions.append(sticker)
        
        # 如果没有匹配的，返回默认推荐
        if not suggestions:
            suggestions = sticker_library[:3]
        
        return suggestions
    
    def share_image_with_annotation(
        self,
        image_data: str,
        image_format: str,
        annotation: Optional[str] = None,
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        分享带有注释的图片
        
        Args:
            image_data: 图片数据
            image_format: 图片格式
            annotation: 注释文本
            user_id: 用户ID
            
        Returns:
            分享结果
        """
        # 这里实现图片分享逻辑
        # 实际项目中需要保存图片并生成分享链接
        
        share_result = {
            "success": True,
            "share_url": f"/shared/images/{datetime.utcnow().timestamp()}",
            "annotation": annotation,
            "shared_at": datetime.utcnow().isoformat()
        }
        
        return share_result
    
    def voice_to_emoji(
        self,
        voice_text: str,
        emotion_intensity: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        将语音内容转换为合适的表情
        
        Args:
            voice_text: 语音转文字的结果
            emotion_intensity: 情绪强度
            
        Returns:
            表情列表
        """
        # 关键词到表情的映射
        keyword_emoji_map = {
            "开心": ["😊", "😄", "🎉"],
            "快乐": ["😊", "🌟", "🎊"],
            "难过": ["😔", "😢", "🫂"],
            "悲伤": ["😔", "😢", "💔"],
            "生气": ["😠", "💢", "😤"],
            "愤怒": ["😠", "💢", "😤"],
            "害怕": ["😨", "😰", "🙀"],
            "恐惧": ["😨", "😰", "🙀"],
            "惊喜": ["😲", "🎉", "✨"],
            "惊讶": ["😲", "😮", "🙀"],
            "爱": ["❤️", "💕", "💖"],
            "喜欢": ["❤️", "💕", "👍"],
        }
        
        # 查找匹配的关键词
        matched_emojis = set()
        voice_text_lower = voice_text.lower()
        
        for keyword, emojis in keyword_emoji_map.items():
            if keyword in voice_text_lower:
                matched_emojis.update(emojis)
        
        # 如果没有匹配，返回默认表情
        if not matched_emojis:
            matched_emojis = {"😊", "🤔", "👍"}
        
        # 构建结果
        result = []
        for emoji in list(matched_emojis)[:5]:
            result.append({
                "emoji": emoji,
                "confidence": 0.8 if matched_emojis else 0.5
            })
        
        return result


def get_multimodal_service() -> MultimodalService:
    """获取多模态交互服务实例"""
    return MultimodalService()
