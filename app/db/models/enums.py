import enum

class MemoryType(enum.Enum):
    TIMELINE = "timeline"        # 时间轴记录
    CORE_FOCUS = "core_focus"   # 核心关注点
    DREAM_TRACK = "dream_track" # 梦想追踪
    QUICK_NOTE = "quick_note"   # 快速记录

class CoreFocusType(enum.Enum):
    CHANGE = "change"           # 今日改变
    EXTERNAL_EXPECT = "external_expect"  # 外部期待
    SELF_EXPECT = "self_expect"         # 个人期待
    IMPORTANT = "important"             # 重要事项 