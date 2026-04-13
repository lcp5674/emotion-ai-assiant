"""
应用配置管理
"""
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """应用配置"""

    # 应用配置
    APP_NAME: str = "心灵伴侣AI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # 数据库配置
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = "emotion_ai"
    MYSQL_PASSWORD: str = ""
    MYSQL_DATABASE: str = "emotion_ai"

    # 支持直接指定数据库URL (SQLite: sqlite:///./emotion_ai.db)
    DATABASE_URL_: Optional[str] = Field(None, alias="DATABASE_URL")

    # Redis配置
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: Optional[str] = None
    REDIS_DB: int = 0

    # JWT配置
    SECRET_KEY: str = ""  # REQUIRED - Must be at least 32 characters in production
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7天
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 30  # 30天

    # 大模型配置
    LLM_PROVIDER: str = ""  # 必须配置，如: openai/anthropic/glm/qwen/minimax/ernie/hunyuan/spark/doubao/siliconflow
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    OPENAI_MODEL: str = "gpt-3.5-turbo"

    ANTHROPIC_API_KEY: Optional[str] = None
    ANTHROPIC_MODEL: str = "claude-3-haiku-20240307"
    ANTHROPIC_BASE_URL: Optional[str] = None

    GLM_API_KEY: Optional[str] = None
    GLM_MODEL: str = "glm-4"
    GLM_BASE_URL: Optional[str] = None

    QWEN_API_KEY: Optional[str] = None
    QWEN_MODEL: str = "qwen-turbo"
    QWEN_BASE_URL: Optional[str] = None

    MINIMAX_API_KEY: Optional[str] = None
    MINIMAX_MODEL: str = "abab5.5-chat"
    MINIMAX_BASE_URL: Optional[str] = None

    ERNIE_API_KEY: Optional[str] = None
    ERNIE_MODEL: str = "ernie-4.0-8k"
    ERNIE_BASE_URL: Optional[str] = None

    HUNYUAN_API_KEY: Optional[str] = None
    HUNYUAN_MODEL: str = "hunyuan-pro"
    HUNYUAN_BASE_URL: Optional[str] = None

    SPARK_API_KEY: Optional[str] = None
    SPARK_MODEL: str = "spark-v3.5"
    SPARK_BASE_URL: Optional[str] = None

    DOUBAO_API_KEY: Optional[str] = None
    DOUBAO_MODEL: str = "doubao-pro-32k"
    DOUBAO_BASE_URL: Optional[str] = None

    SILICONFLOW_API_KEY: Optional[str] = None
    SILICONFLOW_MODEL: str = "Qwen/Qwen2-72B-Instruct"
    SILICONFLOW_BASE_URL: Optional[str] = None

    # 向量数据库配置
    VECTOR_DB_TYPE: str = "milvus"  # milvus/qdrant/faiss
    MILVUS_HOST: str = "localhost"
    MILVUS_PORT: int = 19530
    MILVUS_COLLECTION: str = "emotion_knowledge"

    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    QDRANT_COLLECTION: str = "emotion_knowledge"

    # Embedding配置
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_DIM: int = 384

    # SMS配置 (支持 mock/alibaba)
    SMS_PROVIDER: str = "mock"
    ALIBABA_ACCESS_KEY_ID: Optional[str] = None
    ALIBABA_ACCESS_KEY_SECRET: Optional[str] = None
    ALIBABA_SMS_SIGN_NAME: str = "心灵伴侣AI"
    ALIBABA_SMS_TEMPLATE_CODE: str = "SMS_xxxxx"

    # 内容安全配置 (支持 keyword/alibaba/mock)
    CONTENT_FILTER_PROVIDER: str = "keyword"
    ALIBABA_CONTENT_ACCESS_KEY: Optional[str] = None
    ALIBABA_CONTENT_ACCESS_SECRET: Optional[str] = None

    # HTML安全配置
    HTML_SANITIZER_ALLOWED_TAGS: list = ["p", "h1", "h2", "h3", "h4", "h5", "h6", "strong", "em", "b", "i", "ul", "ol", "li", "a", "img", "blockquote", "code", "pre", "br", "span", "div"]
    HTML_SANITIZER_ALLOWED_ATTRIBUTES: dict = {"a": ["href", "title"], "img": ["src", "alt", "title"], "*": ["class"]}

    # 微信支付配置
    WECHAT_PAY_ENABLED: bool = False
    WECHAT_MCHID: str = ""
    WECHAT_SERIAL_NO: str = ""
    WECHAT_PRIVATE_KEY_PATH: str = ""
    WECHAT_APIV3_KEY: str = ""
    WECHAT_APPID: str = ""
    WECHAT_NOTIFY_URL: str = ""

    # Stripe支付配置
    STRIPE_API_KEY: Optional[str] = None
    STRIPE_WEBHOOK_SECRET: Optional[str] = None

    # 支付宝支付配置
    ALIPAY_ENABLED: bool = False
    ALIPAY_APPID: str = ""
    ALIPAY_PRIVATE_KEY_PATH: str = ""
    ALIPAY_PUBLIC_KEY_PATH: str = ""
    ALIPAY_GATEWAY: str = "https://openapi.alipay.com/gateway.do"
    ALIPAY_NOTIFY_URL: str = ""
    ALIPAY_RETURN_URL: str = ""

    # 语音服务配置
    VOICE_PROVIDER: str = "mock"  # mock/alibaba/baidu/openai/tencent
    
    # 阿里云语音
    ALIBABA_VOICE_APP_KEY: str = ""
    
    # 百度语音
    BAIDU_VOICE_API_KEY: Optional[str] = None
    BAIDU_VOICE_SECRET_KEY: Optional[str] = None
    
    # 腾讯云语音
    TENCENT_VOICE_SECRET_ID: Optional[str] = None
    TENCENT_VOICE_SECRET_KEY: Optional[str] = None

    # API基础URL (用于支付回调)
    API_BASE_URL: str = "http://localhost:3000"

    # 会员权益配置
    FREE_DAILY_MESSAGES: int = 3  # 免费用户每日消息数

    # CORS配置
    CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:5173"]

    @property
    def database_url(self) -> str:
        """数据库连接URL"""
        # 如果显式指定了 DATABASE_URL_，直接使用
        if self.DATABASE_URL_:
            return self.DATABASE_URL_
        # 否则使用MySQL配置
        return (
            f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}"
            f"@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"
            f"?charset=utf8mb4"
        )

    @property
    def REDIS_URL(self) -> str:
        """Redis连接URL"""
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        populate_by_name = True


def _validate_security_config() -> None:
    """验证安全配置，启动时必须检查"""
    if not settings.SECRET_KEY:
        raise ValueError(
            "SECRET_KEY is not set. "
            "Please set SECRET_KEY environment variable (at least 32 characters)."
        )
    if len(settings.SECRET_KEY) < 32:
        import warnings
        warnings.warn(
            f"SECRET_KEY is too short ({len(settings.SECRET_KEY)} chars). "
            "For production, use at least 32 characters."
        )


_settings = Settings()
settings = _settings
_validate_security_config()