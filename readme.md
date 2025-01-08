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
  - content: 记忆内容（文本格式）
  - tags: 标签数组（用于分类和检索）
  - created_at: 创建时间
  - updated_at: 更新时间

- 分析信息
  - emotion_score: 情绪分析结果
  - vector: 语义向量表示

- 关联关系
  - user: 所属用户
  - related_memories: 相关记忆
  - referenced_by: 被引用记忆

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