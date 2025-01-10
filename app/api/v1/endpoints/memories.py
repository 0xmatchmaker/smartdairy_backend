from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_current_user
from app.db.session import get_db
from app.db.models.user import User
from app.db.models.memory import Memory
from app.api.v1.schemas.memory import MemoryCreate, MemoryUpdate, MemoryInDB

router = APIRouter()

@router.post("/", response_model=MemoryInDB)
async def create_memory(
    memory_in: MemoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建新记忆"""
    memory = Memory(
        user_id=current_user.id,
        content=memory_in.content,
        memory_type=memory_in.memory_type,
        tags=memory_in.tags
    )
    
    if memory_in.focus_type:
        memory.focus_type = memory_in.focus_type
    
    if memory_in.timeline_time:
        try:
            hour, minute = memory_in.timeline_time.split(":")
            memory.timeline_time = f"{int(hour):02d}:{int(minute):02d}"
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid time format. Use HH:MM"
            )
    
    db.add(memory)
    db.commit()
    db.refresh(memory)
    return memory

@router.get("/", response_model=List[MemoryInDB])
async def read_memories(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取用户的记忆列表"""
    memories = db.query(Memory)\
        .filter(Memory.user_id == current_user.id)\
        .offset(skip)\
        .limit(limit)\
        .all()
    return memories

@router.get("/{memory_id}", response_model=MemoryInDB)
async def read_memory(
    memory_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取单条记忆"""
    memory = db.query(Memory)\
        .filter(Memory.id == memory_id, Memory.user_id == current_user.id)\
        .first()
    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")
    return memory

@router.patch("/{memory_id}", response_model=MemoryInDB)
async def update_memory(
    memory_id: UUID,
    memory_in: MemoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新记忆"""
    memory = db.query(Memory)\
        .filter(Memory.id == memory_id, Memory.user_id == current_user.id)\
        .first()
    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")
    
    update_data = memory_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(memory, field, value)
    
    db.commit()
    db.refresh(memory)
    return memory

@router.delete("/{memory_id}")
async def delete_memory(
    memory_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除记忆"""
    memory = db.query(Memory)\
        .filter(Memory.id == memory_id, Memory.user_id == current_user.id)\
        .first()
    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")
    
    db.delete(memory)
    db.commit()
    return {"status": "success"} 