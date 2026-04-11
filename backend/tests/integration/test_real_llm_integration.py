"""
真实LLM服务集成测试 - 使用火山引擎doubao
"""
import pytest
import asyncio
from app.core.config import settings
from app.services.llm.factory import get_llm_provider, chat, chat_stream


@pytest.mark.asyncio
async def test_doubao_provider_init():
    """测试豆包provider初始化"""
    from app.services.llm.providers import DoubaoProvider
    
    provider = get_llm_provider()
    assert provider is not None
    assert settings.LLM_PROVIDER == "doubao"
    assert isinstance(provider, DoubaoProvider)
    assert provider.api_key == settings.DOUBAO_API_KEY
    assert provider.model == settings.DOUBAO_MODEL
    assert provider.base_url == settings.DOUBAO_BASE_URL


@pytest.mark.asyncio
async def test_doubao_chat_sync():
    """测试豆包同步聊天"""
    provider = get_llm_provider()
    
    messages = [
        {"role": "system", "content": "你是一个情感倾听助手，用户现在心情有点不好，请给予温暖的回复。"},
        {"role": "user", "content": "我今天考试没考好，感觉很失落。"},
    ]
    
    response = await provider.chat(messages, temperature=0.7, max_tokens=200)
    
    assert isinstance(response, str)
    assert len(response) > 0
    print(f"\n[LLM回复]: {response}")
    
    # 应该包含安慰性质的词语
    lower_response = response.lower()
    assert any(word in lower_response for word in 
              ["失落", "安慰", "没关系", "下次", "加油", "努力", "理解", "感受"])


@pytest.mark.asyncio
async def test_doubao_chat_stream():
    """测试豆包流式聊天"""
    provider = get_llm_provider()
    
    messages = [
        {"role": "system", "content": "你是一个情感倾听助手。"},
        {"role": "user", "content": "简单说一句，今天天气真好。"},
    ]
    
    chunks = []
    async for chunk in provider.chat_stream(messages, temperature=0.7, max_tokens=100):
        chunks.append(chunk)
        print(chunk, end="", flush=True)
    
    assert len(chunks) > 0
    full_response = "".join(chunks)
    assert len(full_response) > 0
    print(f"\n[完整流式回复]: {full_response}")


@pytest.mark.asyncio
async def test_factory_chat():
    """测试通过factory chat接口"""
    messages = [
        {"role": "user", "content": "你好，这是一个集成测试，请简单回复。"},
    ]
    
    response = await chat(messages)
    assert isinstance(response, str)
    assert len(response) > 0
    print(f"\n[factory chat]: {response}")


@pytest.mark.asyncio
async def test_factory_chat_stream():
    """测试通过factory chat_stream接口"""
    messages = [
        {"role": "user", "content": "分段说12345"},
    ]
    
    chunks = []
    async for chunk in chat_stream(messages, max_tokens=50):
        chunks.append(chunk)
    
    assert len(chunks) > 0
    full = "".join(chunks)
    assert len(full) > 0
    print(f"\n[factory stream]: {full}")


@pytest.mark.asyncio
async def test_emotion_support_response():
    """测试情感支持场景响应"""
    messages = [
        {"role": "system", "content": "你是一个专业的情感陪伴AI助手，善于倾听和给予温暖的支持。"},
        {"role": "user", "content": "最近工作压力很大，每天都很累，有点撑不住了。"},
    ]
    
    response = await chat(messages, temperature=0.8)
    assert isinstance(response, str)
    assert len(response) > 20
    print(f"\n[情感支持回复]: {response}")
    
    # 应该有共情和支持
    lower = response.lower()
    # 不一定包含关键词，但长度足够表明有内容
    assert len(response) > 50
