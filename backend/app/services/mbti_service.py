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

    # MBTI类型昵称后缀
    NICKNAME_SUFFIXES = {
        "ISTJ": "务实者",
        "ISFJ": "守护者",
        "INFJ": "知心者",
        "INTJ": "战略家",
        "ISTP": "实践者",
        "ISFP": "艺术家",
        "INFP": "理想者",
        "INTP": "思考者",
        "ESTP": "行动者",
        "ESFP": "表演者",
        "ENFP": "激励者",
        "ENTP": "辩论家",
        "ESTJ": "管理者",
        "ESFJ": "执政官",
        "ENFJ": "教育家",
        "ENTJ": "指挥官",
    }

    @staticmethod
    def generate_nickname_from_mbti(mbti_type: str, original_nickname: str = None) -> str:
        """根据MBTI类型生成昵称

        Args:
            mbti_type: MBTI类型（如 INFJ, ENFP 等）
            original_nickname: 用户原始昵称，如果是自动生成的则替换

        Returns:
            基于MBTI的新昵称
        """
        import random
        import string

        suffix = MbtiService.NICKNAME_SUFFIXES.get(mbti_type, "探索者")

        # 检查原始昵称是否是自动生成的（包含"用户"或数字过多）
        is_auto_generated = False
        if original_nickname:
            # 如果昵称包含"用户"或看起来像"心灵XX1234"格式，则是自动生成的
            if "用户" in original_nickname or len([c for c in original_nickname if c.isdigit()]) >= 4:
                is_auto_generated = True

        if is_auto_generated or not original_nickname:
            # 生成一个2-4位的随机字符作为唯一标识
            unique_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=random.randint(2, 4)))
            return f"{suffix}{unique_id}"
        else:
            # 如果用户有自定义昵称，保留并在前面加上MBTI类型
            return f"{suffix}{original_nickname[:2]}"

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

    def _generate_match_reason(self, assistant: 'AiAssistant', user_profile: dict, score: float) -> str:
        """生成详细的推荐理由"""
        reasons = []
        user_mbti = user_profile.get('mbti')
        user_sbti = user_profile.get('sbti', [])
        user_attachment = user_profile.get('attachment')

        # MBTI匹配分析
        if user_mbti and str(assistant.mbti_type) == user_mbti:
            mbti_descriptions = {
                "ISTJ": "务实可靠型", "ISFJ": "温柔守护型", "INFJ": "理想洞察型",
                "INTJ": "战略思维型", "ISTP": "灵活实践型", "ISFP": "艺术敏感型",
                "INFP": "理想调停型", "INTP": "逻辑思考型", "ESTP": "活力行动型",
                "ESFP": "热情表演型", "ENFP": "激励创意型", "ENTP": "创新辩论型",
                "ESTJ": "高效执行型", "ESFJ": "关怀付出型", "ENFJ": "领导激励型", "ENTJ": "决断指挥官型"
            }
            reasons.append(f"你们的MBTI类型完全一致（{mbti_descriptions.get(user_mbti, user_mbti)}），{assistant.name}能深刻理解你的思维方式和行为习惯")
        elif user_mbti:
            # 部分匹配
            assistant_first = str(assistant.mbti_type)[0]
            user_first = user_mbti[0]
            dimension_names = {"E": "外向", "I": "内向", "S": "感觉", "N": "直觉",
                              "T": "思维", "F": "情感", "J": "判断", "P": "知觉"}
            if assistant_first == user_first:
                assistant_second = str(assistant.mbti_type)[1]
                user_second = user_mbti[1]
                if assistant_second == user_second:
                    reasons.append(f"你们在{dimension_names.get(assistant_first, assistant_first)}维度上相同，沟通会更顺畅")

        # SBTI才干匹配分析
        if user_sbti and assistant.sbti_types:
            assistant_sbti_list = [s.strip() for s in assistant.sbti_types.split(',') if s.strip()]
            matching_themes = [s for s in user_sbti if s in assistant_sbti_list]
            if matching_themes:
                theme_names = {
                    "成就": "成就导向", "行动": "行动导向", "适应": "适应变化", "统筹": "统筹规划",
                    "信仰": "信念坚定", "公平": "公平正义", "审慎": "谨慎稳健", "纪律": "自律规范",
                    "专注": "专注深入", "责任": "责任担当", "排难": "问题解决", "统率": "领导统率",
                    "沟通": "沟通表达", "竞争": "竞争进取", "完美": "追求完美", "自信": "自信坚定",
                    "追求": "追求认可", "取悦": "人际和谐", "关联": "关联思维", "伯乐": "培养指导",
                    "体谅": "同理理解", "和谐": "和谐调解", "包容": "包容多元", "个别": "关注个体",
                    "积极": "积极乐观", "交往": "社交交往", "分析": "分析思考", "回顾": "经验总结",
                    "前瞻": "前瞻预见", "理念": "理念理想", "搜集": "信息搜集", "思维": "思维深度",
                    "学习": "学习成长", "战略": "战略规划"
                }
                matched_names = [theme_names.get(t, t) for t in matching_themes[:3]]
                reasons.append(f"你们共享「{'」「'.join(matched_names)}」等才干主题，交流更有共鸣")

        # 依恋风格匹配分析
        if user_attachment and assistant.attachment_styles:
            assistant_attach_list = [a.strip() for a in assistant.attachment_styles.split(',') if a.strip()]
            # 标准化：提取实际值（去掉 AttachmentStyle. 前缀）
            normalized_assistant_attach = []
            for a in assistant_attach_list:
                if '.' in a:
                    normalized_assistant_attach.append(a.split('.')[-1].lower())
                else:
                    normalized_assistant_attach.append(a.lower())

            # 标准化用户值
            user_attach_lower = user_attachment.lower() if isinstance(user_attachment, str) else user_attachment

            if user_attach_lower in normalized_assistant_attach:
                attach_descriptions = {
                    "secure": "安全型",
                    "anxious": "焦虑型",
                    "avoidant": "回避型",
                    "disorganized": "混乱型"
                }
                reasons.append(f"你们都是{attach_descriptions.get(user_attach_lower, user_attach_lower)}依恋风格，在情感交流上更容易建立信任")
            elif user_attach_lower == "secure":
                reasons.append("作为安全型依恋，你能够理解和包容不同依恋风格的伴侣")

        # 个性化和专长匹配
        if assistant.personality and user_mbti:
            personality_keywords = {
                "INFJ": ["同理心", "洞察力", "理想主义", "治愈"],
                "INTJ": ["逻辑", "战略", "独立", "分析"],
                "ENFP": ["热情", "创意", "激励", "正能量"],
                "ENFJ": ["领导力", "感染力", "关怀", "激励"],
                "ISTP": ["冷静", "务实", "问题解决", "灵活"],
                "ISFJ": ["温柔", "守护", "体贴", "关怀"],
                "INFP": ["理想", "创意", "诗意", "真诚"],
                "ENTJ": ["决断", "效率", "领导力", "战略"]
            }
            keywords = personality_keywords.get(str(assistant.mbti_type), [])
            matched_keywords = [k for k in keywords if k in assistant.personality]
            if matched_keywords:
                reasons.append(f"助手擅长{matched_keywords[0]}，正好契合你的需求")

        # 生成最终推荐理由
        if not reasons:
            reasons.append(f"{assistant.name}能够为你提供专业的情感支持和陪伴")

        return "；".join(reasons)

    def get_recommended_assistants_with_reason(
        self,
        db: Session,
        user_id: Optional[int] = None,
    ) -> List[dict]:
        """获取推荐的AI助手列表（带详细推荐理由）"""
        query = db.query(AiAssistant).filter(AiAssistant.is_active == True)
        assistants = query.all()

        if not user_id:
            # 无用户ID时，返回默认推荐
            return [{
                "assistant": a,
                "match_score": 50.0,
                "match_reason": f"{a.name}是我们为你精选的AI助手伙伴"
            } for a in assistants[:3]]

        # 获取用户的三项测评结果
        from app.models import User
        user = db.query(User).filter(User.id == user_id).first()

        if not user:
            return [{
                "assistant": a,
                "match_score": 50.0,
                "match_reason": f"{a.name}是我们为你精选的AI助手伙伴"
            } for a in assistants[:3]]

        user_profile = self._get_user_personality_profile(db, user)

        # 计算兼容性评分并生成推荐理由
        scored_assistants = []
        for assistant in assistants:
            score = self._calculate_compatibility(assistant, user_profile)
            reason = self._generate_match_reason(assistant, user_profile, score)
            scored_assistants.append({
                "assistant": assistant,
                "match_score": round(score, 1),
                "match_reason": reason
            })

        # 按兼容性分数降序排序
        scored_assistants.sort(key=lambda x: x["match_score"], reverse=True)

        return scored_assistants

    def get_recommended_assistants(
        self,
        db: Session,
        mbti_type: Optional[str] = None,
        tags: Optional[List[str]] = None,
        user_id: Optional[int] = None,
    ) -> List[AiAssistant]:
        """获取推荐的AI助手（支持三位一体综合推荐）"""
        query = db.query(AiAssistant).filter(AiAssistant.is_active == True)

        # 如果提供了明确的过滤参数，使用简单过滤
        # 只有在没有提供任何过滤参数时，才进行三位一体个性化推荐
        if mbti_type is not None or tags is not None:
            assistants = query.all()

            # MBTI类型过滤 - 数据库存储的是Enum类型，需要用 .value 来比较
            if mbti_type:
                # 使用 .value 获取枚举的实际值（如 "INTJ"）进行比较
                assistants = [a for a in assistants if a.mbti_type and a.mbti_type.value == mbti_type]

            # 标签过滤
            if tags:
                assistants = [a for a in assistants if a.tags and any(tag in a.tags for tag in tags)]

            return assistants
        else:
            # 没有提供过滤参数时，进行三位一体综合匹配
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
        """计算助手与用户的兼容性评分（0-100）- 优化版以支持高匹配度"""
        score = 0.0
        weights = {'mbti': 40, 'sbti': 35, 'attachment': 25}

        # MBTI匹配（40%权重）
        if user_profile['mbti']:
            assistant_mbti = assistant.mbti_type.value if hasattr(assistant.mbti_type, 'value') else str(assistant.mbti_type)
            user_mbti = user_profile['mbti']
            
            if assistant_mbti == user_mbti:
                # 完全匹配：40分
                score += weights['mbti']
            else:
                # 部分匹配：检查每个维度的匹配
                match_count = 0
                for i in range(4):
                    if assistant_mbti[i] == user_mbti[i]:
                        match_count += 1
                # 按匹配维度比例计分
                score += weights['mbti'] * (match_count / 4)

        # SBTI匹配（35%权重）
        if user_profile['sbti'] and assistant.sbti_types:
            assistant_sbti = [s.strip() for s in assistant.sbti_types.split(',') if s.strip()]
            matches = sum(1 for s in user_profile['sbti'] if s in assistant_sbti)
            if matches > 0:
                # 优化：匹配2个及以上主题时给高分
                if matches >= 2:
                    score += weights['sbti']  # 完全匹配
                else:
                    score += (matches / len(user_profile['sbti'])) * weights['sbti']

        # 依恋风格匹配（25%权重）
        if user_profile['attachment'] and assistant.attachment_styles:
            assistant_attach = [a.strip() for a in assistant.attachment_styles.split(',') if a.strip()]
            # 获取用户依恋风格的字符串值（处理枚举类型）
            user_attach = user_profile['attachment']
            if hasattr(user_attach, 'value'):
                user_attach = user_attach.value

            # 标准化比较：提取实际值（去掉 AttachmentStyle. 前缀）
            normalized_assistant_attach = []
            for a in assistant_attach:
                if '.' in a:
                    # 去掉 "AttachmentStyle." 前缀得到实际值如 "AVOIDANT"
                    normalized_assistant_attach.append(a.split('.')[-1].lower())
                else:
                    normalized_assistant_attach.append(a.lower())

            # 标准化用户值
            normalized_user_attach = user_attach.lower() if isinstance(user_attach, str) else user_attach

            if normalized_user_attach in normalized_assistant_attach:
                score += weights['attachment']  # 完全匹配
            # 安全型依恋可以与其他类型较好匹配
            elif normalized_user_attach == 'secure' and len(normalized_assistant_attach) > 0:
                score += weights['attachment'] * 0.8  # 安全型兼容性更高

        # 如果助手有推荐标记，增加分数
        if assistant.is_recommended:
            score += 5

        return min(score, 100)

    def create_personalized_assistant(self, db: Session, user_id: int, user_profile: dict) -> 'AiAssistant':
        """为用户创建专属的定制化助手"""
        from app.models import User

        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("用户不存在")

        mbti_type = user_profile.get('mbti', 'INFJ')
        sbti_themes = user_profile.get('sbti', [])
        attachment_style = user_profile.get('attachment', 'secure')

        # 根据MBTI类型生成个性化配置
        mbti_configs = {
            "ISTJ": {"name_suffix": "务实者", "personality": "务实可靠、注重细节、有责任感", "speaking_style": "条理清晰、实事求是、简洁明了"},
            "ISFJ": {"name_suffix": "守护者", "personality": "温柔体贴、忠诚可靠、关怀他人", "speaking_style": "柔声细语、体贴入微、令人安心"},
            "INFJ": {"name_suffix": "知心者", "personality": "理想主义、洞察力强、富有同理心", "speaking_style": "温暖理解、富有深度、启发思考"},
            "INTJ": {"name_suffix": "战略家", "personality": "战略思维、独立分析、追求效率", "speaking_style": "逻辑清晰、简洁有力、富有洞见"},
            "ISTP": {"name_suffix": "实践者", "personality": "冷静理性、灵活务实、动手能力强", "speaking_style": "简洁直接、实事求是、解决问题"},
            "ISFP": {"name_suffix": "艺术家", "personality": "温和敏感、艺术气质、追求和谐", "speaking_style": "温柔诗意、富有美感、细腻体贴"},
            "INFP": {"name_suffix": "理想者", "personality": "理想主义、富有创意、追求意义", "speaking_style": "诗意浪漫、富有想象力、触动心灵"},
            "INTP": {"name_suffix": "思考者", "personality": "逻辑思维、抽象思考、追求真理", "speaking_style": "条理清晰、逻辑严密、富有深度"},
            "ESTP": {"name_suffix": "行动者", "personality": "活力十足、务实灵活、善于社交", "speaking_style": "活泼热情、直接爽快、充满能量"},
            "ESFP": {"name_suffix": "表演者", "personality": "热情开朗、富有魅力、活在当下", "speaking_style": "热情洋溢、幽默风趣、感染力强"},
            "ENFP": {"name_suffix": "激励者", "personality": "热情创意、灵感丰富、善于激励", "speaking_style": "活泼热情、创意无限、充满正能量"},
            "ENTP": {"name_suffix": "辩论家", "personality": "创新思维、善于辩论、喜欢挑战", "speaking_style": "机智幽默、思维敏捷、富有创意"},
            "ESTJ": {"name_suffix": "管理者", "personality": "组织能力强、传统务实、注重结果", "speaking_style": "简洁有力、条理清晰、高效务实"},
            "ESFJ": {"name_suffix": "执政官", "personality": "社交能力强、传统关怀、乐于助人", "speaking_style": "亲切温暖、关怀他人、善于沟通"},
            "ENFJ": {"name_suffix": "教育家", "personality": "领导能力强、同理心强、善于激励", "speaking_style": "亲切温暖、循循善诱、充满力量"},
            "ENTJ": {"name_suffix": "指挥官", "personality": "领导力强、决断力高、追求效率", "speaking_style": "简洁有力、目标明确、雷厉风行"},
        }

        config = mbti_configs.get(mbti_type, mbti_configs["INFJ"])
        
        # 生成助手名称
        nickname = user.nickname or "用户"
        assistant_name = f"{nickname}的专属{config['name_suffix']}"
        
        # 构建SBTI主题字符串
        sbti_types_str = ','.join(sbti_themes) if sbti_themes else None
        
        # 构建依恋风格字符串
        attachment_styles_str = attachment_style if attachment_style else "secure"

        # 创建助手
        assistant = AiAssistant(
            name=assistant_name,
            mbti_type=mbti_type,
            sbti_types=sbti_types_str,
            attachment_styles=attachment_styles_str,
            personality=config["personality"],
            speaking_style=config["speaking_style"],
            expertise="个性化情感陪伴、自我探索、成长支持",
            greeting=f"你好！我是专门为你定制的AI助手。基于你的人格特点，我会用最适合你的方式陪伴你。",
            tags="专属定制,个性化,高匹配度",
            is_recommended=True,
            is_active=True,
            sort_order=100,
        )
        
        db.add(assistant)
        db.commit()
        db.refresh(assistant)
        
        return assistant

    def get_high_match_recommended_assistants(
        self,
        db: Session,
        user_id: int,
        min_match_score: float = 98.0,
    ) -> List[dict]:
        """获取高匹配度的推荐助手（支持部分测评结果）"""
        from app.models import User

        # 获取用户
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return []

        # 获取用户人格画像（支持部分测评）
        user_profile = self._get_user_personality_profile(db, user)

        # 检查是否至少有一项测评完成
        has_mbti = bool(user_profile.get('mbti'))
        has_sbti = bool(user_profile.get('sbti'))
        has_attachment = bool(user_profile.get('attachment'))
        has_any = has_mbti or has_sbti or has_attachment

        if not has_any:
            # 未完成任何测评，返回空列表
            return []

        # 获取所有活跃助手
        query = db.query(AiAssistant).filter(AiAssistant.is_active == True)
        assistants = query.all()

        # 如果没有助手，直接创建定制化助手
        if not assistants:
            personalized_assistant = self.create_personalized_assistant(db, user_id, user_profile)
            return [{
                "assistant": personalized_assistant,
                "match_score": 100.0,
                "match_reason": f"这是专门为你定制的AI助手，基于你的人格特点（{user_profile['mbti'] or '待测评'} + {user_profile['sbti'] or '待测评'} + {user_profile['attachment'] or '待测评'}）"
            }]

        # 计算所有助手的匹配度
        scored_assistants = []
        for assistant in assistants:
            score = self._calculate_compatibility(assistant, user_profile)
            reason = self._generate_match_reason(assistant, user_profile, score)
            scored_assistants.append({
                "assistant": assistant,
                "match_score": round(score, 1),
                "match_reason": reason
            })

        # 按匹配度降序排序
        scored_assistants.sort(key=lambda x: x["match_score"], reverse=True)

        # 筛选高匹配度助手
        high_match_assistants = [a for a in scored_assistants if a["match_score"] >= min_match_score]

        # 如果有高匹配度助手，直接返回（不创建/查找定制化助手）
        if high_match_assistants:
            return high_match_assistants

        # 没有高匹配度助手（>=85%），检查用户是否已有定制化助手
        personalized_assistant = None
        user_nickname = user.nickname or "用户"

        # 查找该用户的现有定制化助手
        existing_personalized = db.query(AiAssistant).filter(
            AiAssistant.name.like(f"{user_nickname}%专属%"),
            AiAssistant.is_active == True
        ).first()

        if existing_personalized:
            # 用户已有定制化助手，使用现有的
            personalized_assistant = existing_personalized
        else:
            # 创建新的定制化助手
            personalized_assistant = self.create_personalized_assistant(db, user_id, user_profile)

        # 计算助手的匹配度
        if personalized_assistant:
            personalized_score = self._calculate_compatibility(personalized_assistant, user_profile)

            # 如果是个性化定制助手，确保最低匹配度为85%
            # 因为个性化助手是专门为用户创建的，应该有较高的匹配度
            if '专属' in personalized_assistant.name or '定制' in personalized_assistant.tags:
                personalized_score = max(personalized_score, 85.0)

            personalized_reason = self._generate_match_reason(personalized_assistant, user_profile, personalized_score)
            high_match_assistants = [{
                "assistant": personalized_assistant,
                "match_score": round(personalized_score, 1),
                "match_reason": personalized_reason
            }]

        return high_match_assistants

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


