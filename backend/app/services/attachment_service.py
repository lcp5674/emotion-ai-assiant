"""
依恋风格服务
"""
from typing import List, Dict, Optional, Any
from datetime import datetime
import loguru

from sqlalchemy.orm import Session


class AttachmentService:
    """依恋风格服务"""

    # 依恋风格配置
    STYLES = {
        "安全型": {
            "description": "你对自己和他人都有积极的看法，能够健康地建立亲密关系。",
            "characteristics": [
                "对自己有信心",
                "信任伴侣",
                "能够开放地表达需求",
                "在亲密和独立之间平衡良好",
            ],
            "relationship_tips": "继续保持开放和信任的沟通方式，这会帮助你建立健康稳定的关系。",
            "self_growth_tips": "继续发展情绪智力，保持关系的新鲜感。",
        },
        "焦虑型": {
            "description": "你对他人有积极的看法，但对自己缺乏信心，容易担心关系的稳定性。",
            "characteristics": [
                "渴望亲密",
                "担心被抛弃",
                "过度关注伴侣",
                "情绪波动较大",
            ],
            "relationship_tips": "试着建立自己的安全感和独立性，学会在不确认伴侣状态时也能保持平静。",
            "self_growth_tips": "建立自我价值感，学会独处，减少对伴侣的过度依赖。",
        },
        "回避型": {
            "description": "你对自己有积极的看法，但对他人缺乏信任，倾向于保持情感距离。",
            "characteristics": [
                "重视独立",
                "难以表达情感",
                "回避亲密",
                "对关系持矛盾态度",
            ],
            "relationship_tips": "试着逐渐开放自己，允许自己依赖伴侣，你会发现亲密关系可以带来更多满足。",
            "self_growth_tips": "学会信任他人，开放情感表达，接受亲密关系。",
        },
        "混乱型": {
            "description": "你对自我和他人都缺乏稳定的看法，关系模式不稳定，容易在亲密和回避之间摇摆。",
            "characteristics": [
                "对关系既渴望又恐惧",
                "情绪极度不稳定",
                "难以预测的行为",
                "强烈的依恋需求",
            ],
            "relationship_tips": "建议寻求专业心理咨询帮助，学习情绪调节和人际关系技巧，建立更健康的关系模式。",
            "self_growth_tips": "建立稳定的自我认同，学习情绪调节，寻求专业支持。",
        },
    }

    def get_questions(self, db: Session) -> List[Any]:
        """获取依恋风格题目"""
        from app.models import AttachmentQuestion
        return db.query(AttachmentQuestion).filter(
            AttachmentQuestion.is_active == True
        ).order_by(AttachmentQuestion.question_no).all()

    def calculate_result(self, db: Session, user_id: int, answers: List[Dict]) -> Dict[str, Any]:
        """计算依恋风格结果"""
        from app.models import AttachmentQuestion, AttachmentStyle
        
        anxiety_score = 0.0
        avoidance_score = 0.0
        anxiety_count = 0
        avoidance_count = 0
        
        for answer in answers:
            question_id = answer["question_id"]
            score = answer.get("score", answer.get("answer", 0))
            
            # 如果是字符串，转换为数字
            if isinstance(score, str):
                try:
                    score = int(score)
                except:
                    score = 1
            
            question = db.query(AttachmentQuestion).filter(
                AttachmentQuestion.id == question_id
            ).first()
            
            if not question:
                continue
            
            # 计算焦虑维度得分
            if question.anxiety_weight > 0:
                anxiety_score += score * question.anxiety_weight
                anxiety_count += 1
            
            # 计算回避维度得分
            if question.avoidance_weight > 0:
                avoidance_score += score * question.avoidance_weight
                avoidance_count += 1
        
        # 归一化得分到1-7范围
        if anxiety_count > 0:
            anxiety_score = anxiety_score / anxiety_count
        if avoidance_count > 0:
            avoidance_score = avoidance_score / avoidance_count
        
        # 确定依恋风格
        style = self._determine_style(anxiety_score, avoidance_score)
        style_config = self.STYLES.get(style, self.STYLES["安全型"])
        
        return {
            "style": style,
            "anxiety_score": round(anxiety_score, 2),
            "avoidance_score": round(avoidance_score, 2),
            "attachment_style": AttachmentStyle[style.upper().replace("型", "")],
            "characteristics": style_config["characteristics"],
            "relationship_tips": style_config["relationship_tips"],
            "self_growth_tips": style_config["self_growth_tips"],
        }

    def _determine_style(self, anxiety_score: float, avoidance_score: float) -> str:
        """根据得分确定依恋风格"""
        # 基于中位数划分（焦虑和回避的中位数约为3.5）
        if anxiety_score <= 3.5 and avoidance_score <= 3.5:
            return "安全型"
        elif anxiety_score > 3.5 and avoidance_score <= 3.5:
            return "焦虑型"
        elif anxiety_score <= 3.5 and avoidance_score > 3.5:
            return "回避型"
        else:
            return "混乱型"

    def seed_questions(self, db: Session, force: bool = False) -> None:
        """初始化依恋风格题目"""
        from app.models import AttachmentQuestion
        
        if not force and db.query(AttachmentQuestion).first():
            return
        
        if force:
            db.query(AttachmentQuestion).delete()
        
        questions_data = self._get_questions_data()
        
        for q in questions_data:
            db.add(AttachmentQuestion(**q))
        
        db.commit()
        loguru.logger.info(f"Attachment questions seeded: {len(questions_data)} questions")

    def _get_questions_data(self) -> List[Dict]:
        """获取10道依恋风格题目"""
        return [
            # 焦虑维度题目 (5题)
            {
                "question_no": 1,
                "question_text": "当伴侣没有及时回复消息时，我会担心是不是自己做错了什么",
                "anxiety_weight": 1.0,
                "avoidance_weight": 0.0,
            },
            {
                "question_no": 2,
                "question_text": "在一段关系中，我最担心的是被抛弃或被拒绝",
                "anxiety_weight": 1.0,
                "avoidance_weight": 0.0,
            },
            {
                "question_no": 3,
                "question_text": "当伴侣需要长时间出差时，我会感到非常不安和担心",
                "anxiety_weight": 1.0,
                "avoidance_weight": 0.0,
            },
            {
                "question_no": 4,
                "question_text": "在争吵后，我会非常担心关系的未来",
                "anxiety_weight": 1.0,
                "avoidance_weight": 0.0,
            },
            {
                "question_no": 5,
                "question_text": "我需要伴侣经常表达爱意来让我感到安心",
                "anxiety_weight": 1.0,
                "avoidance_weight": 0.0,
            },
            # 回避维度题目 (5题)
            {
                "question_no": 6,
                "question_text": "当关系变得越来越亲密时，我会感到有些不舒服，想要退后",
                "anxiety_weight": 0.0,
                "avoidance_weight": 1.0,
            },
            {
                "question_no": 7,
                "question_text": "我倾向于保持独立，不过度依赖他人",
                "anxiety_weight": 0.0,
                "avoidance_weight": 1.0,
            },
            {
                "question_no": 8,
                "question_text": "当伴侣向我表达强烈的情感时，我会感到压力，想要回避",
                "anxiety_weight": 0.0,
                "avoidance_weight": 1.0,
            },
            {
                "question_no": 9,
                "question_text": "谈论自己的感受对我来说比较困难，不习惯",
                "anxiety_weight": 0.0,
                "avoidance_weight": 1.0,
            },
            {
                "question_no": 10,
                "question_text": "在建立亲密关系之前，我会观望一段时间，确保安全",
                "anxiety_weight": 0.0,
                "avoidance_weight": 1.0,
            },
        ]


# 全局服务实例
_attachment_service: Optional[AttachmentService] = None


def get_attachment_service() -> AttachmentService:
    """获取依恋风格服务实例"""
    global _attachment_service
    if _attachment_service is None:
        _attachment_service = AttachmentService()
    return _attachment_service
