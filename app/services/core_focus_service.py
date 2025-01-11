from datetime import date, datetime
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from app.db.models.memory import Memory
from app.db.models.enums import MemoryType, CoreFocusType
from uuid import UUID
from app.core.logger import setup_logger
from fastapi import HTTPException
from app.services.timeline_service import TimelineService

logger = setup_logger("core_focus")

class CoreFocusService:
    def __init__(self, db: Session):
        self.db = db

    async def create_important_matter(
        self,
        user_id: UUID,
        content: str,
        target_minutes: float,
        date: date,
        tags: List[str] = [],
        description: Optional[str] = None
    ) -> Memory:
        """创建重要事项"""
        # 如果有描述，将其添加到内容中
        full_content = (
            f"{content}\n---\n{description}" 
            if description 
            else content
        )
        
        matter = Memory(
            user_id=user_id,
            content=full_content,  # 使用组合后的内容
            memory_type=MemoryType.CORE_FOCUS,
            focus_type=CoreFocusType.IMPORTANT,
            target_duration=target_minutes * 60,
            tags=tags,
            start_time=datetime.combine(date, datetime.min.time()),
            is_ongoing=True
        )
        
        self.db.add(matter)
        self.db.commit()
        self.db.refresh(matter)
        logger.info(f"创建重要事项: {content}, 目标时间: {target_minutes}分钟 ({target_minutes * 60}秒)")
        return matter

    async def get_daily_important_matters(
        self,
        user_id: UUID,
        date: Optional[date] = None
    ) -> List[Memory]:
        """获取某天的重要事项列表"""
        if not date:
            date = datetime.now().date()

        logger.info(f"查询日期: {date}")
        
        matters = self.db.query(Memory).filter(
            Memory.user_id == user_id,
            Memory.memory_type == MemoryType.CORE_FOCUS,
            Memory.focus_type == CoreFocusType.IMPORTANT,
            Memory.start_time >= datetime.combine(date, datetime.min.time()),
            Memory.start_time < datetime.combine(date, datetime.max.time())
        ).all()
        
        logger.info(f"找到 {len(matters)} 个重要事项")
        return matters

    async def calculate_time_investment(
        self,
        matter_id: UUID
    ) -> float:
        """计算某个重要事项的实际投入时间（从时间轴记录中）"""
        matter = self.db.query(Memory).filter(
            Memory.id == matter_id
        ).first()
        
        if not matter:
            return 0
            
        # 获取相关的时间轴记录
        timeline_records = self.db.query(Memory).filter(
            Memory.user_id == matter.user_id,
            Memory.memory_type == MemoryType.TIMELINE,
            Memory.tags.overlap(matter.tags),
            Memory.start_time >= datetime.combine(matter.start_time.date(), datetime.min.time()),
            Memory.start_time < datetime.combine(matter.start_time.date(), datetime.max.time())
        ).all()
        
        total_seconds = sum(
            (record.duration or 0) * 60
            for record in timeline_records
        )
        
        return total_seconds  # 返回秒数 

    async def start_important_matter_activity(
        self,
        matter_id: UUID,
        user_id: UUID,
        content: Optional[str] = None
    ) -> Memory:
        """开始重要事项的一个活动"""
        # 获取重要事项
        matter = self.db.query(Memory).filter(
            Memory.id == matter_id,
            Memory.user_id == user_id,
            Memory.memory_type == MemoryType.CORE_FOCUS,
            Memory.focus_type == CoreFocusType.IMPORTANT
        ).first()
        
        if not matter:
            raise HTTPException(status_code=404, detail="Important matter not found")
        
        # 创建时间轴记录
        timeline_service = TimelineService(self.db)
        activity = await timeline_service.start_activity(
            user_id=user_id,
            content=content or f"开始: {matter.content.split('---')[0]}",
            tags=matter.tags,  # 继承重要事项的标签
            target_duration=60  # 默认一小时，可以根据需要调整
        )
        
        logger.info(f"开始重要事项活动: {activity.content}, 关联事项: {matter.content}")
        return activity

    async def end_important_matter_activity(
        self,
        matter_id: UUID,
        user_id: UUID,
        content: Optional[str] = None
    ) -> Tuple[Memory, float]:
        """结束重要事项的活动并更新完成度"""
        # 获取重要事项
        matter = self.db.query(Memory).filter(
            Memory.id == matter_id,
            Memory.user_id == user_id,
            Memory.memory_type == MemoryType.CORE_FOCUS,
            Memory.focus_type == CoreFocusType.IMPORTANT
        ).first()
        
        if not matter:
            raise HTTPException(status_code=404, detail="Important matter not found")
        
        # 结束时间轴活动
        timeline_service = TimelineService(self.db)
        activity = await timeline_service.end_activity(
            user_id=user_id,
            content=content
        )
        
        # 计算总投入时间
        total_seconds = await self.calculate_time_investment(matter_id)
        completion_rate = (total_seconds / (matter.target_duration or 1)) * 100
        
        logger.info(f"结束重要事项活动: {activity.content}, 总投入: {total_seconds/60:.1f}分钟, 完成度: {completion_rate:.1f}%")
        return activity, completion_rate 

    async def get_matter_activities(
        self,
        matter_id: UUID,
        user_id: UUID
    ) -> Tuple[Memory, List[Memory]]:
        """获取重要事项及其所有相关活动"""
        # 获取重要事项
        matter = self.db.query(Memory).filter(
            Memory.id == matter_id,
            Memory.user_id == user_id,
            Memory.memory_type == MemoryType.CORE_FOCUS,
            Memory.focus_type == CoreFocusType.IMPORTANT
        ).first()
        
        if not matter:
            raise HTTPException(status_code=404, detail="Important matter not found")
        
        # 获取相关的时间轴记录
        activities = self.db.query(Memory).filter(
            Memory.user_id == user_id,
            Memory.memory_type == MemoryType.TIMELINE,
            Memory.tags.overlap(matter.tags),
            Memory.start_time >= datetime.combine(matter.start_time.date(), datetime.min.time()),
            Memory.start_time < datetime.combine(matter.start_time.date(), datetime.max.time())
        ).order_by(Memory.start_time.desc()).all()
        
        logger.info(f"找到重要事项 '{matter.content}' 的 {len(activities)} 个相关活动")
        return matter, activities 