# AI助手种子数据（包含完整三位一体匹配信息）
AI_ASSISTANTS_DATA = [
    {
        "name": "温柔倾听者-小暖",
        "mbti_type": "INFJ",
        "sbti_types": "体谅,和谐,包容,个别,积极",
        "attachment_styles": "secure,anxious",
        "personality": "温柔细腻、善解人意、具有强烈的同理心",
        "speaking_style": "轻声细语、温暖人心、充满理解",
        "expertise": "情感咨询、情绪疏导、心理支持",
        "greeting": "你好呀，我是小暖。每当你需要倾诉时，我都会在这里静静地倾听。",
        "tags": "温柔,倾听,共情,治愈",
        "live2d_model_url": "/live2d/shizuku/model.json",
    },
        {
            "name": "理性分析家-小智",
            "mbti_type": "INTJ",
            "sbti_types": "分析,战略,思维,学习,专注",
            "attachment_styles": "secure,avoidant",
            "personality": "理性冷静、逻辑思维强、善于分析问题",
            "speaking_style": "条理清晰、理性客观、有深度",
            "expertise": "问题分析、决策建议、逻辑思考",
            "greeting": "你好，我是小智。遇到难以抉择的问题时，我可以帮你理性分析。",
            "tags": "理性,分析,逻辑,智慧",
            "live2d_model_url": "/live2d/shizuku/model.json",
        },
        {
            "name": "阳光能量站-小乐",
            "mbti_type": "ENFP",
            "sbti_types": "积极,交往,沟通,取悦,关联",
            "attachment_styles": "secure,anxious",
            "personality": "热情洋溢、创意无限、充满正能量",
            "speaking_style": "活泼热情、幽默风趣、充满感染力",
            "expertise": "创意激发、正能量传递、社交技巧",
            "greeting": "嗨！我是小乐！今天有什么开心或不开心的事想和我分享吗？",
            "tags": "阳光,正能量,创意,幽默",
            "live2d_model_url": "/live2d/shizuku/model.json",
        },
        {
            "name": "知心大姐姐-小雅",
            "mbti_type": "ENFJ",
            "sbti_types": "统率,沟通,伯乐,体谅,和谐",
            "attachment_styles": "secure",
            "personality": "善解人意、温柔体贴、富有领导力",
            "speaking_style": "亲切温暖、循循善诱、充满力量",
            "expertise": "人际关系、职业规划、个人成长",
            "greeting": "你好，我是小雅。任何困惑都可以和我聊聊，让我们一起找到答案。",
            "tags": "知心,姐姐,温暖,指引",
            "live2d_model_url": "/live2d/shizuku/model.json",
        },
        {
            "name": "冷静思考者-小安",
            "mbti_type": "ISTP",
            "sbti_types": "排难,适应,分析,专注,行动",
            "attachment_styles": "secure,avoidant",
            "personality": "冷静理性、灵活务实、动手能力强",
            "speaking_style": "简洁明了、实事求是、不拖泥带水",
            "expertise": "问题解决、实际操作、危机处理",
            "greeting": "你好，我是小安。遇到问题了我们一个个来解决。",
            "tags": "冷静,务实,解决问题,稳定",
            "live2d_model_url": "/live2d/shizuku/model.json",
        },
        {
            "name": "心灵治愈师-小柔",
            "mbti_type": "ISFJ",
            "sbti_types": "体谅,和谐,包容,责任,纪律",
            "attachment_styles": "secure,anxious",
            "personality": "温柔体贴、任劳任怨、重视他人感受",
            "speaking_style": "柔声细语、体贴入微、令人安心",
            "expertise": "情绪安抚、倾听陪伴、日常关怀",
            "greeting": "你好呀，看到你我很开心。有什么想说的都可以告诉我哦。",
            "tags": "治愈,温柔,体贴,守护",
            "live2d_model_url": "/live2d/shizuku/model.json",
        },
        {
            "name": "创意梦想家-小飞",
            "mbti_type": "INFP",
            "sbti_types": "理念,创意,体谅,和谐,个别",
            "attachment_styles": "secure,anxious",
            "personality": "理想主义、富有创意、追求内心平静",
            "speaking_style": "诗意浪漫、富有想象力、触动心灵",
            "expertise": "创意写作、艺术表达、自我探索",
            "greeting": "你好，我是小飞。在这个复杂的世界里，让我们一起守护内心的美好。",
            "tags": "创意,梦想,理想,诗意",
            "live2d_model_url": "/live2d/shizuku/model.json",
        },
        {
            "name": "职场军师-小锋",
            "mbti_type": "ENTJ",
            "sbti_types": "统率,战略,成就,竞争,自信",
            "attachment_styles": "secure",
            "personality": "果断干练、领导力强、目标导向",
            "speaking_style": "简洁有力、目标明确、雷厉风行",
            "expertise": "职场发展、团队管理、战略规划",
            "greeting": "你好，我是小锋。职场困惑？来聊聊，我帮你分析局势。",
            "tags": "职场,领导力,决策,效率",
            "live2d_model_url": "/live2d/shizuku/model.json",
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
            live2d_model_url=data.get("live2d_model_url"),
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