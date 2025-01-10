from sqlalchemy import Column, Text, ForeignKey, JSON, Table, String, Float, Enum, Time, Boolean, Date
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
import uuid
import enum
from .base import Base
from app.services.llm_service import LLMService
from sqlalchemy.orm import Session

# 记忆类型枚举
class MemoryType(enum.Enum):
    TIMELINE = "timeline"        # 时间轴记录
    CORE_FOCUS = "core_focus"   # 核心关注点
    DREAM_TRACK = "dream_track" # 梦想追踪
    QUICK_NOTE = "quick_note"   # 快速记录

# 核心关注点类型
class CoreFocusType(enum.Enum):
    CHANGE = "change"           # 今日改变
    EXTERNAL_EXPECT = "external_expect"  # 外部期待
    SELF_EXPECT = "self_expect"         # 个人期待
    IMPORTANT = "important"             # 重要事项

# 记忆关联的中间表
memory_relations = Table(
    'memory_relations',
    Base.metadata,
    Column('source_id', UUID(as_uuid=True), ForeignKey('memory.id'), primary_key=True),
    Column('target_id', UUID(as_uuid=True), ForeignKey('memory.id'), primary_key=True),
    Column('relation_type', String, nullable=False),  # 关联类型：'similar'(相似),'sequence'(前后顺序),'reference'(引用)等
    Column('relation_score', Float, default=0.0)  # 关联强度
)

class Memory(Base):
    """
    升级后的记忆模型，支持多种记录类型和结构化数据
    """
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False)
    
    # 基础字段
    memory_type = Column(Enum(MemoryType), nullable=False, comment="记忆类型")
    content = Column(Text, nullable=False, comment="主要内容")
    tags = Column(ARRAY(String), default=[], comment="标签数组")
    
    # 时间轴相关字段
    timeline_time = Column(Time, nullable=True, comment="时间点")
    is_preset = Column(Boolean, default=False, comment="是否预设时间点")
    
    # 核心关注点相关字段
    focus_type = Column(Enum(CoreFocusType), nullable=True, comment="核心关注点类型")
    
    # 梦想追踪相关字段
    dream_id = Column(UUID(as_uuid=True), ForeignKey("dream.id"), nullable=True)
    progress_value = Column(Float, nullable=True, comment="进度值")
    
    # 快速记录相关字段
    voice_url = Column(String, nullable=True, comment="语音文件URL")
    template_id = Column(UUID(as_uuid=True), nullable=True, comment="使用的模板ID")
    
    # 分析字段
    emotion_score = Column(JSON, default={}, comment="情绪分析结果")
    vector = Column(ARRAY(Float), nullable=True, comment="语义向量")
    
    # 关联关系
    user = relationship("User", back_populates="memories")
    dream = relationship("Dream", back_populates="memories")
    related_memories = relationship(
        'Memory',
        secondary='memory_relations',
        primaryjoin=id==memory_relations.c.source_id,
        secondaryjoin=id==memory_relations.c.target_id,
        backref='referenced_by'
    )

    @classmethod
    async def create_from_text(cls, text: str, user_id: UUID, db: Session) -> "Memory":
        """
        从自由文本创建结构化记忆
        
        使用示例：
        ```python
        memory = await Memory.create_from_text(
            "今天和团队讨论了新项目...",
            user_id=current_user.id,
            db=session
        )
        ```
        """
        llm_service = LLMService()
        analyzed_data = await llm_service.analyze_content(text)
        
        # 创建记忆实例
        memory = cls(
            user_id=user_id,
            content=text,  # 保存原始文本
            memory_type=analyzed_data['memory_type'],
            tags=analyzed_data['structured_data'].get('tags', []),
            emotion_score=analyzed_data['emotion_score']
        )
        
        # 根据分析结果填充结构化字段
        if 'timeline' in analyzed_data['structured_data']:
            memory.timeline_time = analyzed_data['structured_data']['timeline']['time']
            memory.is_preset = analyzed_data['structured_data']['timeline']['is_preset']
            
        if 'core_focus' in analyzed_data['structured_data']:
            memory.focus_type = analyzed_data['structured_data']['core_focus']['type']
            
        # 检查是否包含梦想相关内容
        dream_data = await llm_service.extract_dreams(text)
        if dream_data:
            # 创建或更新梦想记录
            dream = Dream(
                user_id=user_id,
                **dream_data
            )
            db.add(dream)
            memory.dream = dream
            
        return memory

# 梦想目标模型
class Dream(Base):
    """
    梦想追踪模型
    """
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False)
    title = Column(String, nullable=False, comment="梦想标题")
    description = Column(Text, nullable=True, comment="详细描述")
    target_date = Column(Date, nullable=True, comment="目标日期")
    target_value = Column(Float, nullable=True, comment="目标值")
    current_value = Column(Float, default=0, comment="当前进度")
    
    # 关联关系
    user = relationship("User", back_populates="dreams")
    memories = relationship("Memory", back_populates="dream") 