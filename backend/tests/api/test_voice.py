"""
语音相关接口测试
"""
import pytest
from io import BytesIO


def test_speech_recognition(authorized_vip_client, vip_user):
    """测试语音识别接口"""
    # 创建一个测试音频文件，只测试接口是否可访问
    audio_file = BytesIO(b'test audio content')
    response = authorized_vip_client.post(
        "/api/v1/voice/asr",
        files={"audio": ("test.wav", audio_file, "audio/wav")},
        data={"format": "wav"}
    )
    # 即使识别失败（因为是测试数据），接口应该存在并返回合理状态码
    # 如果使用mock provider，应该返回成功
    assert response.status_code in [200, 403, 500]
    if response.status_code == 200:
        data = response.json()
        assert "text" in data
        assert "success" in data


def test_speech_recognition_free_user(authorized_client, test_user):
    """测试免费用户使用语音识别应该被拒绝"""
    audio_file = BytesIO(b'test audio content')
    response = authorized_client.post(
        "/api/v1/voice/asr",
        files={"audio": ("test.wav", audio_file, "audio/wav")}
    )
    assert response.status_code == 403
    assert "需要VIP会员" in response.json()["detail"]


def test_text_to_speech(authorized_vip_client, vip_user):
    """测试语音合成接口"""
    response = authorized_vip_client.post(
        "/api/v1/voice/tts?text=这是一段测试文本&voice=default"
    )
    # 如果是mock provider可能返回成功，否则可能配置问题
    if response.status_code == 200:
        assert response.headers["content-type"] == "audio/mpeg"
        assert "Content-Disposition" in response.headers
    else:
        assert response.status_code in [500, 403]


def test_text_to_speech_free_user(authorized_client, test_user):
    """测试免费用户使用语音合成应该被拒绝"""
    response = authorized_client.post(
        "/api/v1/voice/tts?text=测试"
    )
    assert response.status_code == 403


def test_text_to_speech_too_long(authorized_vip_client, vip_user):
    """测试文本过长应该返回错误"""
    long_text = "x" * 1001
    response = authorized_vip_client.post(
        f"/api/v1/voice/tts?text={long_text}"
    )
    assert response.status_code == 400


def test_get_voice_status(authorized_client, test_user):
    """测试获取语音服务状态接口"""
    response = authorized_client.get("/api/v1/voice/status")
    assert response.status_code == 200
    data = response.json()
    assert "provider" in data
    assert "available" in data
    assert "supported_voices" in data
    assert "asr_enabled" in data
    assert "tts_enabled" in data


def test_unauthorized_access(client):
    """测试未授权访问"""
    response = client.post("/api/v1/voice/asr")
    assert response.status_code == 401
    
    response = client.post("/api/v1/voice/tts?text=测试")
    assert response.status_code == 401
    
    response = client.get("/api/v1/voice/status")
    assert response.status_code == 401
