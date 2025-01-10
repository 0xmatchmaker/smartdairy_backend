from sqlalchemy import Column, String, Time, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
# 暂时注释掉关系导入
# from sqlalchemy.orm import relationship
import uuid
from .base import Base

class PresetTimepoint(Base):
    """预设时间点模型"""
    __tablename__ = "preset_timepoints"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False, comment="时间点名称，如'起床'")
    default_time = Column(Time, nullable=False, comment="默认时间")
    is_active = Column(Boolean, default=True, comment="是否启用")
    icon = Column(String, nullable=True, comment="显示图标")
    
    # 关联关系 - 暂时注释掉
    # user = relationship("User", back_populates="preset_timepoints") 