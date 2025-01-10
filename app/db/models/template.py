from sqlalchemy import Column, String, JSON
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
import uuid
from .base import Base

class Template(Base):
    """
    快速记录模板：支持用户自定义常用记录模板
    """
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False)
    name = Column(String, nullable=False, comment="模板名称")
    structure = Column(JSON, nullable=False, comment="模板结构")
    tags = Column(ARRAY(String), default=[], comment="默认标签")
    shortcut = Column(String, nullable=True, comment="快捷键或短语")
    
    # 关联关系
    user = relationship("User", back_populates="templates")
    memories = relationship("Memory", back_populates="template") 