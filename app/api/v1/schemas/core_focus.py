from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import date
from uuid import UUID
import re
from app.api.v1.schemas.timeline import TimelineResponse
from app.db.models.memory import Memory

class ImportantMatterCreate(BaseModel):
    """创建重要事项"""
    content: str
    target_minutes: float
    # 移除 date 字段，改用系统时间
    tags: List[str] = []
    description: Optional[str] = None

    model_config = ConfigDict(
        json_schema_extra = {
            "example": {
                "content": "编程学习",
                "target_minutes": 240,
                "tags": ["学习", "编程"],
                "description": "完成FastAPI项目的核心功能"
            }
        }
    )

class ImportantMatterResponse(BaseModel):
    id: UUID
    content: str
    target_minutes: float
    actual_minutes: float = 0
    completion_rate: float = 0
    date: date
    tags: List[str]
    description: Optional[str] = None
    related_activities: List[UUID] = []

    @property
    def formatted_target_time(self) -> str:
        """格式化目标时间"""
        hours = int(self.target_minutes / 60)
        minutes = int(self.target_minutes % 60)
        return f"{hours}小时{minutes}分钟" if hours > 0 else f"{minutes}分钟"

    @property
    def formatted_actual_time(self) -> str:
        """格式化实际时间"""
        hours = int(self.actual_minutes / 60)
        minutes = int(self.actual_minutes % 60)
        return f"{hours}小时{minutes}分钟" if hours > 0 else f"{minutes}分钟"

    @classmethod
    def from_memory(cls, memory: "Memory") -> "ImportantMatterResponse":
        """从 Memory 模型创建响应"""
        # 从内容中提取描述
        content_parts = memory.content.split("\n---\n", 1)
        main_content = content_parts[0]
        description = content_parts[1] if len(content_parts) > 1 else None

        return cls(
            id=memory.id,
            content=main_content,
            target_minutes=memory.target_duration / 60 if memory.target_duration else 0,  # 秒转分钟显示
            actual_minutes=memory.duration / 60 if memory.duration else 0,  # 秒转分钟显示
            completion_rate=memory.completion_rate if memory.completion_rate else 0,
            date=memory.start_time.date(),
            tags=memory.tags,
            description=description,
            related_activities=[]  # 暂时为空
        )

    model_config = ConfigDict(from_attributes=True) 

class ImportantMatterWithActivities(BaseModel):
    """带有活动列表的重要事项"""
    matter: ImportantMatterResponse
    activities: List[TimelineResponse]
    total_minutes: float = 0
    completion_rate: float = 0

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_memory_and_activities(
        cls,
        matter: Memory,
        activities: List[Memory]
    ) -> "ImportantMatterWithActivities":
        total_seconds = sum(  # 改名更清晰
            activity.duration or 0  # 这里是秒
            for activity in activities
        )
        
        return cls(
            matter=ImportantMatterResponse.from_memory(matter),
            activities=[TimelineResponse.from_orm(activity) for activity in activities],
            total_minutes=total_seconds / 60,  # 秒转分钟显示
            completion_rate=(total_seconds / (matter.target_duration or 1)) * 100  # 直接用秒计算
        )