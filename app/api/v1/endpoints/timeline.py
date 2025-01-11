from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.db.session import get_db
from app.api.deps import get_current_user
from app.services.timeline_service import TimelineService
from app.api.v1.schemas.timeline import (
    TimelineCreate,
    TimelineUpdate,
    TimelineResponse,
    TimelineEndRequest
)

router = APIRouter()

@router.post("/start", response_model=TimelineResponse)
async def start_activity(
    activity: TimelineCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """开始一个新活动"""
    timeline_service = TimelineService(db)
    return await timeline_service.start_activity(
        user_id=current_user.id,
        content=activity.content,
        target_duration=activity.target_duration,
        tags=activity.tags,
        allow_parallel=activity.allow_parallel,
        parallel_group=activity.parallel_group,
        priority=activity.priority
    )

@router.post("/end", response_model=TimelineResponse)
async def end_activity(
    request: TimelineEndRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """结束当前活动"""
    timeline_service = TimelineService(db)
    activity = await timeline_service.end_activity(
        user_id=current_user.id,
        content=request.content
    )
    if not activity:
        raise HTTPException(status_code=404, detail="No ongoing activity found")
    return activity

@router.get("/daily", response_model=List[TimelineResponse])
async def get_daily_timeline(
    date: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取日时间轴"""
    timeline_service = TimelineService(db)
    return await timeline_service.get_daily_timeline(
        user_id=current_user.id,
        date=datetime.strptime(date, "%Y-%m-%d") if date else None
    ) 