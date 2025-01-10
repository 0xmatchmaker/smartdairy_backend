from app.db.models.base import Base
from app.db.models.user import User

# 暂时只导入基础用户模型，等认证功能完成后再逐步添加其他模型
# from app.db.models.preset import PresetTimepoint
# from app.db.models.template import Template
# from app.db.models.memory import Memory, memory_relations
# from app.db.models.progress import DreamProgress

# 确保所有模型都被导入，这样 Alembic 才能检测到它们
__all__ = [
    "Base",
    "User",
    # 暂时注释掉其他模型，等基础功能完成后再逐步添加
    # "PresetTimepoint",
    # "Template",
    # "Memory",
    # "DreamProgress",
] 