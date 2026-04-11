"""
stream_service 单元测试 - SSE流式对话服务
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock

import json
from app.services.stream_service import StreamChatService, get_stream_service


class TestStreamChatService:
    """StreamChatService流式输出服务单元测试"""

    def test_init(self):
        """测试初始化"""
        service = StreamChatService()
        assert service is not None
        assert hasattr(service, 'stream_generate')

    def test_singleton_instance(self):
        """测试单例实例"""
        service1 = get_stream_service()
        service2 = get_stream_service()
        assert service1 is service2

    async def test_stream_generate_normal_case(self):
        """测试正常流式生成"""
        service = StreamChatService()
        
        mock_retriever = Mock()
        mock_retriever.retrieve_with_expand = AsyncMock(return_value=[])
        
        mock_generator = Mock()
        mock_generator._build_system_prompt = Mock(return_value="system prompt")
        mock_generator._build_user_prompt = Mock(return_value="user prompt")
        
        # 模拟流式token输出
        mock_stream_output = ["这", "是", "流", "式", "测", "试"]
        
        with patch("app.services.stream_service.get_retriever", return_value=mock_retriever), \
             patch("app.services.stream_service.get_generator", return_value=mock_generator):
        
            # 在with内部定义mock generator来模拟chat_stream
            async def mock_stream(messages, **kwargs):
                for token in mock_stream_output:
                    yield token
            
            with patch("app.services.stream_service.chat_stream", mock_stream):
                chunks = []
                async for chunk in service.stream_generate("测试问题", "INTJ", "", None):
                    chunks.append(chunk)
                
                assert len(chunks) == 7  # 6个内容块 + 1个done块
                # 解析每个chunk
                content_chunks = []
                for chunk in chunks[:-1]:
                    # chunk格式是 "data: {json}\n\n"
                    assert chunk.startswith("data: ")
                    assert chunk.endswith("\n\n")
                    json_part = chunk[5:-2]
                    data = json.loads(json_part)
                    assert data["type"] == "content"
                    content_chunks.append(data["content"])
                
                full_text = "".join(content_chunks)
                assert full_text == "这是流式测试"
                
                # 最后一个块是done
                last_chunk = chunks[-1]
                json_part = last_chunk[5:-2]
                data = json.loads(json_part)
                assert data["type"] == "done"

    async def test_stream_generate_retrieval_error(self):
        """测试检索失败仍然继续生成"""
        service = StreamChatService()
        
        mock_retriever = Mock()
        mock_retriever.retrieve_with_expand = AsyncMock(side_effect=Exception("检索失败"))
        
        mock_generator = Mock()
        mock_generator._build_system_prompt = Mock(return_value="system prompt")
        mock_generator._build_user_prompt = Mock(return_value="user prompt")
        
        mock_stream_output = ["回", "复"]
        
        with patch("app.services.stream_service.get_retriever", return_value=mock_retriever), \
             patch("app.services.stream_service.get_generator", return_value=mock_generator):
        
            async def mock_stream(messages, **kwargs):
                for token in mock_stream_output:
                    yield token
            
            with patch("app.services.stream_service.chat_stream", mock_stream):
                chunks = []
                async for chunk in service.stream_generate("问题", None, None, None):
                    chunks.append(chunk)
                
                # 即使检索失败，仍然能输出
                assert len(chunks) == 3  # 2 + done
                assert chunks[-1].endswith('"type": "done"}\n\n')

    async def test_stream_generate_llm_exception(self):
        """测试LLM异常时返回fallback"""
        service = StreamChatService()
        
        mock_retriever = Mock()
        mock_retriever.retrieve_with_expand = AsyncMock(return_value=[])
        
        mock_generator = Mock()
        mock_generator._build_system_prompt = Mock(return_value="system prompt")
        mock_generator._build_user_prompt = Mock(return_value="user prompt")
        
        with patch("app.services.stream_service.get_retriever", return_value=mock_retriever), \
             patch("app.services.stream_service.get_generator", return_value=mock_generator):
        
            async def mock_stream_error(messages, **kwargs):
                raise Exception("LLM error")
            
            with patch("app.services.stream_service.chat_stream", mock_stream_error), \
                 patch("asyncio.sleep", AsyncMock()):
                chunks = []
                async for chunk in service.stream_generate("问题", None, None, None):
                    chunks.append(chunk)
                
                # 应该返回fallback文本
                content_chunks = []
                for chunk in chunks[:-1]:
                    json_part = chunk[5:-2]
                    data = json.loads(json_part)
                    content_chunks.append(data["content"])
                
                full_text = "".join(content_chunks)
                assert "抱歉" in full_text
                assert "遇到了一些问题" in full_text
                assert chunks[-1] is not None
                # 最后依然是done
                data = json.loads(chunks[-1][5:-2])
                assert data["type"] == "done"
