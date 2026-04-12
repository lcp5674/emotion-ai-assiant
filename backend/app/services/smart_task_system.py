"""
智能任务系统
实现AI生成个性化成长任务和任务难度自适应调整
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, func
import loguru
import random
import uuid

from app.models.growth_models_enhanced import (
    GrowthDimension,
    SmartTask,
    TaskDifficultyHistory,
    UserGrowthDimension,
)
from app.services.growth_service import get_growth_service
from app.services.growth_service_enhanced import get_growth_service_enhanced


class SmartTaskSystem:
    """智能任务系统"""

    # 任务难度配置
    DIFFICULTY_LEVELS = ["easy", "medium", "hard", "expert"]

    # 任务模板库 - 按维度和难度分类
    TASK_TEMPLATES = {
        GrowthDimension.EMOTIONAL_HEALTH.value: {
            "easy": [
                {
                    "title": "记录今日情绪",
                    "description": "花5分钟写下今天最强烈的情绪是什么，以及它触发的原因",
                    "estimated_time": 5,
                    "reward_exp": 15,
                    "dimension_exp": {"emotional_health": 10},
                },
                {
                    "title": "感恩练习",
                    "description": "列出今天让你感恩的3件小事",
                    "estimated_time": 5,
                    "reward_exp": 15,
                    "dimension_exp": {"emotional_health": 10},
                },
            ],
            "medium": [
                {
                    "title": "情绪调节练习",
                    "description": "当你感受到负面情绪时，尝试深呼吸3分钟并记录情绪变化",
                    "estimated_time": 10,
                    "reward_exp": 30,
                    "dimension_exp": {"emotional_health": 20},
                },
                {
                    "title": "情绪日记",
                    "description": "记录一天中不同时段的情绪变化，寻找情绪规律",
                    "estimated_time": 15,
                    "reward_exp": 35,
                    "dimension_exp": {"emotional_health": 25},
                },
            ],
            "hard": [
                {
                    "title": "情绪复盘分析",
                    "description": "选择本周一次情绪波动事件，深入分析触发模式和应对方式",
                    "estimated_time": 25,
                    "reward_exp": 60,
                    "dimension_exp": {"emotional_health": 40, "self_awareness": 20},
                },
            ],
        },
        GrowthDimension.SELF_AWARENESS.value: {
            "easy": [
                {
                    "title": "自我赞美",
                    "description": "写下今天你做得好的一件事并赞美自己",
                    "estimated_time": 5,
                    "reward_exp": 15,
                    "dimension_exp": {"self_awareness": 10},
                },
                {
                    "title": "价值观探索",
                    "description": "列出你最看重的3个价值观",
                    "estimated_time": 8,
                    "reward_exp": 20,
                    "dimension_exp": {"self_awareness": 15},
                },
            ],
            "medium": [
                {
                    "title": "优势探索",
                    "description": "回顾过去一个月，找出自己展现的3个优势",
                    "estimated_time": 15,
                    "reward_exp": 35,
                    "dimension_exp": {"self_awareness": 25},
                },
            ],
            "hard": [
                {
                    "title": "人生目标思考",
                    "description": "写下你未来1-3年想要达成的3个重要目标",
                    "estimated_time": 30,
                    "reward_exp": 70,
                    "dimension_exp": {"self_awareness": 50},
                },
            ],
        },
        GrowthDimension.SOCIAL_SKILLS.value: {
            "easy": [
                {
                    "title": "主动问候",
                    "description": "今天主动向一个人问候",
                    "estimated_time": 2,
                    "reward_exp": 10,
                    "dimension_exp": {"social_skills": 8},
                },
                {
                    "title": "真诚赞美",
                    "description": "给予身边的人一个真诚的赞美",
                    "estimated_time": 3,
                    "reward_exp": 12,
                    "dimension_exp": {"social_skills": 10},
                },
            ],
            "medium": [
                {
                    "title": "深入对话",
                    "description": "与朋友或家人进行一次15分钟的深入对话",
                    "estimated_time": 20,
                    "reward_exp": 40,
                    "dimension_exp": {"social_skills": 30},
                },
            ],
            "hard": [
                {
                    "title": "主动社交",
                    "description": "主动邀请朋友或同事进行一次社交活动",
                    "estimated_time": 60,
                    "reward_exp": 80,
                    "dimension_exp": {"social_skills": 50},
                },
            ],
        },
        GrowthDimension.RESILIENCE.value: {
            "easy": [
                {
                    "title": "小挑战",
                    "description": "今天做一件稍微超出舒适区的小事",
                    "estimated_time": 10,
                    "reward_exp": 15,
                    "dimension_exp": {"resilience": 10},
                },
            ],
            "medium": [
                {
                    "title": "挫折回顾",
                    "description": "回顾一次过去的挫折，写下你从中学到了什么",
                    "estimated_time": 20,
                    "reward_exp": 40,
                    "dimension_exp": {"resilience": 30},
                },
            ],
            "hard": [
                {
                    "title": "压力管理计划",
                    "description": "制定一个应对压力的具体计划",
                    "estimated_time": 30,
                    "reward_exp": 70,
                    "dimension_exp": {"resilience": 50},
                },
            ],
        },
        GrowthDimension.CREATIVITY.value: {
            "easy": [
                {
                    "title": "自由绘画",
                    "description": "花10分钟随意涂鸦，不用在乎画得好不好",
                    "estimated_time": 10,
                    "reward_exp": 15,
                    "dimension_exp": {"creativity": 10},
                },
                {
                    "title": "创意联想",
                    "description": "选择一个日常物品，想出它的10种不同用途",
                    "estimated_time": 8,
                    "reward_exp": 15,
                    "dimension_exp": {"creativity": 10},
                },
            ],
            "medium": [
                {
                    "title": "写小故事",
                    "description": "写一个100字左右的短故事",
                    "estimated_time": 20,
                    "reward_exp": 35,
                    "dimension_exp": {"creativity": 25},
                },
            ],
            "hard": [
                {
                    "title": "创意项目",
                    "description": "开始一个小型创意项目（写诗、作曲、手工等）",
                    "estimated_time": 60,
                    "reward_exp": 80,
                    "dimension_exp": {"creativity": 60},
                },
            ],
        },
        GrowthDimension.MINDFULNESS.value: {
            "easy": [
                {
                    "title": "正念呼吸",
                    "description": "进行5分钟的正念呼吸练习",
                    "estimated_time": 5,
                    "reward_exp": 15,
                    "dimension_exp": {"mindfulness": 10},
                },
                {
                    "title": "感官觉察",
                    "description": "花3分钟仔细观察周围环境，记录5种你注意到的事物",
                    "estimated_time": 5,
                    "reward_exp": 12,
                    "dimension_exp": {"mindfulness": 8},
                },
            ],
            "medium": [
                {
                    "title": "正念进食",
                    "description": "选择一餐，全程正念地品尝食物",
                    "estimated_time": 20,
                    "reward_exp": 35,
                    "dimension_exp": {"mindfulness": 25},
                },
                {
                    "title": "身体扫描",
                    "description": "进行15分钟的身体扫描冥想",
                    "estimated_time": 15,
                    "reward_exp": 30,
                    "dimension_exp": {"mindfulness": 22},
                },
            ],
            "hard": [
                {
                    "title": "深度冥想",
                    "description": "完成一次30分钟的冥想练习",
                    "estimated_time": 30,
                    "reward_exp": 65,
                    "dimension_exp": {"mindfulness": 45},
                },
            ],
        },
    }

    def __init__(self):
        self.growth_service = get_growth_service()
        self.growth_service_enhanced = get_growth_service_enhanced()

    # ============ 用户画像分析 ============

    def _build_user_profile(self, db: Session, user_id: int) -> Dict[str, Any]:
        """构建用户画像"""
        dimensions = self.growth_service_enhanced.get_user_dimensions(db, user_id)
        dimension_scores = {d.dimension: d.score for d in dimensions}
        dimension_levels = {d.dimension: d.level for d in dimensions}
        
        history = db.query(TaskDifficultyHistory).filter(
            TaskDifficultyHistory.user_id == user_id
        ).order_by(desc(TaskDifficultyHistory.created_at)).limit(20).all()
        
        success_rates = {}
        for dim in GrowthDimension:
            dim_history = [h for h in history if h.dimension == dim.value]
            if dim_history:
                success_count = sum(1 for h in dim_history if h.was_successful)
                success_rates[dim.value] = success_count / len(dim_history)
            else:
                success_rates[dim.value] = 0.5
        
        return {
            "dimension_scores": dimension_scores,
            "dimension_levels": dimension_levels,
            "success_rates": success_rates,
            "total_tasks_completed": len(history),
        }

    # ============ 难度自适应算法 ============

    def _calculate_optimal_difficulty(
        self,
        user_profile: Dict[str, Any],
        dimension: str,
    ) -> str:
        """计算最优难度"""
        success_rate = user_profile["success_rates"].get(dimension, 0.5)
        dimension_score = user_profile["dimension_scores"].get(dimension, 0)
        
        base_level = 0
        if dimension_score >= 70:
            base_level = 2
        elif dimension_score >= 40:
            base_level = 1
        
        adjustment = 0
        if success_rate > 0.85:
            adjustment = 1
        elif success_rate < 0.3:
            adjustment = -1
        
        level = max(0, min(len(self.DIFFICULTY_LEVELS) - 1, base_level + adjustment))
        return self.DIFFICULTY_LEVELS[level]

    # ============ AI任务生成 ============

    def generate_tasks(
        self,
        db: Session,
        user_id: int,
        dimension: Optional[str] = None,
        difficulty: Optional[str] = None,
        count: int = 1,
    ) -> List[SmartTask]:
        """生成个性化任务"""
        user_profile = self._build_user_profile(db, user_id)
        
        if dimension is None:
            dimensions = list(GrowthDimension)
            dimension = random.choice(dimensions).value
        
        if difficulty is None:
            difficulty = self._calculate_optimal_difficulty(user_profile, dimension)
        
        templates = self.TASK_TEMPLATES.get(dimension, {}).get(difficulty, [])
        if not templates:
            for diff in self.DIFFICULTY_LEVELS:
                templates = self.TASK_TEMPLATES.get(dimension, {}).get(diff, [])
                if templates:
                    difficulty = diff
                    break
        
        selected_templates = random.sample(templates, min(count, len(templates)))
        
        tasks = []
        for template in selected_templates:
            task_code = f"task_{uuid.uuid4().hex[:8]}"
            
            task = SmartTask(
                user_id=user_id,
                task_code=task_code,
                title=template["title"],
                description=template["description"],
                ai_generated=True,
                generation_prompt=f"Generate {difficulty} task for {dimension}",
                user_profile=user_profile,
                difficulty=difficulty,
                dimension=dimension,
                estimated_time_minutes=template["estimated_time"],
                target=1,
                current=0,
                is_completed=False,
                is_rewarded=False,
                reward_exp=template["reward_exp"],
                reward_dimension_exp=template["dimension_exp"],
                deadline=datetime.now() + timedelta(days=3),
            )
            
            db.add(task)
            tasks.append(task)
        
        db.commit()
        loguru.logger.info(f"为用户 {user_id} 生成了 {len(tasks)} 个智能任务")
        
        return tasks

    # ============ 任务管理 ============

    def get_user_smart_tasks(
        self,
        db: Session,
        user_id: int,
        include_completed: bool = False,
    ) -> List[SmartTask]:
        """获取用户智能任务"""
        query = db.query(SmartTask).filter(SmartTask.user_id == user_id)
        
        if not include_completed:
            query = query.filter(SmartTask.is_completed == False)
        
        return query.order_by(desc(SmartTask.created_at)).all()

    def get_task(self, db: Session, user_id: int, task_id: int) -> Optional[SmartTask]:
        """获取单个任务"""
        return db.query(SmartTask).filter(
            and_(SmartTask.user_id == user_id, SmartTask.id == task_id)
        ).first()

    def update_task_progress(
        self,
        db: Session,
        user_id: int,
        task_id: int,
        progress: int,
    ) -> Optional[SmartTask]:
        """更新任务进度"""
        task = self.get_task(db, user_id, task_id)
        if not task:
            return None
        
        task.current = min(task.target, max(0, progress))
        
        if task.current >= task.target and not task.is_completed:
            task.is_completed = True
            task.completed_at = datetime.now()
        
        db.commit()
        return task

    def complete_task(
        self,
        db: Session,
        user_id: int,
        task_id: int,
        feedback_score: Optional[float] = None,
        completion_time_minutes: Optional[int] = None,
    ) -> Optional[Dict[str, Any]]:
        """完成任务并领取奖励"""
        task = self.get_task(db, user_id, task_id)
        if not task:
            return None
        
        if task.is_completed and task.is_rewarded:
            return {"task": task, "already_rewarded": True}
        
        task.is_completed = True
        task.is_rewarded = True
        task.completed_at = datetime.now()
        
        was_successful = feedback_score is None or feedback_score >= 3
        
        if task.dimension:
            history = TaskDifficultyHistory(
                user_id=user_id,
                task_id=task.id,
                dimension=task.dimension,
                difficulty=task.difficulty,
                completion_time_minutes=completion_time_minutes,
                was_successful=was_successful,
                feedback_score=feedback_score,
            )
            db.add(history)
        
        reward_result = None
        if task.reward_exp > 0:
            reward_result = self.growth_service.add_exp(
                db, user_id, "task_complete", task.id,
                f"完成智能任务: {task.title}"
            )
        
        for dim, exp in task.reward_dimension_exp.items():
            score_delta = 0.5 if was_successful else 0.1
            self.growth_service_enhanced.add_dimension_exp(
                db, user_id, dim, exp, score_delta
            )
        
        db.commit()
        
        return {
            "task": task,
            "reward_exp": task.reward_exp,
            "reward_dimension_exp": task.reward_dimension_exp,
            "result": reward_result,
        }

    def delete_task(self, db: Session, user_id: int, task_id: int) -> bool:
        """删除任务"""
        task = self.get_task(db, user_id, task_id)
        if not task:
            return False
        
        db.delete(task)
        db.commit()
        return True

    # ============ 推荐任务 ============

    def get_recommended_tasks(
        self,
        db: Session,
        user_id: int,
        count: int = 3,
    ) -> List[Dict[str, Any]]:
        """获取推荐任务"""
        user_profile = self._build_user_profile(db, user_id)
        
        weakest_dimensions = sorted(
            user_profile["dimension_scores"].items(),
            key=lambda x: x[1]
        )[:2]
        
        recommendations = []
        
        for dim, _ in weakest_dimensions:
            optimal_diff = self._calculate_optimal_difficulty(user_profile, dim)
            
            templates = self.TASK_TEMPLATES.get(dim, {}).get(optimal_diff, [])
            if templates:
                template = random.choice(templates)
                recommendations.append({
                    "dimension": dim,
                    "difficulty": optimal_diff,
                    "title": template["title"],
                    "description": template["description"],
                    "estimated_time": template["estimated_time"],
                    "reward_exp": template["reward_exp"],
                })
        
        while len(recommendations) < count:
            dim = random.choice(list(GrowthDimension)).value
            optimal_diff = self._calculate_optimal_difficulty(user_profile, dim)
            templates = self.TASK_TEMPLATES.get(dim, {}).get(optimal_diff, [])
            if templates:
                template = random.choice(templates)
                rec = {
                    "dimension": dim,
                    "difficulty": optimal_diff,
                    "title": template["title"],
                    "description": template["description"],
                    "estimated_time": template["estimated_time"],
                    "reward_exp": template["reward_exp"],
                }
                if rec not in recommendations:
                    recommendations.append(rec)
        
        return recommendations[:count]


_smart_task_system: Optional[SmartTaskSystem] = None


def get_smart_task_system() -> SmartTaskSystem:
    """获取智能任务系统实例"""
    global _smart_task_system
    if _smart_task_system is None:
        _smart_task_system = SmartTaskSystem()
    return _smart_task_system
