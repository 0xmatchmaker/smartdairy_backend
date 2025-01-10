from sqlalchemy import Column, Float, Date, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from .base import Base

class DreamProgress(Base):
    """
    梦想进度记录：详细记录每一个进展
    """
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dream_id = Column(UUID(as_uuid=True), ForeignKey("dream.id"), nullable=False)
    value = Column(Float, nullable=False, comment="进度值")
    date = Column(Date, nullable=False, comment="记录日期")
    note = Column(Text, nullable=True, comment="进度说明")
    
    # 关联关系
    dream = relationship("Dream", back_populates="progress_records") 