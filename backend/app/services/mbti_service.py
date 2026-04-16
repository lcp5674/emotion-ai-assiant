"""
MBTI测试服务
"""
import json
import uuid
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import loguru

from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models import MbtiQuestion, MbtiAnswer, MbtiResult, AiAssistant
from app.models.mbti import MbtiDimension, MbtiType


class MbtiService:
    """MBTI测试服务"""

    # 维度名称映射
    DIMENSION_MAP = {
        "EI": ("外向", "内向"),
        "SN": ("感觉", "直觉"),
        "TF": ("思维", "情感"),
        "JP": ("判断", "知觉"),
    }

    # MBTI类型描述
    TYPE_DESCRIPTIONS = {
        "ISTJ": {
            "personality": "务实、可靠、有责任感。注重细节，擅长组织和规划。",
            "strengths": ["可靠性", "责任感", "注重细节", "系统性思维"],
            "weaknesses": ["过于保守", "难以接受变化", "有时过于苛刻"],
            "suitable_jobs": ["会计", "审计", "行政管理", "质量管理"],
        },
        "ISFJ": {
            "personality": "忠诚、细心、有同情心。重视传统和秩序。",
            "strengths": ["忠诚可靠", "细心体贴", "勤奋踏实", "善于照顾他人"],
            "weaknesses": ["过度奉献", "回避冲突", "难以拒绝"],
            "suitable_jobs": ["护理", "教育", "行政管理", "人力资源"],
        },
        "INFJ": {
            "personality": "理想主义、有洞察力、富有创意。追求意义和价值。",
            "strengths": ["洞察力", "创造力", "理想主义", "坚持不懈"],
            "weaknesses": ["过于理想化", "难以接受现实", "过度自我牺牲"],
            "suitable_jobs": ["心理咨询", "教育", "创作", "社会工作"],
        },
        "INTJ": {
            "personality": "战略思维、独立分析。追求知识和效率。",
            "strengths": ["战略思维", "独立自主", "分析能力", "追求完美"],
            "weaknesses": ["过于挑剔", "情感内敛", "难以合作"],
            "suitable_jobs": ["战略规划", "科研", "技术开发", "金融分析"],
        },
        "ISTP": {
            "personality": "灵活、实用、善于观察。喜欢动手解决问题。",
            "strengths": ["动手能力", "灵活变通", "冷静分析", "冒险精神"],
            "weaknesses": ["缺乏规划", "回避承诺", "情感表达困难"],
            "suitable_jobs": ["工程技术", "机械操作", "体育", "执法"],
        },
        "ISFP": {
            "personality": "温和、艺术、敏感。重视个人价值和美学。",
            "strengths": ["艺术感", "温柔体贴", "灵活适应", "审美能力"],
            "weaknesses": ["回避冲突", "拖延", "过度敏感"],
            "suitable_jobs": ["艺术设计", "护理", "烹饪", "音乐"],
        },
        "INFP": {
            "personality": "理想主义、富有创意、同理心强。追求内在和谐。",
            "strengths": ["创意", "同理心", "理想主义", "忠诚"],
            "weaknesses": ["逃避现实", "过度理想化", "难以做决定"],
            "suitable_jobs": ["创作", "心理咨询", "教育", "写作"],
        },
        "INTP": {
            "personality": "逻辑思考、抽象思维。追求知识和真理。",
            "strengths": ["逻辑思维", "创新能力", "独立思考", "分析能力"],
            "weaknesses": ["忽略情感", "难以表达", "拖延"],
            "suitable_jobs": ["科研", "技术开发", "哲学", "数据分析"],
        },
        "ESTP": {
            "personality": "活力十足、务实、善于社交。喜欢行动和挑战。",
            "strengths": ["行动力", "社交能力", "务实灵活", "危机处理"],
            "weaknesses": ["缺乏耐心", "冲动", "回避责任"],
            "suitable_jobs": ["销售", "创业", "体育", "演艺"],
        },
        "ESFP": {
            "personality": "热情、表演、活力四射。善于带动气氛。",
            "strengths": ["热情洋溢", "社交能力强", "实际动手", "乐观积极"],
            "weaknesses": ["缺乏计划", "冲动", "难以集中"],
            "suitable_jobs": ["演艺", "销售", "旅游", "活动策划"],
        },
        "ENFP": {
            "personality": "热情创意、灵感丰富、善于激励他人。",
            "strengths": ["创意", "热情", "激励能力", "善于沟通"],
            "weaknesses": ["难以专注", "情绪波动", "回避负面情绪"],
            "suitable_jobs": ["创意", "营销", "教育", "公关"],
        },
        "ENTP": {
            "personality": "创新、辩论、善于思考。喜欢智识挑战。",
            "strengths": ["创新能力", "辩论能力", "善于思考", "多角度思维"],
            "weaknesses": ["争强好胜", "缺乏耐心", "忽视细节"],
            "suitable_jobs": ["创业", "咨询", "法律", "发明"],
        },
        "ESTJ": {
            "personality": "组织能力强、传统务实、注重结果。",
            "strengths": ["组织能力", "执行力", "责任感", "公正"],
            "weaknesses": ["过于死板", "缺乏灵活", "忽视情感"],
            "suitable_jobs": ["管理", "执法", "金融", "军事"],
        },
        "ESFJ": {
            "personality": "社交、传统、关怀。善于照顾他人需求。",
            "strengths": ["社交能力", "关怀他人", "责任感", "团队合作"],
            "weaknesses": ["过度关注他人", "回避冲突", "自我价值感低"],
            "suitable_jobs": ["教育", "护理", "服务", "人力资源"],
        },
        "ENFJ": {
            "personality": "领导才能、同理心强、善于激励。",
            "strengths": ["领导力", "同理心", "激励能力", "沟通能力"],
            "weaknesses": ["过度理想化", "忽视自我", "控制欲"],
            "suitable_jobs": ["管理", "教育", "咨询", "政治"],
        },
        "ENTJ": {
            "personality": "领导力强、决断力高、追求效率。",
            "strengths": ["领导力", "决断力", "战略思维", "执行力"],
            "weaknesses": ["缺乏耐心", "强硬", "忽视情感"],
            "suitable_jobs": ["企业管理", "创业", "法律", "金融"],
        },
    }

    def get_questions(self, db: Session, dimension: Optional[str] = None) -> List[MbtiQuestion]:
        """获取测试题目"""
        query = db.query(MbtiQuestion).filter(MbtiQuestion.is_active == True)
        if dimension:
            query = query.filter(MbtiQuestion.dimension == MbtiDimension[dimension])
        return query.order_by(MbtiQuestion.question_no).all()

    def start_test(self, user_id: int) -> str:
        """开始测试，返回会话ID"""
        return f"mbti_{user_id}_{int(datetime.now().timestamp())}"

    def calculate_result(self, db: Session, user_id: int, answers: List[Dict]) -> Dict[str, Any]:
        """计算MBTI测试结果"""
        # 统计各维度得分
        # A 选项 = 正向倾向（E/S/T/J），累加正分
        # B 选项 = 反向倾向（I/N/F/P），累加负分
        scores = {"EI": 0, "SN": 0, "TF": 0, "JP": 0}
        question_counts = {"EI": 0, "SN": 0, "TF": 0, "JP": 0}

        for answer in answers:
            question = db.query(MbtiQuestion).filter(MbtiQuestion.id == answer["question_id"]).first()
            if not question:
                continue

            dimension = question.dimension.value
            question_counts[dimension] += 1
            if answer["answer"] == "A":
                # A 选项：正向（E/S/T/J）
                scores[dimension] += question.weight_a
            else:
                # B 选项：反向（I/N/F/P）
                scores[dimension] -= question.weight_b

        # 计算最终类型
        mbti_type = ""
        mbti_type += "E" if scores["EI"] > 0 else "I"
        mbti_type += "S" if scores["SN"] > 0 else "N"
        mbti_type += "T" if scores["TF"] > 0 else "F"
        mbti_type += "J" if scores["JP"] > 0 else "P"

        # 获取类型描述
        description = self.TYPE_DESCRIPTIONS.get(mbti_type, {})

        # 计算每个维度的百分比
        # score 范围：[-max_score, +max_score]，其中 max_score = 该维度题目数 × weight（默认1）
        # 映射到 [5, 95]，避免显示 0% 或 100%
        def calc_percentage(score: int, dimension_key: str) -> int:
            max_score = max(question_counts.get(dimension_key, 12), 1)
            # 将 [-max, +max] 线性映射到 [5, 95]
            normalized = (score + max_score) / (2 * max_score)
            percentage = round(normalized * 90 + 5)  # [0,1] → [5, 95]
            return max(5, min(95, percentage))

        return {
            "mbti_type": mbti_type,
            "ei_score": scores["EI"],
            "sn_score": scores["SN"],
            "tf_score": scores["TF"],
            "jp_score": scores["JP"],
            "dimensions": [
                {
                    "dimension": "EI",
                    "score": scores["EI"],
                    "percentage": calc_percentage(scores["EI"], "EI"),
                    "tendency": "外向" if scores["EI"] > 0 else "内向"
                },
                {
                    "dimension": "SN",
                    "score": scores["SN"],
                    "percentage": calc_percentage(scores["SN"], "SN"),
                    "tendency": "感觉" if scores["SN"] > 0 else "直觉"
                },
                {
                    "dimension": "TF",
                    "score": scores["TF"],
                    "percentage": calc_percentage(scores["TF"], "TF"),
                    "tendency": "思维" if scores["TF"] > 0 else "情感"
                },
                {
                    "dimension": "JP",
                    "score": scores["JP"],
                    "percentage": calc_percentage(scores["JP"], "JP"),
                    "tendency": "判断" if scores["JP"] > 0 else "知觉"
                },
            ],
            "personality": description.get("personality", ""),
            "strengths": description.get("strengths", []),
            "weaknesses": description.get("weaknesses", []),
            "suitable_jobs": description.get("suitable_jobs", []),
            "relationship_tips": self._get_relationship_tips(mbti_type),
            "career_advice": self._get_career_advice(mbti_type),
        }

    def _get_relationship_tips(self, mbti_type: str) -> str:
        """获取人际关系建议"""
        tips = {
            "ISTJ": "你在关系中忠诚可靠，但试着多表达感情，让对方感受到你的温暖。",
            "ISFJ": "你总是默默付出，记得也要照顾好自己的需求，学会适度拒绝。",
            "INFJ": "你善于理解他人，但不要总是迁就，保持真实的自我很重要。",
            "INTJ": "你独立思考能力强，试着多倾听伴侣的感受，建立情感连接。",
            "ISTP": "你灵活务实，但不要回避承诺，给关系一些稳定性。",
            "ISFP": "你温柔敏感，你的艺术气质很吸引人，但也要学会表达需求。",
            "INFP": "你理想浪漫，但要注意实际沟通，不要只在脑海里想象。",
            "INTP": "你逻辑强大，试着多表达感情，情感交流同样重要。",
            "ESTP": "你活力四射，但也要学会倾听，给对方表达的空间。",
            "ESFP": "你热情开朗，你的存在总能让气氛活跃，但也要学会独处。",
            "ENFP": "你创意无限，但不要忽视实际行动，试着坚持下去。",
            "ENTP": "你喜欢辩论，但要小心不要伤害到在乎的人。",
            "ESTJ": "你组织能力强，但试着放松一点，接受一些不确定性。",
            "ESFJ": "你照顾他人，但也要学会说不，保护自己的边界。",
            "ENFJ": "你领导力强，但不要试图控制一切，允许他人做自己。",
            "ENTJ": "你决断力强，但试着多考虑他人感受，平衡理性与感性。",
        }
        return tips.get(mbti_type, "保持真实和善良，你会遇到欣赏你的人。")

    def _get_career_advice(self, mbti_type: str) -> str:
        """获取职业建议"""
        advice = {
            "ISTJ": "适合需要细致、可靠、有组织能力的工作，如会计、行政。",
            "ISFJ": "适合服务他人、照顾他人的工作，如护理、教育、社会服务。",
            "INFJ": "适合有意义、能发挥创造力的工作，如心理咨询、创作、教育。",
            "INTJ": "适合需要战略思维和独立分析的工作，如科研、技术管理。",
            "ISTP": "适合需要动手能力、灵活应变的工作，如工程技术、操作类。",
            "ISFP": "适合能发挥艺术天赋的工作，如设计、音乐、艺术创作。",
            "INFP": "适合创造性、有意义的工作，如写作、心理咨询、艺术。",
            "INTP": "适合需要逻辑思考和创新能力的工作，如科研、技术开发。",
            "ESTP": "适合需要行动力、社交能力的工作，如销售、创业、演艺。",
            "ESFP": "适合能发挥热情和表现力的工作，如演艺、销售、服务业。",
            "ENFP": "适合创意性、激励他人的工作，如营销、创意、公关。",
            "ENTP": "适合需要创新和辩论能力的工作，如咨询、创业、法律。",
            "ESTJ": "适合需要组织和领导能力的工作，如管理、金融、行政。",
            "ESFJ": "适合服务他人、团队协作的工作，如教育、服务、人力资源。",
            "ENFJ": "适合领导、激励他人的工作，如管理、教育、咨询。",
            "ENTJ": "适合需要决断力和领导力的工作，如企业管理、创业。",
        }
        return advice.get(mbti_type, "找到你热爱的领域，发挥你的优势。")

    def get_recommended_assistants(
        self,
        db: Session,
        mbti_type: Optional[str] = None,
        tags: Optional[List[str]] = None,
        user_id: Optional[int] = None,
    ) -> List[AiAssistant]:
        """获取推荐的AI助手（支持三位一体综合推荐）"""
        query = db.query(AiAssistant).filter(AiAssistant.is_active == True)

        assistants = query.all()

        # 如果提供了user_id，进行三位一体综合匹配
        if user_id:
            # 获取用户的三项测评结果
            from app.models import User
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                user_profile = self._get_user_personality_profile(db, user)
                # 计算兼容性评分并排序
                scored_assistants = []
                for assistant in assistants:
                    score = self._calculate_compatibility(assistant, user_profile)
                    scored_assistants.append((assistant, score))
                # 按兼容性分数降序排序
                scored_assistants.sort(key=lambda x: x[1], reverse=True)
                return [a[0] for a in scored_assistants]

        # 原有的简单过滤逻辑
        if mbti_type:
            assistants = [a for a in assistants if str(a.mbti_type) == mbti_type]

        return assistants

    def _get_user_personality_profile(self, db: Session, user: 'User') -> dict:
        """获取用户的人格画像（MBTI + SBTI + 依恋风格）"""
        profile = {
            'mbti': None,
            'sbti': [],
            'attachment': None,
        }

        # 获取MBTI结果
        if user.mbti_type:
            profile['mbti'] = str(user.mbti_type)

        # 获取SBTI结果
        if user.sbti_result_id:
            from app.models import SBTIResult
            sbti_result = db.query(SBTIResult).filter(SBTIResult.id == user.sbti_result_id).first()
            if sbti_result:
                # 获取得分最高的前三个主题
                themes = [
                    sbti_result.top_theme_1,
                    sbti_result.top_theme_2,
                    sbti_result.top_theme_3,
                ]
                profile['sbti'] = [t for t in themes if t]

        # 获取依恋风格结果
        if user.attachment_result_id:
            from app.models import AttachmentResult
            attachment_result = db.query(AttachmentResult).filter(AttachmentResult.id == user.attachment_result_id).first()
            if attachment_result:
                profile['attachment'] = attachment_result.attachment_style

        return profile

    def _calculate_compatibility(self, assistant: 'AiAssistant', user_profile: dict) -> float:
        """计算助手与用户的兼容性评分（0-100）"""
        score = 0.0
        weights = {'mbti': 40, 'sbti': 35, 'attachment': 25}

        # MBTI匹配（40%权重）
        if user_profile['mbti'] and str(assistant.mbti_type) == user_profile['mbti']:
            score += weights['mbti']
        elif user_profile['mbti']:
            # 部分匹配：检查第一个字母是否相同（能量方向）
            if str(assistant.mbti_type)[0] == user_profile['mbti'][0]:
                score += weights['mbti'] * 0.3

        # SBTI匹配（35%权重）
        if user_profile['sbti'] and assistant.sbti_types:
            assistant_sbti = [s.strip() for s in assistant.sbti_types.split(',') if s.strip()]
            matches = sum(1 for s in user_profile['sbti'] if s in assistant_sbti)
            if matches > 0:
                score += (matches / len(user_profile['sbti'])) * weights['sbti']

        # 依恋风格匹配（25%权重）
        if user_profile['attachment'] and assistant.attachment_styles:
            assistant_attach = [a.strip() for a in assistant.attachment_styles.split(',') if a.strip()]
            if user_profile['attachment'] in assistant_attach:
                score += weights['attachment']
            # 安全型依恋可以与其他类型较好匹配
            elif user_profile['attachment'] == 'secure' and len(assistant_attach) > 0:
                score += weights['attachment'] * 0.3

        # 如果助手有推荐标记，增加分数
        if assistant.is_recommended:
            score += 5

        return min(score, 100)

    def seed_questions(self, db: Session, force: bool = False) -> None:
        """初始化MBTI题目"""
        if not force and db.query(MbtiQuestion).first():
            return
        if force:
            db.query(MbtiQuestion).delete()

        questions_data = []

        ei_data = self._get_ei_questions()
        sn_data = self._get_sn_questions()
        tf_data = self._get_tf_questions()
        jp_data = self._get_jp_questions()

        for i, q in enumerate(ei_data, 1):
            questions_data.append({
                "dimension": MbtiDimension.EI,
                "question_no": i,
                "question_text": q["text"],
                "option_a": q["a"],
                "option_b": q["b"],
                "weight_a": 1,
                "weight_b": 1,
            })

        for i, q in enumerate(sn_data, 1):
            questions_data.append({
                "dimension": MbtiDimension.SN,
                "question_no": i,
                "question_text": q["text"],
                "option_a": q["a"],
                "option_b": q["b"],
                "weight_a": 1,
                "weight_b": 1,
            })

        for i, q in enumerate(tf_data, 1):
            questions_data.append({
                "dimension": MbtiDimension.TF,
                "question_no": i,
                "question_text": q["text"],
                "option_a": q["a"],
                "option_b": q["b"],
                "weight_a": 1,
                "weight_b": 1,
            })

        for i, q in enumerate(jp_data, 1):
            questions_data.append({
                "dimension": MbtiDimension.JP,
                "question_no": i,
                "question_text": q["text"],
                "option_a": q["a"],
                "option_b": q["b"],
                "weight_a": 1,
                "weight_b": 1,
            })

        for q in questions_data:
            db.add(MbtiQuestion(**q))

        db.commit()
        loguru.logger.info("MBTI questions seeded: 48 questions across 4 dimensions")

    def _get_ei_questions(self) -> list:
        return [
            {"text": "周末你通常会怎么安排？", "a": "约朋友一起出去玩，参加聚会或活动", "b": "一个人在家看书、听音乐或看电影"},
            {"text": "在社交场合中，你通常会？", "a": "主动和陌生人攀谈，充当气氛制造者", "b": "在一旁观察，和熟悉的人轻声交流"},
            {"text": "当你独自一人时，你更喜欢？", "a": "安排紧凑的日程，享受充实的独处时光", "b": "什么都不想，让自己完全放松下来"},
            {"text": "你获取能量的方式更接近？", "a": "和一群人相处后感到充满活力", "b": "独处一段时间后感到精力充沛"},
            {"text": "在工作中，你更享受？", "a": "和团队一起头脑风暴，讨论创意", "b": "独自专注工作，不受打扰"},
            {"text": "面对新认识的人，你的反应通常是？", "a": "很快就能熟络起来，聊得很开心", "b": "需要一些时间才会打开话匣子"},
            {"text": "你更喜欢什么样的沟通方式？", "a": "面对面或电话交流，能听到对方的声音", "b": "文字消息或邮件，可以思考后再回复"},
            {"text": "假期旅行时，你更倾向于？", "a": "去热门景点，和当地人、其他游客互动", "b": "去安静的地方，享受私人空间"},
            {"text": "参加聚会时，如果大多数人你都不认识，你会？", "a": "主动自我介绍，很快融入圈子", "b": "找个角落待着，等朋友来介绍"},
            {"text": "当你遇到问题时，你更愿意？", "a": "找人聊聊，听听不同意见", "b": "自己想清楚再做决定"},
            {"text": "空闲时间，你更经常？", "a": "外出参加各种活动或社交", "b": "在家做自己喜欢的事情"},
            {"text": "在群体讨论中，你的角色通常是？", "a": "积极发言，分享自己的想法", "b": "倾听为主，适时补充观点"},
        ]

    def _get_sn_questions(self) -> list:
        return [
            {"text": "你看地图时，更关注？", "a": "具体的街道名、地标和距离", "b": "整体的方向和相对位置"},
            {"text": "在描述一件艺术品时，你更在意？", "a": "作品的材质、技法和细节", "b": "作品传达的感觉和意境"},
            {"text": "阅读小说时，你更容易被什么吸引？", "a": "具体的情节发展和人物行为", "b": "故事背后的隐喻和深层含义"},
            {"text": "解决一个问题时，你更依赖？", "a": "过往的经验和已验证的方法", "b": "新的想法和创新的思路"},
            {"text": "在规划活动时，你更看重？", "a": "具体的流程、时间表和细节安排", "b": "大致的方向和整体氛围"},
            {"text": "面对一个新产品，你更关注？", "a": "它的具体功能和使用方法", "b": "它代表的新概念和可能性"},
            {"text": "学习新技能时，你更喜欢？", "a": "一步一步跟着教程操作练习", "b": "先理解原理，再自由探索"},
            {"text": "看天气预报时，你更想知道？", "a": "温度、降雨概率、空气质量等具体数据", "b": "天气变化趋势和出行建议"},
            {"text": "评价一个人，你更看重？", "a": "他实际做了什么，取得了什么成果", "b": "他的潜力和未来的可能性"},
            {"text": "听到一个新奇的想法时，你的反应是？", "a": "质疑它的可行性，要求具体说明", "b": "感到兴奋，想要进一步了解"},
            {"text": "和朋友聊天时，你更经常谈论？", "a": "最近发生的事，大家都在聊的话题", "b": "未来的计划、理想和人生感悟"},
            {"text": "选择礼物时，你更倾向于？", "a": "对方明确表示过需要的东西", "b": "能代表心意、有创意的惊喜礼物"},
        ]

    def _get_tf_questions(self) -> list:
        return [
            {"text": "做重要决定时，你最看重？", "a": "这件事的逻辑性和实际效果", "b": "各方的感受和关系的影响"},
            {"text": "当朋友向你倾诉烦恼时，你通常会？", "a": "帮他分析问题，找出解决方案", "b": "先共情安慰，让他感到被理解"},
            {"text": "你更认同以下哪种观点？", "a": "公平比仁慈更重要", "b": "仁慈比公平更重要"},
            {"text": "看到感人的电影场景，你的反应是？", "a": "会被触动，但理性上会想这是否是刻意煽情", "b": "完全沉浸其中，跟着角色一起流泪"},
            {"text": "在帮助他人时，你更在意？", "a": "是否真正解决了问题", "b": "对方是否感受到关心和支持"},
            {"text": "你更希望被什么样的人称赞？", "a": "称赞我的能力和成果", "b": "称赞我的善良和为人"},
            {"text": "当团队意见不统一时，你倾向于？", "a": "用逻辑分析找出最优方案", "b": "协调各方感受，寻求共识"},
            {"text": "在公交车上给老人让座，你的想法是？", "a": "尊老爱幼是基本礼貌，应该这样做", "b": "希望能真正帮到他，而不只是形式"},
            {"text": "看新闻时，你更关注？", "a": "事件的来龙去脉和客观事实", "b": "背后的人性故事和情感因素"},
            {"text": "你更愿意和什么样的人深交？", "a": "聪明、有能力、能给我启发的人", "b": "真诚、善良、让我感到温暖的人"},
            {"text": "面对一个两难的选择，你的决定依据是？", "a": "权衡利弊，选择最优解", "b": "考虑所有人的感受，选择最温和的方案"},
            {"text": "你认为最好的道歉方式是？", "a": "承认错误，说明如何改正", "b": "真诚表达歉意，让对方感受到悔意"},
        ]

    def _get_jp_questions(self) -> list:
        return [
            {"text": "你更喜欢什么样的生活方式？", "a": "有计划、有规律、井井有条", "b": "灵活自由、随性而为"},
            {"text": "做一件事之前，你会？", "a": "先制定详细的计划再开始", "b": "先开始做，边做边调整"},
            {"text": "你的书桌或房间通常是什么状态？", "a": "整齐有序，每样东西都有固定位置", "b": "有点乱，但你知道每样东西在哪"},
            {"text": "和朋友约好见面，你会？", "a": "提前规划好路线和时间，准时到达", "b": "差不多时间再出发，灵活应对"},
            {"text": "面对多项任务时，你会？", "a": "按优先级排序，一件件完成", "b": "哪件想做就做哪件"},
            {"text": "你更倾向于？", "a": "严格遵守截止日期，按时完成任务", "b": "在最后期限前灵活调整"},
            {"text": "你更喜欢什么样的工作环境？", "a": "结构清晰、有明确流程和规范", "b": "宽松自由、可以自由发挥"},
            {"text": "出门旅行前，你会？", "a": "提前订好所有行程和酒店", "b": "只定大概方向，走到哪算哪"},
            {"text": "你更害怕哪种情况？", "a": "计划被打乱，出现意外变故", "b": "感到无聊，生活没有新鲜感"},
            {"text": "做一件事时，你更享受？", "a": "按部就班完成每个步骤的成就感", "b": "在过程中发现新可能的惊喜感"},
            {"text": "你收到一份没有明确要求的任务，会？", "a": "主动列出问题，和对方确认细节", "b": "先按自己的理解做，有问题再调整"},
            {"text": "你的衣柜里，大多数衣服是？", "a": "基础款式，便于搭配", "b": "各种风格都有，看心情选择"},
        ]

