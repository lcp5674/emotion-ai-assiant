"""
SBTI测评服务
"""

from typing import List, Dict, Optional, Any
from datetime import datetime
import loguru

from sqlalchemy.orm import Session
from sqlalchemy import and_


class SBTIService:
    """SBTI测评服务"""

    # 34个才干主题定义（四大领域）
    THEMES = {
        # 执行力 (Executing)
        "成就": {
            "domain": "执行力",
            "description": "追求卓越，享受完成任务和达成目标的成就感。",
        },
        "行动": {
            "domain": "执行力",
            "description": "喜欢立即行动，快速将想法付诸实践。",
        },
        "适应": {
            "domain": "执行力",
            "description": "灵活变通，能够快速适应变化的环境和情况。",
        },
        "统筹": {
            "domain": "执行力",
            "description": "善于组织和协调资源，能够高效管理系统和流程。",
        },
        "信仰": {
            "domain": "执行力",
            "description": "重视传统和价值观，寻求做事方式背后的意义。",
        },
        "公平": {
            "domain": "执行力",
            "description": "重视公正和平等，对不一致和不公平非常敏感。",
        },
        "审慎": {
            "domain": "执行力",
            "description": "行事谨慎，在行动前会充分考虑风险。",
        },
        "纪律": {
            "domain": "执行力",
            "description": "做事有章法，喜欢按照计划和流程进行。",
        },
        "专注": {
            "domain": "执行力",
            "description": "能够排除干扰，全身心投入重要的事情。",
        },
        "责任": {"domain": "执行力", "description": "言出必行，对承诺的事情负责到底。"},
        "排难": {
            "domain": "执行力",
            "description": "善于解决问题，能够在困难面前保持冷静。",
        },
        # 影响力 (Influencing)
        "统率": {
            "domain": "影响力",
            "description": "具有领导才能，能够掌控局面并做出决定。",
        },
        "沟通": {
            "domain": "影响力",
            "description": "善于表达和交流，能够激发他人的热情和想法。",
        },
        "竞争": {
            "domain": "影响力",
            "description": "有进取心，喜欢与他人比较并追求领先。",
        },
        "完美": {
            "domain": "影响力",
            "description": "追求卓越，欣赏美好和优秀的人和事物。",
        },
        "自信": {
            "domain": "影响力",
            "description": "对自己有清晰的认识，相信自己有能力做好事情。",
        },
        "追求": {
            "domain": "影响力",
            "description": "渴望被认可，希望自己的贡献被重视。",
        },
        "取悦": {
            "domain": "影响力",
            "description": "喜欢结交朋友，善于赢得他人的好感和认可。",
        },
        # 关系建立 (Relationship Building)
        "关联": {
            "domain": "关系建立",
            "description": "相信万事皆有关联，重视人际之间的联系和共同点。",
        },
        "伯乐": {
            "domain": "关系建立",
            "description": "善于发现他人的潜能，乐于培养和指导他人。",
        },
        "体谅": {
            "domain": "关系建立",
            "description": "善于理解他人，能够设身处地为别人着想。",
        },
        "和谐": {
            "domain": "关系建立",
            "description": "寻求共识和一致，避免冲突和争议。",
        },
        "包容": {
            "domain": "关系建立",
            "description": "接纳并欣赏人与人之间的差异，尊重不同观点。",
        },
        "个别": {
            "domain": "关系建立",
            "description": "善于识别每个人的独特之处，关注个体差异。",
        },
        "积极": {"domain": "关系建立", "description": "充满活力，善于激励自己和他人。"},
        "交往": {
            "domain": "关系建立",
            "description": "喜欢结交和维护朋友，享受深度的人际交流。",
        },
        # 战略思维 (Strategic Thinking)
        "分析": {
            "domain": "战略思维",
            "description": "善于深入分析问题，寻找事物背后的逻辑和规律。",
        },
        "回顾": {
            "domain": "战略思维",
            "description": "善于从过去的经验中学习，理解当前的情境。",
        },
        "前瞻": {
            "domain": "战略思维",
            "description": "善于预见未来可能性，对长远发展有敏锐的直觉。",
        },
        "理念": {
            "domain": "战略思维",
            "description": "追求深层意义，喜欢思考抽象和哲学问题。",
        },
        "搜集": {"domain": "战略思维", "description": "好奇心强，喜欢收集信息和资源。"},
        "思维": {
            "domain": "战略思维",
            "description": "善于独立思考，喜欢深入分析问题。",
        },
        "学习": {
            "domain": "战略思维",
            "description": "热爱学习，享受获取新知识和技能的过程。",
        },
        "战略": {
            "domain": "战略思维",
            "description": "善于制定长远计划，能够看到全局和可能性。",
        },
    }

    # 题目与才干主题的映射（24道题）
    QUESTION_THEME_MAP = {
        1: "关联",
        2: "体谅",
        3: "沟通",
        4: "成就",
        5: "分析",
        6: "责任",
        7: "排难",
        8: "公平",
        9: "和谐",
        10: "理念",
        11: "包容",
        12: "适应",
        13: "专注",
        14: "搜集",
        15: "学习",
        16: "前瞻",
        17: "战略",
        18: "思维",
        19: "审慎",
        20: "行动",
        21: "积极",
        22: "取悦",
        23: "自信",
        24: "完美",
    }

    def get_questions(self, db: Session) -> List[Any]:
        """获取SBTI测评题目"""
        from app.models import SBTIQuestion

        return (
            db.query(SBTIQuestion)
            .filter(SBTIQuestion.is_active == True)
            .order_by(SBTIQuestion.question_no)
            .all()
        )

    def calculate_result(
        self, db: Session, user_id: int, answers: List[Dict]
    ) -> Dict[str, Any]:
        """计算SBTI测评结果 - 使用标准分计算避免满分问题"""
        import math
        from app.models import SBTIQuestion

        # 统计各主题得分
        theme_scores = {theme: 0 for theme in self.THEMES.keys()}
        theme_counts = {theme: 0 for theme in self.THEMES.keys()}

        for answer in answers:
            question_id = answer["question_id"]
            choice = answer["answer"]

            # 获取题目
            question = (
                db.query(SBTIQuestion).filter(SBTIQuestion.id == question_id).first()
            )

            if not question:
                continue

            # 根据选择确定主题
            selected_theme = question.theme_a if choice == "A" else question.theme_b
            weight = question.weight_a if choice == "A" else question.weight_b

            if selected_theme in theme_scores:
                theme_scores[selected_theme] += weight
                theme_counts[selected_theme] += 1

        # 原始得分（用于计算标准分）
        raw_scores = {}
        for theme in self.THEMES.keys():
            if theme_counts[theme] > 0:
                raw_scores[theme] = theme_scores[theme]
            else:
                raw_scores[theme] = 0

        # 使用标准分计算，避免全是100%的问题
        # 计算均值和标准差
        score_values = list(raw_scores.values())
        if score_values and sum(score_values) > 0:
            mean_score = sum(score_values) / len(score_values)
            variance = sum((x - mean_score) ** 2 for x in score_values) / len(
                score_values
            )
            std_dev = math.sqrt(variance) if variance > 0 else 1

            # 使用Z-Score转换为标准分，然后映射到0-100
            normalized_scores = {}
            for theme, raw_score in raw_scores.items():
                if theme_counts[theme] == 0:
                    normalized_scores[theme] = 0
                    continue
                # 计算Z-Score
                if std_dev > 0:
                    z_score = (raw_score - mean_score) / std_dev
                else:
                    z_score = 0
                # 将Z-Score映射到0-100分（使用tanh压缩避免边界问题）
                # 使用S型曲线：50 + 40 * tanh(z_score)，范围约5-95
                percentile = 50 + 40 * math.tanh(z_score * 0.5)
                normalized_scores[theme] = max(5, min(95, int(percentile)))
        else:
            normalized_scores = {theme: 0 for theme in self.THEMES.keys()}

        # 按得分排序，获取Top5
        sorted_themes = sorted(
            normalized_scores.items(), key=lambda x: x[1], reverse=True
        )
        top5 = sorted_themes[:5]

        top5_themes = [t[0] for t in top5]
        top5_scores = [t[1] for t in top5]

        # 计算四大领域得分
        domain_scores = {
            "执行力": 0,
            "影响力": 0,
            "关系建立": 0,
            "战略思维": 0,
        }

        domain_themes = {
            "执行力": [
                "成就",
                "行动",
                "适应",
                "统筹",
                "信仰",
                "公平",
                "审慎",
                "纪律",
                "专注",
                "责任",
                "排难",
            ],
            "影响力": ["统率", "沟通", "竞争", "完美", "自信", "追求", "取悦"],
            "关系建立": [
                "关联",
                "伯乐",
                "体谅",
                "和谐",
                "包容",
                "个别",
                "积极",
                "交往",
            ],
            "战略思维": [
                "分析",
                "回顾",
                "前瞻",
                "理念",
                "搜集",
                "思维",
                "学习",
                "战略",
            ],
        }

        for domain, themes in domain_themes.items():
            domain_total = sum(normalized_scores.get(t, 0) for t in themes)
            domain_scores[domain] = int(domain_total / len(themes)) if themes else 0

        # 确定主导领域
        dominant_domain = max(domain_scores.items(), key=lambda x: x[1])[0]

        # 构建主题详情
        theme_details = {}
        for i, (theme, score) in enumerate(zip(top5_themes, top5_scores), 1):
            theme_info = self.THEMES.get(theme, {})
            theme_details[theme] = {
                "rank": i,
                "score": score,
                "description": theme_info.get("description", ""),
                "domain": theme_info.get("domain", ""),
                "strengths": self._get_theme_strengths(theme),
                "growth_suggestions": self._get_growth_suggestions(theme),
            }

        # 构建关系洞察
        relationship_insights = self._build_relationship_insights(
            top5_themes, top5_scores
        )

        return {
            "all_themes_scores": normalized_scores,
            "top5_themes": top5_themes,
            "top5_scores": top5_scores,
            "theme_details": theme_details,
            "domain_scores": domain_scores,
            "dominant_domain": dominant_domain,
            "relationship_insights": relationship_insights,
        }

    def _get_theme_strengths(self, theme: str) -> List[str]:
        """获取主题优势"""
        strengths_map = {
            "关联": ["善于建立关系", "共情能力强", "团队精神"],
            "体谅": ["善解人意", "富有同情心", "支持他人"],
            "沟通": ["表达能力强", "富有感染力", "善于激励"],
            "成就": ["勤奋努力", "目标导向", "自我驱动"],
            "分析": ["分析能力强", "理性客观", "逻辑清晰"],
            "专注": ["专注力强", "有韧性", "高效执行"],
            "战略": ["全局视角", "善于规划", "预见未来"],
            "学习": ["学习能力强", "好奇心强", "适应力强"],
            "自信": ["自信果断", "抗压能力强", "有主见"],
            "完美": ["追求卓越", "有品位", "激励他人"],
        }
        return strengths_map.get(theme, ["具有相关优势"])

    def _get_growth_suggestions(self, theme: str) -> List[str]:
        """获取成长建议"""
        suggestions_map = {
            "关联": ["学会设立边界", "适当拒绝不重要的事"],
            "体谅": ["设立情绪边界", "学会自我关怀"],
            "沟通": ["多倾听少说", "注重深度交流"],
            "成就": ["学会欣赏过程", "适当休息放松"],
            "分析": ["平衡理性与情感", "学会接纳不确定性"],
            "专注": ["拓宽视野", "平衡工作与生活"],
            "战略": ["关注执行细节", "学以致用"],
            "学习": ["专注深度学习", "将知识转化为能力"],
            "自信": ["保持谦逊", "倾听他人意见"],
            "完美": ["接纳不完美", "欣赏平凡之美"],
        }
        return suggestions_map.get(theme, ["持续发展和提升"])

    def _build_relationship_insights(
        self, top5_themes: List[str], top5_scores: List[int]
    ) -> Dict[str, Any]:
        """构建关系洞察"""
        insights = {
            "strengths": [],
            "communication_style": "",
            "growth_areas": [],
        }

        # 基于才干主题分析关系优势
        relationship_themes = ["关联", "体谅", "沟通", "包容", "和谐", "交往", "伯乐"]
        for theme in top5_themes:
            if theme in relationship_themes:
                if theme == "关联":
                    insights["strengths"].append("善于建立深度关系")
                elif theme == "体谅":
                    insights["strengths"].append("共情能力强")
                elif theme == "沟通":
                    insights["strengths"].append("善于表达情感")
                elif theme == "包容":
                    insights["strengths"].append("接纳差异，关系包容")
                elif theme == "和谐":
                    insights["strengths"].append("善于处理冲突")
                elif theme == "交往":
                    insights["strengths"].append("善于维护友谊")

        if not insights["strengths"]:
            insights["strengths"].append("有自己的独特魅力")

        # 分析沟通风格
        if "沟通" in top5_themes:
            insights["communication_style"] = "善于表达、富有感染力"
        elif "思维" in top5_themes or "分析" in top5_themes:
            insights["communication_style"] = "理性、逻辑清晰"
        elif "体谅" in top5_themes or "关联" in top5_themes:
            insights["communication_style"] = "真诚、有深度"
        else:
            insights["communication_style"] = "真诚、直接"

        # 成长领域
        growth_areas = []
        if "沟通" not in top5_themes:
            growth_areas.append("提升沟通表达能力")
        if "体谅" not in top5_themes:
            growth_areas.append("培养共情能力")
        if "关联" not in top5_themes:
            growth_areas.append("学会建立深度连接")

        insights["growth_areas"] = (
            growth_areas if growth_areas else ["继续保持现有优势"]
        )

        return insights

    def seed_questions(self, db: Session, force: bool = False) -> None:
        """初始化SBTI题目"""
        from app.models import SBTIQuestion

        if not force and db.query(SBTIQuestion).first():
            return

        if force:
            db.query(SBTIQuestion).delete()

        questions_data = self._get_questions_data()

        for q in questions_data:
            db.add(SBTIQuestion(**q))

        db.commit()
        loguru.logger.info(f"SBTI questions seeded: {len(questions_data)} questions")

    def _get_questions_data(self) -> List[Dict]:
        return [
            {
                "question_no": 1,
                "statement_a": "我相信人与人之间存在深层联系",
                "theme_a": "关联",
                "statement_b": "每个人都是独立的个体",
                "theme_b": "个别",
                "domain": "关系建立",
                "weight_a": 1,
                "weight_b": 1,
            },
            {
                "question_no": 2,
                "statement_a": "我能够设身处地理解他人的感受",
                "theme_a": "体谅",
                "statement_b": "我更善于分析和解决问题",
                "theme_b": "分析",
                "domain": "关系建立",
                "weight_a": 1,
                "weight_b": 1,
            },
            {
                "question_no": 3,
                "statement_a": "我善于表达并说服他人",
                "theme_a": "沟通",
                "statement_b": "我更善于倾听和理解他人",
                "theme_b": "体谅",
                "domain": "影响力",
                "weight_a": 1,
                "weight_b": 1,
            },
            {
                "question_no": 4,
                "statement_a": "我喜欢设定目标并努力达成",
                "theme_a": "成就",
                "statement_b": "我喜欢灵活应对，随机应变",
                "theme_b": "适应",
                "domain": "执行力",
                "weight_a": 1,
                "weight_b": 1,
            },
            {
                "question_no": 5,
                "statement_a": "我善于分析数据和逻辑推理",
                "theme_a": "分析",
                "statement_b": "我善于从全局角度思考问题",
                "theme_b": "战略",
                "domain": "战略思维",
                "weight_a": 1,
                "weight_b": 1,
            },
            {
                "question_no": 6,
                "statement_a": "我言出必行，对承诺负责到底",
                "theme_a": "责任",
                "statement_b": "我会灵活调整，根据情况变化",
                "theme_b": "适应",
                "domain": "执行力",
                "weight_a": 1,
                "weight_b": 1,
            },
            {
                "question_no": 7,
                "statement_a": "我喜欢解决复杂的问题和挑战",
                "theme_a": "排难",
                "statement_b": "我喜欢预防问题的发生",
                "theme_b": "审慎",
                "domain": "执行力",
                "weight_a": 1,
                "weight_b": 1,
            },
            {
                "question_no": 8,
                "statement_a": "我重视公平公正，一视同仁",
                "theme_a": "公平",
                "statement_b": "我因人而异，灵活处理",
                "theme_b": "个别",
                "domain": "执行力",
                "weight_a": 1,
                "weight_b": 1,
            },
            {
                "question_no": 9,
                "statement_a": "我寻求共识，避免冲突",
                "theme_a": "和谐",
                "statement_b": "我直面冲突，解决分歧",
                "theme_b": "统率",
                "domain": "关系建立",
                "weight_a": 1,
                "weight_b": 1,
            },
            {
                "question_no": 10,
                "statement_a": "我喜欢思考抽象的概念和理念",
                "theme_a": "理念",
                "statement_b": "我更关注实际的应用和效果",
                "theme_b": "成就",
                "domain": "战略思维",
                "weight_a": 1,
                "weight_b": 1,
            },
            {
                "question_no": 11,
                "statement_a": "我接纳不同的观点和差异",
                "theme_a": "包容",
                "statement_b": "我有明确的标准和原则",
                "theme_b": "公平",
                "domain": "关系建立",
                "weight_a": 1,
                "weight_b": 1,
            },
            {
                "question_no": 12,
                "statement_a": "我能够快速适应新环境",
                "theme_a": "适应",
                "statement_b": "我喜欢建立稳定的惯例",
                "theme_b": "纪律",
                "domain": "执行力",
                "weight_a": 1,
                "weight_b": 1,
            },
            {
                "question_no": 13,
                "statement_a": "我能够长时间专注一件事",
                "theme_a": "专注",
                "statement_b": "我喜欢同时处理多个任务",
                "theme_b": "统筹",
                "domain": "执行力",
                "weight_a": 1,
                "weight_b": 1,
            },
            {
                "question_no": 14,
                "statement_a": "我喜欢收集和整理信息",
                "theme_a": "搜集",
                "statement_b": "我喜欢提炼关键信息",
                "theme_b": "分析",
                "domain": "战略思维",
                "weight_a": 1,
                "weight_b": 1,
            },
            {
                "question_no": 15,
                "statement_a": "我享受学习新知识和技能",
                "theme_a": "学习",
                "statement_b": "我擅长深入钻研某一领域",
                "theme_b": "专注",
                "domain": "战略思维",
                "weight_a": 1,
                "weight_b": 1,
            },
            {
                "question_no": 16,
                "statement_a": "我善于预见未来的可能性",
                "theme_a": "前瞻",
                "statement_b": "我善于总结过去的经验教训",
                "theme_b": "回顾",
                "domain": "战略思维",
                "weight_a": 1,
                "weight_b": 1,
            },
            {
                "question_no": 17,
                "statement_a": "我善于制定长远战略规划",
                "theme_a": "战略",
                "statement_b": "我善于灵活应对当前挑战",
                "theme_b": "行动",
                "domain": "战略思维",
                "weight_a": 1,
                "weight_b": 1,
            },
            {
                "question_no": 18,
                "statement_a": "我善于独立思考和内省",
                "theme_a": "思维",
                "statement_b": "我善于与他人讨论交流",
                "theme_b": "沟通",
                "domain": "战略思维",
                "weight_a": 1,
                "weight_b": 1,
            },
            {
                "question_no": 19,
                "statement_a": "我行动前会谨慎评估风险",
                "theme_a": "审慎",
                "statement_b": "我愿意冒险，抓住机会",
                "theme_b": "行动",
                "domain": "执行力",
                "weight_a": 1,
                "weight_b": 1,
            },
            {
                "question_no": 20,
                "statement_a": "我倾向于立即行动",
                "theme_a": "行动",
                "statement_b": "我倾向于深思熟虑后再行动",
                "theme_b": "审慎",
                "domain": "执行力",
                "weight_a": 1,
                "weight_b": 1,
            },
            {
                "question_no": 21,
                "statement_a": "我总是保持积极乐观的态度",
                "theme_a": "积极",
                "statement_b": "我倾向于客观冷静分析",
                "theme_b": "分析",
                "domain": "关系建立",
                "weight_a": 1,
                "weight_b": 1,
            },
            {
                "question_no": 22,
                "statement_a": "我喜欢结交新朋友",
                "theme_a": "取悦",
                "statement_b": "我喜欢与老朋友深度交流",
                "theme_b": "交往",
                "domain": "影响力",
                "weight_a": 1,
                "weight_b": 1,
            },
            {
                "question_no": 23,
                "statement_a": "我对自己的能力充满信心",
                "theme_a": "自信",
                "statement_b": "我相信能力可以不断提升",
                "theme_b": "学习",
                "domain": "影响力",
                "weight_a": 1,
                "weight_b": 1,
            },
            {
                "question_no": 24,
                "statement_a": "我追求卓越，力求完美",
                "theme_a": "完美",
                "statement_b": "我注重实效，追求成果",
                "theme_b": "成就",
                "domain": "影响力",
                "weight_a": 1,
                "weight_b": 1,
            },
            {
                "question_no": 25,
                "statement_a": "我相信天生的才能更重要",
                "theme_a": "自信",
                "statement_b": "我相信努力可以改变一切",
                "theme_b": "学习",
                "domain": "影响力",
                "weight_a": 1,
                "weight_b": 1,
            },
            {
                "question_no": 26,
                "statement_a": "我渴望成为焦点，被大家关注",
                "theme_a": "追求",
                "statement_b": "我prefer默默做好自己的事",
                "theme_b": "责任",
                "domain": "影响力",
                "weight_a": 1,
                "weight_b": 1,
            },
            {
                "question_no": 27,
                "statement_a": "我喜欢领导和指挥他人",
                "theme_a": "统率",
                "statement_b": "我喜欢配合和支持他人",
                "theme_b": "伯乐",
                "domain": "影响力",
                "weight_a": 1,
                "weight_b": 1,
            },
            {
                "question_no": 28,
                "statement_a": "我相信努力就会有收获",
                "theme_a": "成就",
                "statement_b": "我相信时机和运气更重要",
                "theme_b": "前瞻",
                "domain": "执行力",
                "weight_a": 1,
                "weight_b": 1,
            },
            {
                "question_no": 29,
                "statement_a": "我喜欢有备无患",
                "theme_a": "审慎",
                "statement_b": "我喜欢兵来将挡，水来土掩",
                "theme_b": "适应",
                "domain": "执行力",
                "weight_a": 1,
                "weight_b": 1,
            },
            {
                "question_no": 30,
                "statement_a": "我坚持按照计划执行",
                "theme_a": "纪律",
                "statement_b": "我会根据实际情况调整计划",
                "theme_b": "适应",
                "domain": "执行力",
                "weight_a": 1,
                "weight_b": 1,
            },
            {
                "question_no": 31,
                "statement_a": "我坚定自己的信念和价值观",
                "theme_a": "信仰",
                "statement_b": "我的信念会随经验改变",
                "theme_b": "学习",
                "domain": "执行力",
                "weight_a": 1,
                "weight_b": 1,
            },
            {
                "question_no": 32,
                "statement_a": "我相信每个问题都有标准答案",
                "theme_a": "分析",
                "statement_b": "我相信每个问题有多种解法",
                "theme_b": "战略",
                "domain": "战略思维",
                "weight_a": 1,
                "weight_b": 1,
            },
            {
                "question_no": 33,
                "statement_a": "我喜欢回顾过去，总结经验",
                "theme_a": "回顾",
                "statement_b": "我喜欢展望未来，设想可能",
                "theme_b": "前瞻",
                "domain": "战略思维",
                "weight_a": 1,
                "weight_b": 1,
            },
            {
                "question_no": 34,
                "statement_a": "我相信所有事情都有意义",
                "theme_a": "关联",
                "statement_b": "我只相信眼前的事实",
                "theme_b": "分析",
                "domain": "关系建立",
                "weight_a": 1,
                "weight_b": 1,
            },
            {
                "question_no": 35,
                "statement_a": "我善于发现并培养他人的潜能",
                "theme_a": "伯乐",
                "statement_b": "我更相信自己动手",
                "theme_b": "排难",
                "domain": "关系建立",
                "weight_a": 1,
                "weight_b": 1,
            },
            {
                "question_no": 36,
                "statement_a": "我prefer团队合作",
                "theme_a": "交往",
                "statement_b": "我prefer独立工作",
                "theme_b": "思维",
                "domain": "关系建立",
                "weight_a": 1,
                "weight_b": 1,
            },
            {
                "question_no": 37,
                "statement_a": "我相信真诚是交往的基础",
                "theme_a": "关联",
                "statement_b": "我相信信任是交往的基础",
                "theme_b": "和谐",
                "domain": "关系建立",
                "weight_a": 1,
                "weight_b": 1,
            },
            {
                "question_no": 38,
                "statement_a": "我善于看到每个人的独特之处",
                "theme_a": "个别",
                "statement_b": "我善于看到大家的共同点",
                "theme_b": "关联",
                "domain": "关系建立",
                "weight_a": 1,
                "weight_b": 1,
            },
            {
                "question_no": 39,
                "statement_a": "我会严格遵守规则和流程",
                "theme_a": "纪律",
                "statement_b": "我会灵活解释规则",
                "theme_b": "个别",
                "domain": "执行力",
                "weight_a": 1,
                "weight_b": 1,
            },
            {
                "question_no": 40,
                "statement_a": "我总是追求更好的结果",
                "theme_a": "完美",
                "statement_b": "我接受足够好的结果",
                "theme_b": "适应",
                "domain": "影响力",
                "weight_a": 1,
                "weight_b": 1,
            },
            {
                "question_no": 41,
                "statement_a": "我相信竞争使人进步",
                "theme_a": "竞争",
                "statement_b": "我相信合作使人进步",
                "theme_b": "伯乐",
                "domain": "影响力",
                "weight_a": 1,
                "weight_b": 1,
            },
            {
                "question_no": 42,
                "statement_a": "我善于同时处理多个项目",
                "theme_a": "统筹",
                "statement_b": "我善于专注一个项目",
                "theme_b": "专注",
                "domain": "执行力",
                "weight_a": 1,
                "weight_b": 1,
            },
            {
                "question_no": 43,
                "statement_a": "我相信直觉和第六感",
                "theme_a": "前瞻",
                "statement_b": "我相信数据和事实",
                "theme_b": "分析",
                "domain": "战略思维",
                "weight_a": 1,
                "weight_b": 1,
            },
            {
                "question_no": 44,
                "statement_a": "我prefer有挑战性的工作",
                "theme_a": "排难",
                "statement_b": "我prefer稳定性工作",
                "theme_b": "纪律",
                "domain": "执行力",
                "weight_a": 1,
                "weight_b": 1,
            },
            {
                "question_no": 45,
                "statement_a": "我善于用创意解决问题",
                "theme_a": "分析",
                "statement_b": "我善于用经验解决问题",
                "theme_b": "回顾",
                "domain": "战略思维",
                "weight_a": 1,
                "weight_b": 1,
            },
            {
                "question_no": 46,
                "statement_a": "我喜欢设定长期目标",
                "theme_a": "前瞻",
                "statement_b": "我喜欢设定短期目标",
                "theme_b": "行动",
                "domain": "战略思维",
                "weight_a": 1,
                "weight_b": 1,
            },
            {
                "question_no": 47,
                "statement_a": "我善于组织团队活动",
                "theme_a": "统筹",
                "statement_b": "我善于参与团队活动",
                "theme_b": "交往",
                "domain": "关系建立",
                "weight_a": 1,
                "weight_b": 1,
            },
            {
                "question_no": 48,
                "statement_a": "我相信细节决定成败",
                "theme_a": "审慎",
                "statement_b": "我相信大局观更重要",
                "theme_b": "战略",
                "domain": "执行力",
                "weight_a": 1,
                "weight_b": 1,
            },
        ]
_sbti_service: Optional["SBTIService"] = None


def get_sbti_service() -> "SBTIService":
    """获取SBTI服务实例"""
    global _sbti_service
    if _sbti_service is None:
        _sbti_service = SBTIService()
    return _sbti_service
