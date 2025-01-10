# 记忆管理系统后端 MVP

## 项目简介
这是一个基于 FastAPI 的记忆管理系统后端，支持记忆的收集、整理、关联与检索，以及反思引导功能。

## 技术栈
- Python 3.9+
- FastAPI
- PostgreSQL
- Redis
- FAISS

## 项目结构 
memory_backend/
├── app/
│ ├── api/ # API 路由
│ ├── core/ # 核心配置
│ ├── db/ # 数据库模型和工具
│ ├── services/ # 业务逻辑
│ └── utils/ # 工具函数
├── tests/ # 测试文件
├── alembic/ # 数据库迁移
├── .env # 环境变量
└── requirements.txt # 依赖包

## 数据模型

### Memory 模型
- 基础信息
  - id: UUID 主键
  - user_id: 关联用户ID
  - memory_type: 记忆类型
    - TIMELINE: 时间轴记录
    - CORE_FOCUS: 核心关注点
    - DREAM_TRACK: 梦想追踪
    - QUICK_NOTE: 快速记录
  - content: 记忆内容
  - tags: 标签数组

  - 时间轴功能
    - timeline_time: 时间点
    - is_preset: 是否预设时间点

  - 核心关注点
    - focus_type: 关注点类型
      - CHANGE: 今日改变
      - EXTERNAL_EXPECT: 外部期待
      - SELF_EXPECT: 个人期待
      - IMPORTANT: 重要事项

  - 梦想追踪
    - dream_id: 关联的梦想ID
    - progress_value: 进度值

  - 快速记录
    - voice_url: 语音文件URL
    - template_id: 使用的模板ID

- 分析信息
  - emotion_score: 情绪分析结果
  - vector: 语义向量表示

### Dream 模型
- 基础信息
  - id: UUID 主键
  - user_id: 关联用户ID
  - title: 梦想标题
  - description: 详细描述
  - target_date: 目标日期
  - target_value: 目标值
  - current_value: 当前进度

## 数据库配置
1. 创建数据库
```bash
createdb memory_db
```

2. 环境变量配置(.env)
```bash
POSTGRES_SERVER=localhost
POSTGRES_USER=your_user
POSTGRES_PASSWORD=your_password
POSTGRES_DB=memory_db
```

+ ## 数据库会话管理
+ 
+ 系统使用 SQLAlchemy 的会话管理机制：
+ 
+ ```python
+ # 在 API 路由中使用数据库会话
+ @app.get("/memories/")
+ def read_memories(db: Session = Depends(get_db)):
+     memories = db.query(Memory).all()
+     return memories
+ ```
+ 
+ 特点：
+ - 自动连接池管理
+ - 自动会话清理
+ - 支持事务管理
+ - 内置连接健康检查
+ 
+ 配置参数：
+ - pool_pre_ping: 启用连接健康检查
+ - echo: 在调试模式下打印 SQL 语句
+ - autocommit: 默认关闭自动提交
+ - autoflush: 默认关闭自动刷新

## 备注：整体项目设计要求：
1. 时间轴框架
   - 预设基本时间点(起床、三餐、就寝等)
   - 简单点击或拖拽即可标记
   - 可选择性添加简短备注
2. 核心关注点(每日必填)
   - 今日改变(What changed)
   - 外部期待(Expected from others)
   - 个人期待(My expectations)
   - 重要事项(What really matters)
3. 梦想追踪区
   - 固定展示区域显示长期目标
   - 记录与梦想相关的每日进展
   - 可视化展示距离目标的进度
4. 快速记录功能
   - 语音输入
   - 快捷短语
   - 标签系统
   - 模板功能
5. 特别前端要求（需要后端配合）:
- 界面要简洁,突出重要内容
- 日常事项尽量用选择/点击方式完成
- 重点关注"改变"和"期待"
- 让用户容易看到自己的进步和距离目标的距离
