"""
数据质量服务 - 确保数据的时效性、完整性、一致性和安全性
"""
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum
import hashlib
import json
import loguru

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_


class DataQualityLevel(str, Enum):
    """数据质量等级"""
    EXCELLENT = "excellent"    # 优秀
    GOOD = "good"              # 良好
    FAIR = "fair"              # 一般
    POOR = "poor"             # 较差


class DataQualityReport:
    """数据质量报告"""
    def __init__(
        self,
        dimension: str,
        level: DataQualityLevel,
        score: float,
        issues: List[str],
        suggestions: List[str],
    ):
        self.dimension = dimension
        self.level = level
        self.score = score  # 0-100
        self.issues = issues
        self.suggestions = suggestions

    def to_dict(self) -> Dict[str, Any]:
        return {
            "dimension": self.dimension,
            "level": self.level.value,
            "score": self.score,
            "issues": self.issues,
            "suggestions": self.suggestions,
        }


class DataQualityService:
    """数据质量服务"""

    def __init__(self):
        self._cache_ttl = timedelta(hours=1)

    def assess_timeliness(
        self,
        db: Session,
        user_id: int,
    ) -> DataQualityReport:
        """评估数据时效性"""
        issues = []
        suggestions = []
        score = 100

        from app.models import MbtiResult, SBTIResult, AttachmentResult

        # 检查MBTI结果时效
        mbti_result = db.query(MbtiResult).filter(
            MbtiResult.user_id == user_id,
            MbtiResult.is_latest == True
        ).first()

        if mbti_result:
            days_since = (datetime.now() - mbti_result.created_at).days
            if days_since > 365:
                issues.append(f"MBTI结果已超过1年未更新")
                suggestions.append("建议重新测评以获得更准确的人格分析")
                score -= 15
            elif days_since > 180:
                issues.append(f"MBTI结果已超过6个月")
                suggestions.append("考虑是否需要更新以反映个人成长")
                score -= 5

        # 检查SBTI结果时效
        sbti_result = db.query(SBTIResult).filter(
            SBTIResult.user_id == user_id,
            SBTIResult.is_latest == True
        ).first()

        if sbti_result:
            days_since = (datetime.now() - sbti_result.created_at).days
            if days_since > 365:
                issues.append(f"SBTI结果已超过1年未更新")
                suggestions.append("建议重新测评以反映才干发展变化")
                score -= 15
            elif days_since > 180:
                issues.append(f"SBTI结果已超过6个月")
                suggestions.append("考虑是否需要更新以反映个人成长")
                score -= 5

        # 检查依恋风格结果时效
        attachment_result = db.query(AttachmentResult).filter(
            AttachmentResult.user_id == user_id,
            AttachmentResult.is_latest == True
        ).first()

        if attachment_result:
            days_since = (datetime.now() - attachment_result.created_at).days
            if days_since > 365:
                issues.append(f"依恋风格结果已超过1年未更新")
                suggestions.append("建议重新测评以反映依恋模式的发展")
                score -= 15
            elif days_since > 180:
                issues.append(f"依恋风格结果已超过6个月")
                suggestions.append("考虑是否需要更新以反映个人成长")
                score -= 5

        # 确定等级
        if score >= 90:
            level = DataQualityLevel.EXCELLENT
        elif score >= 70:
            level = DataQualityLevel.GOOD
        elif score >= 50:
            level = DataQualityLevel.FAIR
        else:
            level = DataQualityLevel.POOR

        return DataQualityReport(
            dimension="timeliness",
            level=level,
            score=max(0, score),
            issues=issues,
            suggestions=suggestions,
        )

    def assess_completeness(
        self,
        db: Session,
        user_id: int,
    ) -> DataQualityReport:
        """评估数据完整性"""
        issues = []
        suggestions = []
        score = 0
        max_score = 100
        step = max_score / 3  # 三个测评各占33.33分

        from app.models import MbtiResult, SBTIResult, AttachmentResult

        # MBTI完整性
        mbti_result = db.query(MbtiResult).filter(
            MbtiResult.user_id == user_id,
            MbtiResult.is_latest == True
        ).first()

        if mbti_result:
            score += step
            # 检查MBTI结果完整性
            if not mbti_result.mbti_type:
                issues.append("MBTI类型未记录")
                score -= step / 2
        else:
            issues.append("缺少MBTI测评结果")
            suggestions.append("完成MBTI测评以获得完整的人格画像")

        # SBTI完整性
        sbti_result = db.query(SBTIResult).filter(
            SBTIResult.user_id == user_id,
            SBTIResult.is_latest == True
        ).first()

        if sbti_result:
            score += step
            # 检查SBTI结果完整性
            if not sbti_result.top_theme_1:
                issues.append("SBTI Top5才干未完整记录")
                score -= step / 2
        else:
            issues.append("缺少SBTI测评结果")
            suggestions.append("完成SBTI测评以发现你的核心才干")

        # 依恋风格完整性
        attachment_result = db.query(AttachmentResult).filter(
            AttachmentResult.user_id == user_id,
            AttachmentResult.is_latest == True
        ).first()

        if attachment_result:
            score += step
            # 检查依恋风格结果完整性
            if not attachment_result.attachment_style:
                issues.append("依恋风格类型未记录")
                score -= step / 2
        else:
            issues.append("缺少依恋风格测评结果")
            suggestions.append("完成依恋风格测评以了解你的关系模式")

        # 深度画像完整性
        if mbti_result and sbti_result and attachment_result:
            # 三个测评都完成，深度画像才完整
            pass
        elif mbti_result or sbti_result or attachment_result:
            suggestions.append("完成全部三个测评以生成深度人格画像")

        # 确定等级
        if score >= 90:
            level = DataQualityLevel.EXCELLENT
        elif score >= 70:
            level = DataQualityLevel.GOOD
        elif score >= 50:
            level = DataQualityLevel.FAIR
        else:
            level = DataQualityLevel.POOR

        return DataQualityReport(
            dimension="completeness",
            level=level,
            score=min(100, max(0, score)),
            issues=issues,
            suggestions=suggestions,
        )

    def assess_consistency(
        self,
        db: Session,
        user_id: int,
    ) -> DataQualityReport:
        """评估数据一致性"""
        issues = []
        suggestions = []
        score = 100

        from app.models import User, MbtiResult, SBTIResult, AttachmentResult

        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return DataQualityReport(
                dimension="consistency",
                level=DataQualityLevel.POOR,
                score=0,
                issues=["用户不存在"],
                suggestions=["请重新注册"],
            )

        # 检查用户的外键关联是否有效
        if user.mbti_result_id:
            mbti = db.query(MbtiResult).filter(
                MbtiResult.id == user.mbti_result_id
            ).first()
            if not mbti:
                issues.append("用户MBTI结果ID指向不存在的记录")
                suggestions.append("清除失效的MBTI结果关联")
                score -= 20
            elif not mbti.is_latest:
                issues.append("用户MBTI结果ID指向非最新记录")
                suggestions.append("更新为最新的MBTI结果ID")
                score -= 10

        if user.sbti_result_id:
            sbti = db.query(SBTIResult).filter(
                SBTIResult.id == user.sbti_result_id
            ).first()
            if not sbti:
                issues.append("用户SBTI结果ID指向不存在的记录")
                suggestions.append("清除失效的SBTI结果关联")
                score -= 20
            elif not sbti.is_latest:
                issues.append("用户SBTI结果ID指向非最新记录")
                suggestions.append("更新为最新的SBTI结果ID")
                score -= 10

        if user.attachment_result_id:
            attachment = db.query(AttachmentResult).filter(
                AttachmentResult.id == user.attachment_result_id
            ).first()
            if not attachment:
                issues.append("用户依恋风格结果ID指向不存在的记录")
                suggestions.append("清除失效的依恋风格结果关联")
                score -= 20
            elif not attachment.is_latest:
                issues.append("用户依恋风格结果ID指向非最新记录")
                suggestions.append("更新为最新的依恋风格结果ID")
                score -= 10

        # 检查历史结果是否被正确标记
        old_results = db.query(SBTIResult).filter(
            SBTIResult.user_id == user_id,
            SBTIResult.is_latest == False
        ).all()
        for result in old_results:
            if result.version > 1:
                # 有更新版本存在，这是正常的
                pass

        # 确定等级
        if score >= 90:
            level = DataQualityLevel.EXCELLENT
        elif score >= 70:
            level = DataQualityLevel.GOOD
        elif score >= 50:
            level = DataQualityLevel.FAIR
        else:
            level = DataQualityLevel.POOR

        return DataQualityReport(
            dimension="consistency",
            level=level,
            score=max(0, score),
            issues=issues,
            suggestions=suggestions,
        )

    def fix_consistency_issues(
        self,
        db: Session,
        user_id: int,
    ) -> Dict[str, Any]:
        """修复数据一致性问题"""
        fixed = []
        errors = []

        from app.models import User, MbtiResult, SBTIResult, AttachmentResult

        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            errors.append("用户不存在")
            return {"fixed": fixed, "errors": errors}

        # 修复MBTI结果关联
        if user.mbti_result_id:
            mbti = db.query(MbtiResult).filter(
                MbtiResult.id == user.mbti_result_id
            ).first()
            if not mbti or not mbti.is_latest:
                # 找到最新的结果
                latest = db.query(MbtiResult).filter(
                    MbtiResult.user_id == user_id,
                    MbtiResult.is_latest == True
                ).first()
                if latest:
                    user.mbti_result_id = latest.id
                    fixed.append(f"MBTI结果关联已更新为最新记录ID:{latest.id}")
                elif mbti:
                    user.mbti_result_id = None
                    fixed.append("MBTI结果关联已清除(无最新记录)")

        # 修复SBTI结果关联
        if user.sbti_result_id:
            sbti = db.query(SBTIResult).filter(
                SBTIResult.id == user.sbti_result_id
            ).first()
            if not sbti or not sbti.is_latest:
                latest = db.query(SBTIResult).filter(
                    SBTIResult.user_id == user_id,
                    SBTIResult.is_latest == True
                ).first()
                if latest:
                    user.sbti_result_id = latest.id
                    fixed.append(f"SBTI结果关联已更新为最新记录ID:{latest.id}")
                elif sbti:
                    user.sbti_result_id = None
                    fixed.append("SBTI结果关联已清除(无最新记录)")

        # 修复依恋风格结果关联
        if user.attachment_result_id:
            attachment = db.query(AttachmentResult).filter(
                AttachmentResult.id == user.attachment_result_id
            ).first()
            if not attachment or not attachment.is_latest:
                latest = db.query(AttachmentResult).filter(
                    AttachmentResult.user_id == user_id,
                    AttachmentResult.is_latest == True
                ).first()
                if latest:
                    user.attachment_result_id = latest.id
                    fixed.append(f"依恋风格结果关联已更新为最新记录ID:{latest.id}")
                elif attachment:
                    user.attachment_result_id = None
                    fixed.append("依恋风格结果关联已清除(无最新记录)")

        try:
            db.commit()
        except Exception as e:
            db.rollback()
            errors.append(f"数据库提交失败: {str(e)}")

        return {"fixed": fixed, "errors": errors}

    def get_overall_quality_score(
        self,
        db: Session,
        user_id: int,
    ) -> Dict[str, Any]:
        """获取整体数据质量评分"""
        timeliness = self.assess_timeliness(db, user_id)
        completeness = self.assess_completeness(db, user_id)
        consistency = self.assess_consistency(db, user_id)

        # 加权平均
        weights = {
            "timeliness": 0.25,
            "completeness": 0.40,
            "consistency": 0.35,
        }

        overall_score = (
            timeliness.score * weights["timeliness"] +
            completeness.score * weights["completeness"] +
            consistency.score * weights["consistency"]
        )

        # 确定整体等级
        if overall_score >= 90:
            overall_level = DataQualityLevel.EXCELLENT
        elif overall_score >= 70:
            overall_level = DataQualityLevel.GOOD
        elif overall_score >= 50:
            overall_level = DataQualityLevel.FAIR
        else:
            overall_level = DataQualityLevel.POOR

        return {
            "overall_score": round(overall_score, 2),
            "overall_level": overall_level.value,
            "dimensions": {
                "timeliness": timeliness.to_dict(),
                "completeness": completeness.to_dict(),
                "consistency": consistency.to_dict(),
            },
            "recommendations": list(set(
                timeliness.suggestions +
                completeness.suggestions +
                consistency.suggestions
            )),
        }


# 全局服务实例
_data_quality_service: Optional[DataQualityService] = None


def get_data_quality_service() -> DataQualityService:
    """获取数据质量服务实例"""
    global _data_quality_service
    if _data_quality_service is None:
        _data_quality_service = DataQualityService()
    return _data_quality_service