# 全局服务实例
_mbti_service: Optional[MbtiService] = None


def get_mbti_service() -> MbtiService:
    """获取MBTI服务实例"""
    global _mbti_service
    if _mbti_service is None:
        _mbti_service = MbtiService()
    return _mbti_service


# AI助手种子数据
AI_ASSISTANTS_DATA = [
    {
        "name": "温柔倾听者-小暖",
        "mbti_type": "INFJ",
        "personality": "温柔细腻、善解人意、具有强烈的同理心",
        "speaking_style": "轻声细语、温暖人心、充满理解",
        "expertise": "情感咨询、情绪疏导、心理支持",
        "greeting": "你好呀，我是小暖。每当你需要倾诉时，我都会在这里静静地倾听。",
        "tags": "温柔,倾听,共情,治愈",
    },
    {
        "name": "理性分析家-小智",
        "mbti_type": "INTJ",
        "personality": "理性冷静、逻辑思维强、善于分析问题",
        "speaking_style": "条理清晰、理性客观、有深度",
        "expertise": "问题分析、决策建议、逻辑思考",
        "greeting": "你好，我是小智。遇到难以抉择的问题时，我可以帮你理性分析。",
        "tags": "理性,分析,逻辑,智慧",
    },
    {
        "name": "阳光能量站-小乐",
        "mbti_type": "ENFP",
        "personality": "热情洋溢、创意无限、充满正能量",
        "speaking_style": "活泼热情、幽默风趣、充满感染力",
        "expertise": "创意激发、正能量传递、社交技巧",
        "greeting": "嗨！我是小乐！今天有什么开心或不开心的事想和我分享吗？",
        "tags": "阳光,正能量,创意,幽默",
    },
    {
        "name": "知心大姐姐-小雅",
        "mbti_type": "ENFJ",
        "personality": "善解人意、温柔体贴、富有领导力",
        "speaking_style": "亲切温暖、循循善诱、充满力量",
        "expertise": "人际关系、职业规划、个人成长",
        "greeting": "你好，我是小雅。任何困惑都可以和我聊聊，让我们一起找到答案。",
        "tags": "知心,姐姐,温暖,指引",
    },
    {
        "name": "冷静思考者-小安",
        "mbti_type": "ISTP",
        "personality": "冷静理性、灵活务实、动手能力强",
        "speaking_style": "简洁明了、实事求是、不拖泥带水",
        "expertise": "问题解决、实际操作、危机处理",
        "greeting": "你好，我是小安。遇到问题了我们一个个来解决。",
        "tags": "冷静,务实,解决问题,稳定",
    },
    {
        "name": "心灵治愈师-小柔",
        "mbti_type": "ISFJ",
        "personality": "温柔体贴、任劳任怨、重视他人感受",
        "speaking_style": "柔声细语、体贴入微、令人安心",
        "expertise": "情绪安抚、倾听陪伴日常关怀",
        "greeting": "你好呀，看到你我很开心。有什么想说的都可以告诉我哦。",
        "tags": "治愈,温柔,体贴,守护",
    },
    {
        "name": "创意梦想家-小飞",
        "mbti_type": "INFP",
        "personality": "理想主义、富有创意、追求内心平静",
        "speaking_style": "诗意浪漫、富有想象力、触动心灵",
        "expertise": "创意写作、艺术表达、自我探索",
        "greeting": "你好，我是小飞。在这个复杂的世界里，让我们一起守护内心的美好。",
        "tags": "创意,梦想,理想,诗意",
    },
    {
        "name": "职场军师-小锋",
        "mbti_type": "ENTJ",
        "personality": "果断干练、领导力强、目标导向",
        "speaking_style": "简洁有力、目标明确、雷厉风行",
        "expertise": "职场发展、团队管理、战略规划",
        "greeting": "你好，我是小锋。职场困惑？来聊聊，我帮你分析局势。",
        "tags": "职场,领导力,决策,效率",
    },
]


