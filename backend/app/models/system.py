from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func

from app.core.database import Base


class SystemConfig(Base):
    __tablename__ = "system_configs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    config_key = Column(String(100), unique=True, nullable=False, index=True, comment="配置键名")
    config_value = Column(Text, nullable=True, comment="配置值")
    description = Column(String(500), nullable=True, comment="配置描述")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    def __repr__(self):
        return f"<SystemConfig(key={self.config_key}, value={self.config_value[:20] if self.config_value else None}...)>"
