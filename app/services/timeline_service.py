from datetime import datetime
from typing import Optional, List
from sqlalchemy.orm import Session
from app.db.models.memory import Memory
from app.db.models.enums import MemoryType
from uuid import UUID
from app.core.logger import setup_logger
from fastapi import HTTPException

# 配置日志
logger = setup_logger("timeline")

class TimelineService:
    def __init__(self, db: Session):
        self.db = db

    async def start_activity(
        self, 
        user_id: UUID, 
        content: str,
        target_duration: Optional[float] = None,
        tags: List[str] = [],
        allow_parallel: bool = False,
        parallel_group: Optional[str] = None,
        priority: int = 1
    ) -> Memory:
        """开始一个新活动"""
        # 只有当不允许并行时，才结束其他活动
        if not allow_parallel:
            ongoing_activities = self.db.query(Memory).filter(
                Memory.user_id == user_id,
                Memory.is_ongoing == True
            ).all()
            
            for activity in ongoing_activities:
                activity.is_ongoing = False
                activity.end_time = datetime.now()
                activity.duration = activity.calculate_duration
                activity.completion_rate = activity.calculate_completion_rate
                logger.info(f"结束已有活动: {activity.content}")
        
        # 创建新活动
        new_activity = Memory(
            user_id=user_id,
            content=content,
            memory_type=MemoryType.TIMELINE,
            tags=tags,
            start_time=datetime.now(),
            is_ongoing=True,
            target_duration=target_duration,
            allow_parallel=allow_parallel,
            parallel_group=parallel_group,
            priority=priority
        )
        
        self.db.add(new_activity)
        self.db.commit()
        self.db.refresh(new_activity)
        logger.info(f"开始新活动: {content}")
        return new_activity

    async def end_activity(
        self,
        user_id: UUID,
        content: Optional[str] = None
    ) -> Memory:
        """结束当前进行中的活动"""
        ongoing_activity = self.db.query(Memory).filter(
            Memory.user_id == user_id,
            Memory.is_ongoing == True
        ).first()
        
        if not ongoing_activity:
            logger.warning("未找到进行中的活动")
            return None
            
        ongoing_activity.is_ongoing = False
        ongoing_activity.end_time = datetime.now()
        ongoing_activity.duration = ongoing_activity.calculate_duration
        ongoing_activity.completion_rate = ongoing_activity.calculate_completion_rate
        
        if content:
            new_content = (
                f"{ongoing_activity.content}\n"
                f"---\n"
                f"完成时间：{ongoing_activity.end_time.strftime('%H:%M:%S')}\n"
                f"持续时间：{ongoing_activity.duration / 60:.1f}分钟\n"
                f"完成备注：{content}"
            )
            ongoing_activity.content = new_content
        
        try:
            self.db.commit()
            self.db.refresh(ongoing_activity)
            logger.info(f"活动已完成: {ongoing_activity.content}")
        except Exception as e:
            logger.error(f"更新失败: {str(e)}")
            self.db.rollback()
            raise
        
        return ongoing_activity

    async def get_daily_timeline(
        self,
        user_id: UUID,
        date: Optional[datetime] = None
    ) -> List[Memory]:
        """获取某天的完整时间轴"""
        if not date:
            date = datetime.now()
            
        return self.db.query(Memory).filter(
            Memory.user_id == user_id,
            Memory.memory_type == MemoryType.TIMELINE,
            Memory.start_time >= date.replace(hour=0, minute=0, second=0),
            Memory.start_time < date.replace(hour=23, minute=59, second=59)
        ).order_by(Memory.start_time).all()

    async def get_current_activities(
        self,
        user_id: UUID
    ) -> List[Memory]:
        """获取当前所有进行中的活动"""
        return self.db.query(Memory).filter(
            Memory.user_id == user_id,
            Memory.is_ongoing == True
        ).order_by(Memory.priority.desc()).all() 