async def seed_assistants(db: Session) -> None:
    """初始化AI助手数据"""
    from app.models import AiAssistant
    from app.services.cache_service import cache_assistants

    # 检查是否已有助手
    if db.query(AiAssistant).first():
        return

    for i, data in enumerate(AI_ASSISTANTS_DATA):
        assistant = AiAssistant(
            name=data["name"],
            mbti_type=MbtiType[data["mbti_type"]],
            personality=data["personality"],
            speaking_style=data["speaking_style"],
            expertise=data["expertise"],
            greeting=data["greeting"],
            tags=data["tags"],
            is_recommended=i < 3,  # 前3个推荐
            sort_order=10 - i,
        )
        db.add(assistant)

    db.commit()
    
    # 缓存助手数据
    assistants = db.query(AiAssistant).all()
    assistants_data = [
        {
            "id": assistant.id,
            "name": assistant.name,
            "mbti_type": assistant.mbti_type.value,
            "personality": assistant.personality,
            "speaking_style": assistant.speaking_style,
            "expertise": assistant.expertise,
            "greeting": assistant.greeting,
            "tags": assistant.tags,
            "is_recommended": assistant.is_recommended
        }
        for assistant in assistants
    ]
    
    # 缓存所有助手
    await cache_assistants(assistants_data)
    
    # 按MBTI类型缓存
    for mbti_type in ["ISTJ", "ISFJ", "INFJ", "INTJ", "ISTP", "ISFP", "INFP", "INTP", "ESTP", "ESFP", "ENFP", "ENTP", "ESTJ", "ESFJ", "ENFJ", "ENTJ"]:
        type_assistants = [a for a in assistants_data if a["mbti_type"] == mbti_type]
        if type_assistants:
            await cache_assistants(type_assistants, mbti_type)
    
    print(f"已初始化 {len(AI_ASSISTANTS_DATA)} 个AI助手")


