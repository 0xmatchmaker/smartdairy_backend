from sqlalchemy import Column, Text, ForeignKey, JSON, Table, String, Float, Enum, Time, Boolean, Date
from sqlalchemy.dialects.postgresql import UUID, ARRAY
# 暂时注释掉关系导入
# from sqlalchemy.orm import relationship
from sqlalchemy.orm import Session
import uuid
from .base import Base
from .enums import MemoryType, CoreFocusType

# 记忆关联的中间表 - 暂时注释掉
# memory_relations = Table(
#     'memory_relations',
#     Base.metadata,
#     Column('source_id', UUID(as_uuid=True), ForeignKey('memories.id'), primary_key=True),
#     Column('target_id', UUID(as_uuid=True), ForeignKey('memories.id'), primary_key=True),
#     Column('relation_type', String, nullable=False),
#     Column('relation_score', Float, default=0.0)
# )

class Memory(Base):
    """升级后的记忆模型，支持多种记录类型和结构化数据"""
    __tablename__ = "memories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # 基础字段
    memory_type = Column(Enum(MemoryType), nullable=False, comment="记忆类型")
    content = Column(Text, nullable=False, comment="主要内容")
    tags = Column(ARRAY(String), default=[], comment="标签数组")
    
    # 时间轴相关字段
    timeline_time = Column(Time, nullable=True, comment="时间点")
    is_preset = Column(Boolean, default=False, comment="是否预设时间点")
    
    # 核心关注点相关字段
    focus_type = Column(Enum(CoreFocusType), nullable=True, comment="核心关注点类型")
    
    # 分析字段
    emotion_score = Column(JSON, default={}, comment="情绪分析结果")
    vector = Column(ARRAY(Float), nullable=True, comment="语义向量")
    
    # 关联关系 - 暂时注释掉
    # user = relationship("User", back_populates="memories")
    # related_memories = relationship(
    #     'Memory',
    #     secondary='memory_relations',
    #     primaryjoin=id==memory_relations.c.source_id,
    #     secondaryjoin=id==memory_relations.c.target_id,
    #     backref='referenced_by'
    # )

    @classmethod
    async def create_from_text(cls, text: str, user_id: UUID, db: Session) -> "Memory":
        """从自由文本创建结构化记忆"""
        # 暂时注释掉 LLM 相关功能
        # llm_service = LLMService()
        # analyzed_data = await llm_service.analyze_content(text)
        
        # 创建基础记忆实例
        memory = cls(
            user_id=user_id,
            content=text,
            memory_type=MemoryType.QUICK_NOTE,  # 默认为快速记录
            tags=[],
        )
            
        return memory 