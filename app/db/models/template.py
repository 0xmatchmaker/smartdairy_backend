from sqlalchemy import Column, String, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
# 暂时注释掉关系导入
# from sqlalchemy.orm import relationship
import uuid
from .base import Base

class Template(Base):
    """记忆模板：用于快速记录常见场景"""
    __tablename__ = "templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False, comment="模板名称")
    fields = Column(JSON, nullable=False, comment="字段定义")
    
    # 关联关系 - 暂时注释掉
    # user = relationship("User", back_populates="templates")
    # memories = relationship("Memory", back_populates="template") 