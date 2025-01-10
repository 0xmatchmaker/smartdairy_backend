from sqlalchemy import Column, String, Text, Float, Date, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
# 暂时注释掉关系导入
# from sqlalchemy.orm import relationship
import uuid
from .base import Base

class Dream(Base):
    """梦想追踪模型"""
    __tablename__ = "dreams"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False, comment="梦想标题")
    description = Column(Text, nullable=True, comment="详细描述")
    target_date = Column(Date, nullable=True, comment="目标日期")
    target_value = Column(Float, nullable=True, comment="目标值")
    current_value = Column(Float, default=0, comment="当前进度")
    
    # 关联关系 - 暂时注释掉
    # user = relationship("User", back_populates="dreams")
    # memories = relationship("Memory", back_populates="dream") 