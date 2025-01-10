from fastapi import APIRouter
from app.api.v1.endpoints import auth, memories, timeline # 暂时移除 dreams

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(memories.router, prefix="/memories", tags=["memories"])
api_router.include_router(timeline.router, prefix="/timeline", tags=["timeline"]) 
# api_router.include_router(dreams.router, prefix="/dreams", tags=["dreams"])  # 暂时注释掉 