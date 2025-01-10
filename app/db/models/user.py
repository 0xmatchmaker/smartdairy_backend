from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.dialects.postgresql import UUID
import uuid
from .base import Base
from sqlalchemy.orm import relationship

class User(Base):
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean(), default=True)
    preset_timepoints = relationship("PresetTimepoint", back_populates="user")
    templates = relationship("Template", back_populates="user")
    dreams = relationship("Dream", back_populates="user") 