# ==================== 快速版MBTI测试（12题）====================

QUICK_MBTI_QUESTIONS = [
    {"dimension": "EI", "text": "在社交聚会中，你通常？", "a": "和很多人交流，感觉很自在", "b": "只和熟悉的几个人聊天"},
    {"dimension": "EI", "text": "当你遇到问题时，你倾向于？", "a": "找朋友倾诉讨论", "b": "独自思考解决"},
    {"dimension": "EI", "text": "面对新工作环境，你会？", "a": "主动认识新同事", "b": "等别人来认识我"},
    {"dimension": "SN", "text": "你更关注事物的？", "a": "具体的事实和细节", "b": "可能性和整体印象"},
    {"dimension": "SN", "text": "学习新东西时，你喜欢？", "a": "亲自动手实践", "b": "先理解理论原理"},
    {"dimension": "SN", "text": "当别人描述一件事，你会？", "a": "记住具体细节", "b": "记住整体感觉"},
    {"dimension": "TF", "text": "做决定时，你更看重？", "a": "逻辑和公正", "b": "对他人的影响"},
    {"dimension": "TF", "text": "当别人犯错时，你会？", "a": "直接指出问题", "b": "考虑对方感受"},
    {"dimension": "TF", "text": "你更容易被什么说服？", "a": "数据和逻辑", "b": "感情和价值"},
    {"dimension": "JP", "text": "你更喜欢的生活方式是？", "a": "有计划有安排", "b": "灵活随性"},
    {"dimension": "JP", "text": "面对截止日期，你会？", "a": "提前完成", "b": "最后一刻完成"},
    {"dimension": "JP", "text": "你的工作习惯是？", "a": "列清单，按优先级", "b": "随做随学，灵活调整"},
]


