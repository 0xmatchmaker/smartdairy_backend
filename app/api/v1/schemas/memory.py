from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel
from uuid import UUID
from app.db.models.memory import MemoryType, CoreFocusType

class MemoryBase(BaseModel):
    """记忆基础模型"""
    content: str
    memory_type: MemoryType
    tags: List[str] = []

class MemoryCreate(MemoryBase):
    """创建记忆请求模型"""
    focus_type: Optional[CoreFocusType] = None
    timeline_time: Optional[str] = None  # 格式: "HH:MM"

class MemoryUpdate(BaseModel):
    """更新记忆请求模型"""
    content: Optional[str] = None
    tags: Optional[List[str]] = None

class MemoryInDB(MemoryBase):
    """数据库记忆模型"""
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True 