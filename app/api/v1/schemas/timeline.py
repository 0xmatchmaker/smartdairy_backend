from pydantic import BaseModel, computed_field
from typing import List, Optional
from datetime import datetime
from uuid import UUID

class TimelineCreate(BaseModel):
    content: str
    target_duration: Optional[float] = None
    tags: List[str] = []
    allow_parallel: bool = False
    parallel_group: Optional[str] = None
    priority: Optional[int] = 1

class TimelineUpdate(BaseModel):
    content: Optional[str] = None
    tags: Optional[List[str]] = None

class TimelineResponse(BaseModel):
    id: UUID
    content: str
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    duration: Optional[float]
    is_ongoing: bool
    target_duration: Optional[float]
    completion_rate: Optional[float]
    tags: List[str]
    allow_parallel: bool
    parallel_group: Optional[str]
    priority: int

    @computed_field
    @property
    def formatted_start_time(self) -> Optional[str]:
        """格式化开始时间"""
        return self.start_time.strftime("%H:%M:%S") if self.start_time else None

    @computed_field
    @property
    def formatted_end_time(self) -> Optional[str]:
        """格式化结束时间"""
        return self.end_time.strftime("%H:%M:%S") if self.end_time else None

    @computed_field
    @property
    def formatted_duration(self) -> Optional[str]:
        """格式化持续时间"""
        if self.duration is None:
            return None
        minutes = int(self.duration)
        seconds = int((self.duration - minutes) * 60)
        return f"{minutes}分{seconds}秒"

    class Config:
        from_attributes = True 

class TimelineEndRequest(BaseModel):
    content: Optional[str] = None 