from sqlalchemy import Column, String, Boolean
from sqlalchemy.dialects.postgresql import UUID
# 暂时注释掉，等基础功能完成后再启用
# from sqlalchemy.orm import relationship
import uuid
from .base import Base

class User(Base):
    """用户模型"""
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean(), default=True)

    # 关联关系 - 暂时注释掉，等基础认证功能完成后再启用
    # memories = relationship("Memory", back_populates="user", lazy="dynamic")
    # preset_timepoints = relationship("PresetTimepoint", back_populates="user", lazy="dynamic")
    # templates = relationship("Template", back_populates="user", lazy="dynamic")
    # dreams = relationship("Dream", back_populates="user", lazy="dynamic") 