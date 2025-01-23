import enum

class MemoryType(enum.Enum):
    TIMELINE = "TIMELINE"        # 时间轴记录
    CORE_FOCUS = "CORE_FOCUS"   # 核心关注点
    DREAM_TRACK = "DREAM_TRACK" # 梦想追踪
    QUICK_NOTE = "QUICK_NOTE"   # 快速记录

class CoreFocusType(enum.Enum):
    CHANGE = "CHANGE"           # 今日改变
    EXTERNAL_EXPECT = "EXTERNAL_EXPECT"  # 外部期待
    SELF_EXPECT = "SELF_EXPECT"         # 个人期待
    IMPORTANT = "IMPORTANT"             # 重要事项
    LONG_TERM = "LONG_TERM"            # 长期目标 