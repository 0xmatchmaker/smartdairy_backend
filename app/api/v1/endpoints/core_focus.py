from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.api.deps import get_current_user
from app.services.core_focus_service import CoreFocusService
from app.api.v1.schemas.core_focus import ImportantMatterCreate, ImportantMatterResponse, ImportantMatterWithActivities, LongTermGoalCreate, GoalProgressUpdate, LongTermGoalResponse
from app.api.v1.schemas.timeline import TimelineResponse
from typing import List, Optional
from uuid import UUID
from datetime import date
import logging

router = APIRouter()

logger = logging.getLogger(__name__)

@router.post("/important", response_model=ImportantMatterResponse)
async def create_important_matter(
    matter: ImportantMatterCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """创建重要事项"""
    service = CoreFocusService(db)
    memory = await service.create_important_matter(
        user_id=current_user.id,
        content=matter.content,
        target_minutes=matter.target_minutes,
        tags=matter.tags,
        description=matter.description
    )
    return ImportantMatterResponse.from_memory(memory)

@router.get("/important/daily", response_model=List[ImportantMatterResponse])
async def get_daily_important_matters(
    date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取每日重要事项"""
    service = CoreFocusService(db)
    matters = await service.get_daily_important_matters(
        user_id=current_user.id,
        date=date
    )
    return [ImportantMatterResponse.from_memory(matter) for matter in matters]

@router.post("/important/{matter_id}/start", response_model=TimelineResponse)
async def start_important_matter_activity(
    matter_id: UUID,
    content: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """开始重要事项的一个活动"""
    service = CoreFocusService(db)
    activity = await service.start_important_matter_activity(
        matter_id=matter_id,
        user_id=current_user.id,
        content=content
    )
    return activity

@router.post("/important/{matter_id}/end", response_model=TimelineResponse)
async def end_important_matter_activity(
    matter_id: UUID,
    content: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """结束重要事项的活动"""
    service = CoreFocusService(db)
    activity, completion_rate = await service.end_important_matter_activity(
        matter_id=matter_id,
        user_id=current_user.id,
        content=content
    )
    return activity 

@router.get("/important/{matter_id}/activities", response_model=ImportantMatterWithActivities)
async def get_matter_activities(
    matter_id: UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取重要事项的所有相关活动"""
    service = CoreFocusService(db)
    matter, activities = await service.get_matter_activities(
        matter_id=matter_id,
        user_id=current_user.id
    )
    return ImportantMatterWithActivities.from_memory_and_activities(matter, activities)

@router.post("/long-term", response_model=LongTermGoalResponse)
async def create_long_term_goal(
    goal: LongTermGoalCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """创建长期目标"""
    logger.info("=== API Layer Debug ===")
    logger.info(f"Request Data: {goal.model_dump()}")
    
    service = CoreFocusService(db)
    try:
        memory = await service.create_long_term_goal(
            user_id=current_user.id,
            **goal.model_dump()
        )
        logger.info(f"Created Memory: {memory.__dict__}")
        return LongTermGoalResponse.from_memory(memory)
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise

@router.put("/long-term/{goal_id}/progress")
async def update_goal_progress(
    goal_id: UUID,
    progress: GoalProgressUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """更新目标进度"""
    service = CoreFocusService(db)
    return await service.update_goal_progress(
        goal_id=goal_id,
        **progress.model_dump()
    )

@router.get("/long-term", response_model=List[LongTermGoalResponse])
async def list_long_term_goals(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取所有长期目标列表"""
    service = CoreFocusService(db)
    memories = await service.get_long_term_goals(user_id=current_user.id)
    return [LongTermGoalResponse.from_memory(m) for m in memories]

@router.get("/long-term/{goal_id}", response_model=LongTermGoalResponse)
async def get_long_term_goal(
    goal_id: UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取单个长期目标详情"""
    service = CoreFocusService(db)
    memory = await service.get_long_term_goal(goal_id=goal_id, user_id=current_user.id)
    return LongTermGoalResponse.from_memory(memory)

@router.get("/long-term/{goal_id}/progress", response_model=List[TimelineResponse])
async def get_goal_progress_history(
    goal_id: UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取目标的进度历史"""
    service = CoreFocusService(db)
    activities = await service.get_goal_progress_history(goal_id=goal_id, user_id=current_user.id)
    return [TimelineResponse.from_orm(a) for a in activities] 