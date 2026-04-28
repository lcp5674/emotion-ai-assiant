#!/usr/bin/env python3
"""
更新现有用户的昵称，基于其 MBTI 类型
用法: python scripts/update_user_nicknames.py
"""
import sys
import os

# 添加 backend 目录到 path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

import asyncio
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import random
import string

# MBTI 类型昵称后缀映射
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

def generate_unique_id():
    """生成2-4位随机字符"""
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=random.randint(2, 4)))

def generate_nickname_from_mbti(mbti_type, original_nickname=None):
    """根据 MBTI 类型生成昵称"""
    if not mbti_type:
        return None

    suffix = NICKNAME_SUFFIXES.get(mbti_type.upper(), "探索者")

    # 检查原始昵称是否是自动生成的
    is_auto_generated = False
    if original_nickname:
        if "用户" in original_nickname or len([c for c in original_nickname if c.isdigit()]) >= 4:
            is_auto_generated = True

    if is_auto_generated or not original_nickname:
        unique_id = generate_unique_id()
        return f"{suffix}{unique_id}"
    else:
        # 保留用户自定义昵称，只更新自动生成的
        return original_nickname

async def main():
    # 从环境变量获取数据库连接
    mysql_host = os.getenv('MYSQL_HOST', 'localhost')
    mysql_port = os.getenv('MYSQL_PORT', '3306')
    mysql_user = os.getenv('MYSQL_USER', 'emotion_ai')
    mysql_password = os.getenv('MYSQL_PASSWORD', '')
    mysql_database = os.getenv('MYSQL_DATABASE', 'emotion_ai')

    if not mysql_password:
        print("错误: 请设置 MYSQL_PASSWORD 环境变量")
        return

    connection_string = f"mysql+pymysql://{mysql_user}:{mysql_password}@{mysql_host}:{mysql_port}/{mysql_database}"

    engine = create_engine(connection_string)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # 查询所有有 MBTI 类型但昵称是自动生成的用户
        query = text("""
            SELECT id, nickname, mbti_type, phone
            FROM users
            WHERE mbti_type IS NOT NULL
            AND mbti_type != ''
            AND (nickname LIKE '用户%' OR nickname LIKE '心灵%' OR nickname LIKE '星光%'
                 OR nickname LIKE '月光%' OR nickname LIKE '阳光%' OR nickname LIKE '彩虹%'
                 OR nickname LIKE '清风%' OR nickname LIKE '白云%' OR nickname LIKE '彩云%'
                 OR nickname LIKE '星辰%' OR nickname LIKE '流云%')
        """)

        result = session.execute(query)
        users = result.fetchall()

        print(f"找到 {len(users)} 个需要更新昵称的用户")

        updated_count = 0
        for user in users:
            user_id, nickname, mbti_type, phone = user
            new_nickname = generate_nickname_from_mbti(mbti_type, nickname)

            if new_nickname and new_nickname != nickname:
                update_query = text("""
                    UPDATE users SET nickname = :new_nickname WHERE id = :user_id
                """)
                session.execute(update_query, {"new_nickname": new_nickname, "user_id": user_id})
                updated_count += 1
                print(f"用户 {user_id} (手机: {phone[-4:] if phone else 'N/A'}): {nickname} -> {new_nickname}")

        session.commit()
        print(f"\n更新完成! 共更新了 {updated_count} 个用户的昵称")

    except Exception as e:
        print(f"错误: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    asyncio.run(main())
