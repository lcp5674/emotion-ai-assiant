#!/usr/bin/env python3
"""
简单创建测试账号
"""
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import bcrypt

# 创建SQLite引擎
engine = create_engine('sqlite:///./emotion_ai.db', connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 定义用户模型
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    phone = Column(String(20), unique=True, nullable=False)
    nickname = Column(String(50), nullable=True)
    password_hash = Column(String(100), nullable=True)
    avatar = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    member_level = Column(String(20), default="free")
    mbti_type = Column(String(4), nullable=True)
    mbti_result_id = Column(Integer, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    last_login_at = Column(DateTime, nullable=True)

# 创建表结构
def create_tables():
    Base.metadata.create_all(bind=engine)
    print("表结构创建完成")

# 哈希密码
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

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
        password_hash=hash_password(password),
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
    create_tables()
    create_test_user()
    print("测试账号创建完成！")
