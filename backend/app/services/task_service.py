"""
定时任务服务 - 处理会员过期等定时任务
"""
from datetime import datetime
from sqlalchemy.orm import Session
import loguru

from app.core.database import SessionLocal
from app.models.user import User, MemberLevel


class TaskService:
    """定时任务服务"""

    @staticmethod
    def check_member_expiration():
        """检查并处理会员过期"""
        db: Session = SessionLocal()
        try:
            # 查找所有非免费会员且过期的用户
            expired_users = db.query(User).filter(
                User.member_level != MemberLevel.FREE,
                User.member_expire_at < datetime.now()
            ).all()

            for user in expired_users:
                # 将过期会员降级为免费用户
                user.member_level = MemberLevel.FREE
                loguru.logger.info(f"用户 {user.id} 会员已过期，已降级为免费用户")

            db.commit()
            loguru.logger.info(f"会员过期检查完成，处理了 {len(expired_users)} 个过期会员")
        except Exception as e:
            loguru.logger.error(f"会员过期检查失败: {e}")
            db.rollback()
        finally:
            db.close()

    @staticmethod
    def run_scheduled_tasks():
        """运行所有定时任务"""
        loguru.logger.info("开始执行定时任务")
        TaskService.check_member_expiration()
        loguru.logger.info("定时任务执行完成")


def run_scheduled_tasks():
    """运行定时任务的便捷函数"""
    TaskService.run_scheduled_tasks()
