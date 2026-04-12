#!/usr/bin/env python3
"""
简单测试脚本 - 验证系统核心功能
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("  心灵伴侣AI - 简单功能测试")
print("=" * 60)

# 设置环境变量以避免数据库连接
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["SECRET_KEY"] = "dev-secret-key-change-in-production-at-least-32-chars"
os.environ["LLM_PROVIDER"] = "mock"
os.environ["VECTOR_DB_TYPE"] = "memory"

# 测试1: 导入核心模块
print("\n1. 测试核心模块导入...")
try:
    from app.core.config import settings
    print("   ✓ 配置模块导入成功")
    print(f"   应用名称: {settings.APP_NAME}")
    print(f"   版本: {settings.APP_VERSION}")
except Exception as e:
    print(f"   ✗ 配置模块导入失败: {e}")
    import traceback
    traceback.print_exc()

# 测试2: 导入数据库模块（不连接）
print("\n2. 测试模型模块导入...")
try:
    from app.models import user, chat, mbti
    print("   ✓ 核心模型模块导入成功")
except Exception as e:
    print(f"   ✗ 核心模型模块导入失败: {e}")
    import traceback
    traceback.print_exc()

# 测试3: 导入新功能模块
print("\n3. 测试新功能模块导入...")
try:
    from app.models import recommendation, feedback
    print("   ✓ 推荐和反馈模型导入成功")
except Exception as e:
    print(f"   ✗ 推荐和反馈模型导入失败: {e}")
    import traceback
    traceback.print_exc()

# 测试4: 导入服务模块
print("\n4. 测试服务模块导入...")
try:
    from app.services import (
        recommendation_service,
        feedback_service,
        analytics_insight_service,
        multimodal_service,
        trust_security_service
    )
    print("   ✓ 新功能服务导入成功:")
    print("     - 推荐服务")
    print("     - 反馈服务")
    print("     - 分析洞察服务")
    print("     - 多模态服务")
    print("     - 信任安全服务")
except Exception as e:
    print(f"   ✗ 新功能服务导入失败: {e}")
    import traceback
    traceback.print_exc()

# 测试5: 导入API模块
print("\n5. 测试API模块导入...")
try:
    from app.api.v1 import auth, chat, mbti, user
    print("   ✓ API模块导入成功")
except Exception as e:
    print(f"   ✗ API模块导入失败: {e}")
    import traceback
    traceback.print_exc()

# 测试6: 检查FastAPI应用创建
print("\n6. 测试FastAPI应用创建...")
try:
    from app.main import app
    print("   ✓ FastAPI应用创建成功")
    print(f"   应用标题: {app.title}")
except Exception as e:
    print(f"   ✗ FastAPI应用创建失败: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("  测试完成")
print("=" * 60)
