from datetime import date, datetime
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from app.db.models.memory import Memory
from app.db.models.enums import MemoryType, CoreFocusType
from uuid import UUID
from app.core.logger import setup_logger
from fastapi import HTTPException
from app.services.timeline_service import TimelineService
import sqlalchemy as sa

logger = setup_logger("core_focus")

class CoreFocusService:
    def __init__(self, db: Session):
        self.db = db

    async def create_important_matter(
        self,
        user_id: UUID,
        content: str,
        target_minutes: float,
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
            start_time=datetime.now(),
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
            record.duration or 0
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

    async def create_long_term_goal(
        self,
        user_id: UUID,
        content: str,
        target_date: date,
        target_value: float,
        progress_type: str,
        milestone_points: List[float] = None,
        tags: List[str] = None,
        description: str = None
    ) -> Memory:
        """创建长期目标"""
        # 使用 logger 而不是 print
        logger.info("=== Service Layer Debug ===")
        logger.info(f"Memory Type: {MemoryType.CORE_FOCUS}")
        logger.info(f"Focus Type: {CoreFocusType.LONG_TERM}")
        logger.info(f"Memory Type Value: {MemoryType.CORE_FOCUS.value}")
        logger.info(f"Focus Type Value: {CoreFocusType.LONG_TERM.value}")
        
        # 检查枚举类型
        logger.info("\n=== Enum Debug ===")
        logger.info(f"Memory Type Enum: {MemoryType.__members__}")
        logger.info(f"Core Focus Type Enum: {CoreFocusType.__members__}")
        
        memory = Memory(
            user_id=user_id,
            content=content,
            memory_type=MemoryType.CORE_FOCUS,  # 不使用 .value
            focus_type=CoreFocusType.LONG_TERM,  # 不使用 .value
            is_long_term=True,
            target_date=target_date,
            target_value=target_value,
            current_value=0,
            progress_type=progress_type,
            milestone_points=milestone_points,
            tags=tags or [],
            description=description
        )
        
        # 打印创建的对象
        logger.info("\n=== Memory Object Debug ===")
        logger.info(f"Memory Dict: {memory.__dict__}")
        
        self.db.add(memory)
        self.db.commit()
        return memory

    async def update_goal_progress(
        self,
        goal_id: UUID,
        current_value: float,
        note: str = None
    ) -> Tuple[Memory, float]:
        """更新目标进度"""
        goal = self.db.query(Memory).filter(
            Memory.id == goal_id,
            Memory.is_long_term == True
        ).first()
        
        if not goal:
            raise HTTPException(status_code=404, detail="Goal not found")
            
        goal.current_value = current_value
        completion_rate = (current_value / goal.target_value) * 100
        
        # 创建进度记录
        activity = Memory(
            user_id=goal.user_id,
            content=f"进度更新: {note}" if note else f"进度更新到 {current_value}",
            memory_type=MemoryType.TIMELINE,
            tags=goal.tags,
            start_time=datetime.now(),
            end_time=datetime.now()
        )
        
        self.db.add(activity)
        self.db.commit()
        return goal, completion_rate 

    async def get_long_term_goals(
        self,
        user_id: UUID,
        include_completed: bool = False  # 新增参数：是否包含已完成的目标
    ) -> List[Memory]:
        """获取用户的所有长期目标
        
        Args:
            user_id (UUID): 用户ID
            include_completed (bool, optional): 是否包含已完成的目标. Defaults to False.
        
        Returns:
            List[Memory]: 长期目标列表，按目标日期升序排序
        """
        logger.info(f"获取用户 {user_id} 的长期目标列表")
        
        # 构建基础查询
        query = self.db.query(Memory).filter(
            Memory.user_id == user_id,
            Memory.memory_type == MemoryType.CORE_FOCUS,
            Memory.focus_type == CoreFocusType.LONG_TERM,
            Memory.is_long_term == True
        )
        
        # 如果不包含已完成的目标，添加条件
        if not include_completed:
            query = query.filter(
                sa.or_(
                    Memory.current_value < Memory.target_value,  # 未达到目标值
                    Memory.current_value == None  # 或者还未开始
                )
            )
        
        # 按目标日期升序排序
        goals = query.order_by(Memory.target_date.asc()).all()
        
        logger.info(f"找到 {len(goals)} 个长期目标")
        return goals 

    async def get_long_term_goal(
        self,
        goal_id: UUID,
        user_id: UUID
    ) -> Memory:
        """获取单个长期目标详情
        
        Args:
            goal_id (UUID): 目标ID
            user_id (UUID): 用户ID
            
        Returns:
            Memory: 目标详情
            
        Raises:
            HTTPException: 如果目标不存在或不属于该用户
        """
        logger.info(f"获取目标 {goal_id} 的详情")
        
        goal = self.db.query(Memory).filter(
            Memory.id == goal_id,
            Memory.user_id == user_id,
            Memory.memory_type == MemoryType.CORE_FOCUS,
            Memory.focus_type == CoreFocusType.LONG_TERM,
            Memory.is_long_term == True
        ).first()
        
        if not goal:
            logger.warning(f"目标 {goal_id} 不存在或不属于用户 {user_id}")
            raise HTTPException(status_code=404, detail="Goal not found")
        
        logger.info(f"找到目标: {goal.content}")
        return goal 