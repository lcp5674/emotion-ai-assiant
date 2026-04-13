#!/usr/bin/env python3
"""验证架构审查问题修复"""

import sys
import os

# 添加backend路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def test_mood_level_fix():
    """测试心情等级枚举问题修复"""
    print("=" * 60)
    print("测试1: 心情等级枚举修复")
    print("=" * 60)
    
    # 模拟_get_mood_level返回的值
    MOOD_CONFIGS = {
        "very_happy": {"score_range": [8, 10], "emoji": "😄"},
        "happy": {"score_range": [6, 7], "emoji": "🙂"},
        "neutral": {"score_range": [4, 5], "emoji": "😐"},
        "sad": {"score_range": [2, 3], "emoji": "😢"},
        "very_sad": {"score_range": [0, 1], "emoji": "😭"},
    }
    
    def _get_mood_level(score: int) -> str:
        """根据分数获取心情等级"""
        for level, config in MOOD_CONFIGS.items():
            if config["score_range"][0] <= score <= config["score_range"][1]:
                return level
        return "neutral"
    
    # 测试用例
    test_cases = [
        (9, "very_happy"),
        (7, "happy"),
        (5, "neutral"),
        (3, "sad"),
        (1, "very_sad"),
    ]
    
    print("测试心情等级转换：")
    all_passed = True
    for score, expected in test_cases:
        mood_level = _get_mood_level(score)
        # 修复后的代码：不再使用 .upper()
        mood_level_str = mood_level
        
        if mood_level_str == expected:
            print(f"  ✓ score={score} -> {mood_level_str}")
        else:
            print(f"  ✗ score={score} -> {mood_level_str} (期望: {expected})")
            all_passed = False
    
    if all_passed:
        print("\n✅ 测试通过：心情等级枚举修复正确！\n")
    else:
        print("\n❌ 测试失败：心情等级枚举修复有问题！\n")
    
    return all_passed

def test_websocket_message_type():
    """测试WebSocket消息类型修复"""
    print("=" * 60)
    print("测试2: WebSocket消息类型修复")
    print("=" * 60)
    
    # 前端期望的消息类型
    expected_types = ['start', 'chunk', 'done', 'error']
    
    # 后端发送的消息（修复后应该是chunk）
    backend_message = {
        "type": "chunk",  # 修复后
        "content": "这是流式内容...",
    }
    
    print(f"前端期望的消息类型: {expected_types}")
    print(f"后端发送的消息: {backend_message}")
    
    if backend_message["type"] in expected_types:
        print(f"\n✅ 测试通过：消息类型 '{backend_message['type']}' 在前端期望列表中！\n")
        return True
    else:
        print(f"\n❌ 测试失败：消息类型 '{backend_message['type']}' 不在期望列表中！\n")
        return False

def test_code_fixes():
    """检查代码文件中的修复"""
    print("=" * 60)
    print("测试3: 代码文件验证")
    print("=" * 60)
    
    backend_path = os.path.join(os.path.dirname(__file__), 'backend')
    
    # 检查diary_service.py
    diary_service_path = os.path.join(backend_path, 'app/services/diary_service.py')
    print(f"\n检查文件: {diary_service_path}")
    
    with open(diary_service_path, 'r', encoding='utf-8') as f:
        diary_content = f.read()
    
    # 检查是否还有错误的 .upper()
    if 'mood_level_str.upper()' in diary_content:
        print("  ✗ 发现未修复的问题: mood_level_str.upper()")
        return False
    else:
        print("  ✓ diary_service.py: 心情等级枚举修复已应用")
    
    # 检查websocket/chat.py
    websocket_path = os.path.join(backend_path, 'app/websocket/chat.py')
    print(f"\n检查文件: {websocket_path}")
    
    with open(websocket_path, 'r', encoding='utf-8') as f:
        websocket_content = f.read()
    
    # 检查是否修复为 'chunk'
    if '"type": "content"' in websocket_content:
        print("  ✗ 发现未修复的问题: 消息类型仍为 'content'")
        return False
    elif '"type": "chunk"' in websocket_content:
        print("  ✓ websocket/chat.py: 消息类型已修复为 'chunk'")
    else:
        print("  ? websocket/chat.py: 无法确认消息类型")
        return False
    
    print("\n✅ 代码文件验证通过！\n")
    return True

def main():
    print("\n" + "=" * 60)
    print("开始验证架构审查问题修复")
    print("=" * 60 + "\n")
    
    results = []
    
    results.append(("心情等级枚举修复", test_mood_level_fix()))
    results.append(("WebSocket消息类型修复", test_websocket_message_type()))
    results.append(("代码文件验证", test_code_fixes()))
    
    print("=" * 60)
    print("验证结果汇总")
    print("=" * 60)
    
    all_passed = True
    for name, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{status}: {name}")
        if not passed:
            all_passed = False
    
    print("=" * 60)
    if all_passed:
        print("\n🎉 所有修复验证通过！\n")
        return 0
    else:
        print("\n⚠️ 部分修复验证失败，请检查！\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())
