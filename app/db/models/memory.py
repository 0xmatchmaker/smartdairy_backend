from sqlalchemy import Column, Text, ForeignKey, JSON, Table
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
import uuid
from .base import Base

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
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False)
    content = Column(Text, nullable=False)
    tags = Column(ARRAY(String), default=[])  # 使用标签来实现分类功能
    emotion_score = Column(JSON, default={})  # 存储情绪分析结果
    vector = Column(ARRAY(Float), nullable=True)  # 存储语义向量
    
    # 关联
    user = relationship("User", back_populates="memories")
    
    # 记忆关联关系
    related_memories = relationship(
        'Memory',
        secondary=memory_relations,
        primaryjoin=id==memory_relations.c.source_id,
        secondaryjoin=id==memory_relations.c.target_id,
        backref='referenced_by'
    ) 