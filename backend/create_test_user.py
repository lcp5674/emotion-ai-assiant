#!/usr/bin/env python3
"""
创建测试账号
"""
import sys
sys.path.append('..')

# 直接使用SQLAlchemy创建引擎和会话
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 导入用户模型和加密函数
from app.models.user import User
from app.core.security import get_password_hash

# 创建SQLite引擎
engine = create_engine('sqlite:///./emotion_ai.db', connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建测试用户
def create_test_user():
    db = SessionLocal()
    
    # 测试账号信息
    phone = "13800138000"
    password = "123456"
    nickname = "测试用户"
    
    # 检查用户是否已存在
    existing_user = db.query(User).filter(User.phone == phone).first()
    if existing_user:
        print(f"测试账号 {phone} 已存在")
        return
    
    # 创建新用户
    user = User(
        phone=phone,
        nickname=nickname,
        password_hash=get_password_hash(password),
        is_active=True,
        is_verified=True
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    print(f"测试账号创建成功！")
    print(f"手机号: {phone}")
    print(f"密码: {password}")
    print(f"用户ID: {user.id}")

if __name__ == "__main__":
    print("开始创建测试账号...")
    create_test_user()
    print("测试账号创建完成！")
