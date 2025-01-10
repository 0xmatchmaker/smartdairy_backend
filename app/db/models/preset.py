from sqlalchemy import Column, String, Time, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from .base import Base

class PresetTimepoint(Base):
    """
    预设时间点模型：管理常用的时间点（如起床、三餐、就寝等）
    """
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False)
    name = Column(String, nullable=False, comment="时间点名称，如'起床'")
    default_time = Column(Time, nullable=False, comment="默认时间")
    is_active = Column(Boolean, default=True, comment="是否启用")
    icon = Column(String, nullable=True, comment="显示图标")
    
    # 关联关系
    user = relationship("User", back_populates="preset_timepoints") 