def get_quick_questions() -> List[Dict]:
    """获取快速版MBTI题目（12题）"""
    return [
        {"question_id": i, "dimension": q["dimension"], "text": q["text"], "option_a": q["a"], "option_b": q["b"]}
        for i, q in enumerate(QUICK_MBTI_QUESTIONS)
    ]


def calculate_quick_result(answers: List[Dict]) -> Dict:
    """计算快速版MBTI结果
    
    12题版本：每维度3题，每题+1(A)或-1(B)
    分数规则：
    - 得分 > 0: 选择A端的类型 (E/S/T/J)
    - 得分 <= 0: 选择B端的类型 (I/N/F/P)
    - 注意：如果回答数量少于12题，可能出现0分，此时默认B端
    """
    scores = {"EI": 0, "SN": 0, "TF": 0, "JP": 0}
    
    for answer in answers:
        q_idx = answer.get("question_id", 0)
        # 验证题目索引有效性
        if q_idx < 0 or q_idx >= len(QUICK_MBTI_QUESTIONS):
            loguru.logger.warning(f"无效题目索引: {q_idx}")
            continue
        q = QUICK_MBTI_QUESTIONS[q_idx]
        dimension = q["dimension"]
        # 答案转换为标准格式
        user_answer = answer.get("answer", "").upper()
        if user_answer == "A":
            scores[dimension] += 1
        elif user_answer == "B":
            scores[dimension] -= 1
        else:
            loguru.logger.warning(f"无效答案: {answer.get('answer')}")
    
    # 确定MBTI类型
    mbti_type = ""
    mbti_type += "E" if scores["EI"] > 0 else "I"
    mbti_type += "S" if scores["SN"] > 0 else "N"
    mbti_type += "T" if scores["TF"] > 0 else "F"
    mbti_type += "J" if scores["JP"] > 0 else "P"
    
    loguru.logger.info(f"快速MBTI结果: {mbti_type}, 分数: {scores}, 回答数: {len(answers)}")
    
    return {"mbti_type": mbti_type, "scores": scores}