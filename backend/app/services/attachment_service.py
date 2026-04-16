"""
依恋风格服务
"""
from typing import List, Dict, Optional, Any, Tuple
from datetime import datetime
import asyncio
import loguru

from sqlalchemy.orm import Session

from app.services.llm.factory import chat


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
        },
        "焦虑型": {
            "description": "你对他人有积极的看法，但对自己缺乏信心，容易担心关系的稳定性。",
            "characteristics": [
                "渴望亲密",
                "担心被抛弃",
                "过度关注伴侣",
                "情绪波动较大",
            ],
        },
        "回避型": {
            "description": "你对自己有积极的看法，但对他人缺乏信任，倾向于保持情感距离。",
            "characteristics": [
                "重视独立",
                "难以表达情感",
                "回避亲密",
                "对关系持矛盾态度",
            ],
        },
        "混乱型": {
            "description": "你对自我和他人都缺乏稳定的看法，关系模式不稳定，容易在亲密和回避之间摇摆。",
            "characteristics": [
                "对关系既渴望又恐惧",
                "情绪极度不稳定",
                "难以预测的行为",
                "强烈的依恋需求",
            ],
        },
    }

    # 中文风格名到枚举的映射
    STYLE_TO_ENUM = {
        "安全型": "SECURE",
        "焦虑型": "ANXIOUS",
        "回避型": "AVOIDANT",
        "混乱型": "DISORGANIZED",
    }

    # 题目分析模式
    QUESTION_PATTERNS = {
        # 焦虑维度题目分析
        1: {
            "pattern": "害怕被遗弃",
            "high_score_desc": "当伴侣没有及时回复时，你会立刻感到焦虑，担心自己做错了什么",
            "low_score_desc": "你能理性看待伴侣的忙碌，不会过度解读未回复消息",
            "advice": "练习区分「伴侣忙」和「伴侣不爱我了」这两种情况，可以发消息问「你方便吗」而不是质问"
        },
        2: {
            "pattern": "恐惧被拒绝",
            "high_score_desc": "你内心深处害怕被抛弃，被拒绝会让你非常痛苦",
            "low_score_desc": "你对被拒绝有一定承受能力，能够理性看待",
            "advice": "建立多元化的情感支持系统，不要把全部情感需求寄托在一个人身上"
        },
        3: {
            "pattern": "分离焦虑",
            "high_score_desc": "与伴侣分开时你会感到强烈的不安，甚至影响日常生活",
            "low_score_desc": "你能享受与伴侣分开时的独立时光",
            "advice": "利用分开的时间专注于自我成长，把这当作充电而非煎熬"
        },
        4: {
            "pattern": "对关系的未来缺乏安全感",
            "high_score_desc": "争吵后你会反复思考「这段关系还能继续吗」",
            "low_score_desc": "争吵后你能较快恢复理性，信任关系的韧性",
            "advice": "记录每次争吵后的解决结果，你会发现自己关系的韧性比想象中强"
        },
        5: {
            "pattern": "需要持续的确认",
            "high_score_desc": "你需要伴侣不断表达爱意来确认自己是被爱的",
            "low_score_desc": "你对自己的价值有稳定的认知，不需要频繁的外界确认",
            "advice": "每天给自己3句自我肯定，减少对伴侣确认的依赖"
        },
        # 回避维度题目分析
        6: {
            "pattern": "亲密恐惧",
            "high_score_desc": "当关系变得更亲密时，你会本能地想要退缩",
            "low_score_desc": "你能享受亲密，不会因为亲密而感到不适",
            "advice": "把亲密感的增加视为关系健康的标志，而非危险的信号"
        },
        7: {
            "pattern": "过度强调独立",
            "high_score_desc": "你认为依赖他人是软弱的表现，保持距离让你感到安全",
            "low_score_desc": "你能接受适度的相互依赖",
            "advice": "区分「健康的依赖」和「过度依赖」，前者是关系的粘合剂"
        },
        8: {
            "pattern": "情感表达压力",
            "high_score_desc": "面对伴侣强烈的情感表达，你会感到压力想要逃避",
            "low_score_desc": "你能接受并欣赏伴侣的情感表达",
            "advice": "告诉伴侣你需要的表达方式，比如「我需要时间消化」而非完全回避"
        },
        9: {
            "pattern": "情感封闭",
            "high_score_desc": "你不习惯谈论内心感受，觉得表达情感很别扭",
            "low_score_desc": "你能够相对自如地分享内心感受",
            "advice": "从「分享今天发生的小事」开始，逐步练习表达感受"
        },
        10: {
            "pattern": "信任建立困难",
            "high_score_desc": "你需要很长时间才能在关系中感到安全",
            "low_score_desc": "你能较快地建立对伴侣的信任",
            "advice": "信任是逐步建立的，给自己和对方一个观察的机会"
        },
    }

    def get_questions(self, db: Session) -> List[Any]:
        """获取依恋风格题目"""
        from app.models import AttachmentQuestion
        return db.query(AttachmentQuestion).filter(
            AttachmentQuestion.is_active == True
        ).order_by(AttachmentQuestion.question_no).all()

    def _analyze_answer_patterns(self, answers: List[Dict], db: Session) -> Dict[str, Any]:
        """分析用户的答题模式，识别具体心理特征"""
        from app.models import AttachmentQuestion

        anxiety_answers = []  # 焦虑维度答题详情
        avoidance_answers = []  # 回避维度答题详情

        for answer in answers:
            question_id = answer["question_id"]
            score = answer.get("score", answer.get("answer", 0))
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

            answer_detail = {
                "question_id": question_id,
                "question_text": question.question_text,
                "score": score,
                "pattern_info": self.QUESTION_PATTERNS.get(question_id, {})
            }

            if question.anxiety_weight > 0:
                anxiety_answers.append(answer_detail)
            if question.avoidance_weight > 0:
                avoidance_answers.append(answer_detail)

        # 找出得分最高和最低的题目
        anxiety_sorted = sorted(anxiety_answers, key=lambda x: x["score"], reverse=True)
        avoidance_sorted = sorted(avoidance_answers, key=lambda x: x["score"], reverse=True)

        # 识别最显著的模式
        top_anxiety_patterns = [a for a in anxiety_sorted if a["score"] >= 5]
        top_avoidance_patterns = [a for a in avoidance_sorted if a["score"] >= 5]

        return {
            "anxiety_answers": anxiety_answers,
            "avoidance_answers": avoidance_answers,
            "anxiety_sorted": anxiety_sorted,
            "avoidance_sorted": avoidance_sorted,
            "top_anxiety_patterns": top_anxiety_patterns,
            "top_avoidance_patterns": top_avoidance_patterns,
        }

    def _generate_dynamic_relationship_tips(
        self,
        style: str,
        anxiety_score: float,
        avoidance_score: float,
        answer_analysis: Dict[str, Any]
    ) -> str:
        """生成完全动态的、基于用户具体答题模式的个性化关系建议"""

        top_anxiety = answer_analysis["top_anxiety_patterns"]
        top_avoidance = answer_analysis["top_avoidance_patterns"]

        tips_parts = []

        # 根据风格生成核心建议
        if style == "安全型":
            if anxiety_score > 3.5:
                tips_parts.append(f"你整体依恋模式健康，但焦虑分数({anxiety_score:.1f})略高。")
                if top_anxiety:
                    pattern = top_anxiety[0]["pattern_info"]
                    tips_parts.append(f"你最近可能比较担心「{pattern}」这个问题。")
            elif avoidance_score > 3.5:
                tips_parts.append(f"你整体依恋模式健康，但回避分数({avoidance_score:.1f})略高。")
                if top_avoidance:
                    pattern = top_avoidance[0]["pattern_info"]
                    tips_parts.append(f"在「{pattern}」方面你可能需要更多练习。")
            else:
                tips_parts.append("你拥有健康的依恋模式，能够在亲密和独立之间保持平衡。")
                tips_parts.append("继续保持这种状态，有意识地经营关系会让你更幸福。")

        elif style == "焦虑型":
            tips_parts.append(f"你的焦虑分数为{anxiety_score:.1f}，这意味着你在亲密关系中容易感到不安。")
            if top_anxiety:
                tips_parts.append(f"你最大的困扰似乎与「{top_anxiety[0]['pattern_info']['pattern']}」相关。")
                advice = top_anxiety[0]["pattern_info"].get("advice", "")
                if advice:
                    tips_parts.append(f"针对这一点，我的建议是：{advice}")

            if len(top_anxiety) > 1:
                tips_parts.append(f"此外，你在「{top_anxiety[1]['pattern_info']['pattern']}」方面也有较高得分。")

            # 根据焦虑程度给出不同强度的建议
            if anxiety_score >= 6.0:
                tips_parts.append(f"你的焦虑水平较高({anxiety_score:.1f}/7)，这可能影响你的日常情绪。")
                tips_parts.append("建议每天进行5-10分钟的放松练习，如深呼吸或冥想，帮助降低基础焦虑水平。")
            elif anxiety_score >= 4.5:
                tips_parts.append(f"你的焦虑水平中等偏高({anxiety_score:.1f}/7)，需要学会在感到不安时自我安抚。")

        elif style == "回避型":
            tips_parts.append(f"你的回避分数为{avoidance_score:.1f}，这意味着你在亲密关系中倾向于保持距离。")
            if top_avoidance:
                tips_parts.append(f"你主要的回避模式与「{top_avoidance[0]['pattern_info']['pattern']}」相关。")
                advice = top_avoidance[0]["pattern_info"].get("advice", "")
                if advice:
                    tips_parts.append(f"针对这一点：{advice}")

            if len(top_avoidance) > 1:
                tips_parts.append(f"同时，你在「{top_avoidance[1]['pattern_info']['pattern']}」方面也表现明显。")

            if avoidance_score >= 6.0:
                tips_parts.append(f"你的回避水平较高({avoidance_score:.1f}/7)，可能需要系统性练习来改变这个模式。")
            elif avoidance_score >= 4.5:
                tips_parts.append(f"你的回避水平中等偏高({avoidance_score:.1f}/7)，尝试每周做一件稍微突破舒适区的事。")

        else:  # 混乱型
            tips_parts.append(f"你的依恋模式较为复杂：焦虑{anxiety_score:.1f}，回避{avoidance_score:.1f}。")
            tips_parts.append("这种矛盾模式意味着你在关系中可能会有「想要亲密又害怕亲密」的冲突感受。")
            if top_anxiety and top_avoidance:
                anxiety_pattern = top_anxiety[0]["pattern_info"]["pattern"]
                avoidance_pattern = top_avoidance[0]["pattern_info"]["pattern"]
                tips_parts.append(f"你最突出的矛盾是：既担心「{anxiety_pattern}」，又害怕「{avoidance_pattern}」。")
            tips_parts.append("这种复杂的感受是正常的。")
            tips_parts.append("建议从「识别和命名」自己的情绪开始：当这种矛盾感出现时，试着说「我现在既感到...又感到...」。")

        return "".join(tips_parts)

    def _generate_dynamic_growth_tips(
        self,
        style: str,
        anxiety_score: float,
        avoidance_score: float,
        answer_analysis: Dict[str, Any]
    ) -> str:
        """生成完全动态的、基于用户具体答题模式的个性化成长建议"""

        anxiety_sorted = answer_analysis["anxiety_sorted"]
        avoidance_sorted = answer_analysis["avoidance_sorted"]
        top_anxiety = answer_analysis["top_anxiety_patterns"]
        top_avoidance = answer_analysis["top_avoidance_patterns"]

        growth_parts = []

        # 核心成长方向
        if style == "安全型":
            growth_parts.append("你的依恋基础良好，有很好的自我觉察能力。")
            if anxiety_score > 3.0 or avoidance_score > 3.0:
                growth_parts.append(f"但你的焦虑分数{anxiety_score:.1f}和回避分数{avoidance_score:.1f}显示还有一些成长空间。")
                growth_parts.append("建议：尝试主动表达更多感受，这会让你的关系更加深入。")
            else:
                growth_parts.append("你的成长方向是：深化情感连接，帮助身边需要支持的人。")

        elif style == "焦虑型":
            growth_parts.append(f"焦虑型依恋的核心课题是建立稳定的自我价值感（你的焦虑分数：{anxiety_score:.1f}）。")

            # 基于具体答题给出成长建议
            if top_anxiety:
                highest = top_anxiety[0]
                pattern_info = highest["pattern_info"]
                growth_parts.append(f"你得分最高的是「{pattern_info['pattern']}」：{pattern_info.get('high_score_desc', '')}")
                if highest["score"] >= 6:
                    growth_parts.append("这是一个需要重点关注的模式。")

            # 具体的成长练习
            growth_parts.append("具体成长练习：")
            if anxiety_score > 5.0:
                growth_parts.append("1. 每日情绪日志：记录触发焦虑的场景、你的反应、实际结果。你会发现很多担忧并没有发生。")
                growth_parts.append("2. 自我安抚清单：创建3个能快速让自己冷静下来的方法（如听音乐、散步、给朋友打电话）。")
                growth_parts.append("3. 逐步暴露：故意不立即回复消息，练习耐受不确定性的能力。")
            else:
                growth_parts.append("1. 情绪粒度练习：每天3次命名自己的情绪，从「不舒服」细化为「担心」「不安」「焦虑」等。")
                growth_parts.append("2. 建立独立支持系统：除了伴侣，找到至少2个可以倾诉的朋友。")

        elif style == "回避型":
            growth_parts.append(f"回避型依恋的核心课题是学会信任和表达（你的回避分数：{avoidance_score:.1f}）。")

            if top_avoidance:
                highest = top_avoidance[0]
                pattern_info = highest["pattern_info"]
                growth_parts.append(f"你得分最高的是「{pattern_info['pattern']}」：{pattern_info.get('high_score_desc', '')}")
                if highest["score"] >= 6:
                    growth_parts.append("这个模式比较根深蒂固，需要持续练习。")

            growth_parts.append("具体成长练习：")
            if avoidance_score > 5.0:
                growth_parts.append("1. 情感词汇练习：每天学一个描述感受的词（如「失落」「沮丧」「欣慰」），扩大情感词汇量。")
                growth_parts.append("2. 逐步敞露：从分享「外部事件」逐步过渡到分享「内心感受」，每周至少1次。")
                growth_parts.append("3. 依赖练习：每周有意识地接受1次来自他人的帮助，练习接受支持的感觉。")
            else:
                growth_parts.append("1. 感受记录：每天记录3个当下感受到的情绪，不管多细微。")
                growth_parts.append("2. 主动连接：每周主动与一个人分享你的想法或感受，不要只是回应他人。")

        else:  # 混乱型
            growth_parts.append(f"混乱型依恋的成长需要更多耐心和系统的方法（焦虑{anxiety_score:.1f}，回避{avoidance_score:.1f}）。")

            growth_parts.append("你可能经常在「想要亲密」和「想要逃离」之间摇摆，这是很正常的内心冲突。")
            growth_parts.append("核心练习：")
            growth_parts.append("1. 情绪双识别：当感到矛盾时，试着说「我同时感到A和B」，比如「我感到渴望亲密又感到害怕被控制」。")
            growth_parts.append("2. 暂停技术：在感到强烈冲动想要联系或不联系伴侣时，给自己10分钟冷静期。")
            growth_parts.append("3. 寻求专业支持：考虑心理咨询，专业人士可以帮助你更系统地理解和改变依恋模式。")

        # 添加基于具体分数的额外建议
        if anxiety_score > 6.0:
            growth_parts.append(f"\n补充：你的焦虑水平很高({anxiety_score:.1f}/7)，建议优先处理焦虑问题，再关注关系技巧。")
        if avoidance_score > 6.0:
            growth_parts.append(f"\n补充：你的回避水平很高({avoidance_score:.1f}/7)，建议优先建立情感觉察能力，再尝试打开亲密的大门。")

        return "".join(growth_parts)

    async def _generate_llm_advice(
        self,
        style: str,
        anxiety_score: float,
        avoidance_score: float,
        answer_analysis: Dict[str, Any],
        advice_type: str = "relationship"
    ) -> Optional[str]:
        """使用LLM生成真正个性化的建议"""
        try:
            # 构建用户画像
            style_descriptions = {
                "安全型": "安全型（Secure）",
                "焦虑型": "焦虑型（Anxious）",
                "回避型": "回避型（Avoidant）",
                "混乱型": "混乱型（Disorganized）"
            }
            style_name = style_descriptions.get(style, style)

            # 构建答题模式详情
            top_anxiety = answer_analysis.get("top_anxiety_patterns", [])
            top_avoidance = answer_analysis.get("top_avoidance_patterns", [])

            # 构建用户详细档案
            user_profile = f"""
依恋风格类型：{style_name}
焦虑维度得分：{anxiety_score:.2f}/7（得分越高表示越容易在亲密关系中感到不安和担忧）
回避维度得分：{avoidance_score:.2f}/7（得分越高表示越倾向于在亲密关系中保持距离）

最突出的焦虑模式：
"""
            for i, pattern in enumerate(top_anxiety[:3], 1):
                pattern_info = pattern.get("pattern_info", {})
                user_profile += f"{i}. {pattern_info.get('pattern', '未知')}（得分：{pattern['score']}/7）\n"
                user_profile += f"   具体表现：{pattern_info.get('high_score_desc', '未知描述')}\n"

            user_profile += "\n最突出的回避模式：\n"
            for i, pattern in enumerate(top_avoidance[:3], 1):
                pattern_info = pattern.get("pattern_info", {})
                user_profile += f"{i}. {pattern_info.get('pattern', '未知')}（得分：{pattern['score']}/7）\n"
                user_profile += f"   具体表现：{pattern_info.get('high_score_desc', '未知描述')}\n"

            # 根据建议类型构建提示词
            if advice_type == "relationship":
                system_prompt = """你是一位专业的心理咨询师，专注于依恋理论和亲密关系咨询。
你的任务是结合用户的依恋风格测试结果（包含具体答题模式和得分），给出真正个性化、可操作的建议。
要求：
1. 基于用户具体的答题模式而不是泛泛而谈
2. 指出用户特有的具体问题模式，不是笼统的性格描述
3. 给出具体、可执行的建议，而不是"多沟通"这样的空话
4. 语气温暖、理解、共情，不评判
5. 建议要具体到行为层面，比如"当伴侣30分钟没回复时，先深呼吸3次，而不是立刻发消息质问"
6. 结合用户的得分，给出与得分匹配的指导
7. 回答用中文，200字以内"""

                user_prompt = (
                    f"{user_profile}\n\n"
                    "请根据以上用户的依恋风格测试结果，给出个性化的关系相处建议。"
                    "要特别针对用户得分最高的模式给出具体建议。"
                )
            else:  # growth
                system_prompt = """你是一位专业的心理咨询师，专注于依恋理论和个人成长。
你的任务是结合用户的依恋风格测试结果，给出真正个性化、可执行的成长指导。
要求：
1. 基于用户具体的答题模式而不是泛泛而谈
2. 指出用户特有的具体成长点，不是笼统的自我提升建议
3. 给出具体、可执行的成长练习，而不是"多爱自己"这样的空话
4. 成长建议要与用户的得分和模式匹配
5. 可以建议具体的日常练习（如情绪记录、冥想、认知重构等）
6. 强调渐进式改变，接受不完美
7. 回答用中文，200字以内"""

                user_prompt = (
                    f"{user_profile}\n\n"
                    "请根据以上用户的依恋风格测试结果，给出个性化的成长建议。"
                    "要特别针对用户得分最高的模式给出具体的成长练习。"
                )

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ]

            # 调用LLM生成建议，带重试和超时
            try:
                llm_advice = await asyncio.wait_for(
                    chat(messages, temperature=0.7, max_tokens=500),
                    timeout=15.0
                )
                return llm_advice.strip() if llm_advice else None
            except asyncio.TimeoutError:
                loguru.logger.warning(f"LLM advice generation timeout for advice_type={advice_type}")
                return None
            except Exception as e:
                loguru.logger.error(f"LLM advice generation error: {e}")
                return None

        except Exception as e:
            loguru.logger.error(f"Error in _generate_llm_advice: {e}")
            return None

    async def calculate_result(self, db: Session, user_id: int, answers: List[Dict]) -> Dict[str, Any]:
        """计算依恋风格结果（结合动态建议和LLM个性化建议）"""
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

        # 分析答题模式
        answer_analysis = self._analyze_answer_patterns(answers, db)

        # 确定依恋风格
        style = self._determine_style(anxiety_score, avoidance_score)
        style_config = self.STYLES.get(style, self.STYLES["安全型"])

        # 获取枚举值
        enum_key = self.STYLE_TO_ENUM.get(style, "SECURE")
        attachment_style_enum = AttachmentStyle[enum_key]

        # 生成完全动态的个性化建议（规则基础）
        relationship_tips = self._generate_dynamic_relationship_tips(
            style, anxiety_score, avoidance_score, answer_analysis
        )
        self_growth_tips = self._generate_dynamic_growth_tips(
            style, anxiety_score, avoidance_score, answer_analysis
        )

        # 并行调用LLM生成个性化建议
        llm_relationship_advice, llm_growth_advice = await asyncio.gather(
            self._generate_llm_advice(style, anxiety_score, avoidance_score, answer_analysis, "relationship"),
            self._generate_llm_advice(style, anxiety_score, avoidance_score, answer_analysis, "growth"),
            return_exceptions=True
        )

        # 处理LLM建议异常
        if isinstance(llm_relationship_advice, Exception):
            loguru.logger.warning(f"LLM relationship advice failed: {llm_relationship_advice}")
            llm_relationship_advice = None
        if isinstance(llm_growth_advice, Exception):
            loguru.logger.warning(f"LLM growth advice failed: {llm_growth_advice}")
            llm_growth_advice = None

        # 组合建议：动态建议 + LLM建议
        combined_relationship_tips = relationship_tips
        if llm_relationship_advice:
            combined_relationship_tips = f"{relationship_tips}\n\n【AI个性化建议】\n{llm_relationship_advice}"

        combined_self_growth_tips = self_growth_tips
        if llm_growth_advice:
            combined_self_growth_tips = f"{self_growth_tips}\n\n【AI个性化成长指导】\n{llm_growth_advice}"

        return {
            "style": style,
            "anxiety_score": round(anxiety_score, 2),
            "avoidance_score": round(avoidance_score, 2),
            "attachment_style": attachment_style_enum.value,
            "characteristics": style_config["characteristics"],
            "relationship_tips": combined_relationship_tips,
            "self_growth_tips": combined_self_growth_tips,
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
