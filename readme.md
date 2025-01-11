# 记忆管理系统后端 MVP

## 项目简介
这是一个基于 FastAPI 的记忆管理系统后端，支持记忆的收集、整理、关联与检索，以及反思引导功能。

## 技术栈
- Python 3.9+
- FastAPI
- PostgreSQL
- Redis
- FAISS

## 部署指南 🚀

### 1. 环境要求
- Python 3.9+
- PostgreSQL 12+
- Nginx
- 操作系统：Ubuntu 20.04/22.04 LTS

### 2. 安装步骤

#### 2.1 基础环境配置
```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装必要工具
sudo apt install -y python3-pip python3-dev build-essential libssl-dev libffi-dev python3-setuptools python3-venv git nginx

# 安装 PostgreSQL
sudo apt install -y postgresql postgresql-contrib
```

#### 2.2 数据库配置
```bash
# 切换到 postgres 用户
sudo -u postgres psql

# 创建数据库和用户
CREATE DATABASE memory_db;
CREATE USER memory_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE memory_db TO memory_user;

# 退出 PostgreSQL
\q
```

#### 2.3 项目部署
```bash
# 创建项目目录
mkdir -p /var/www/memory_backend
cd /var/www/memory_backend

# 克隆项目
git clone <项目地址> .
git checkout deploy  # 切换到部署分支

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

#### 2.4 环境变量配置
创建 `.env` 文件并配置以下变量：
```bash
# 数据库配置
POSTGRES_SERVER=localhost
POSTGRES_USER=memory_user
POSTGRES_PASSWORD=your_password
POSTGRES_DB=memory_db

# JWT配置
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=1440  # 24小时

# 其他配置
SQL_DEBUG=false
```

#### 2.5 数据库迁移
```bash
# 执行数据库迁移
alembic upgrade head
```

### 3. 服务配置

#### 3.1 Gunicorn 服务
创建服务文件：
```bash
sudo nano /etc/systemd/system/memory_backend.service
```

配置内容：
```ini
[Unit]
Description=Memory Backend
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/var/www/memory_backend
Environment="PATH=/var/www/memory_backend/venv/bin"
ExecStart=/var/www/memory_backend/venv/bin/gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b unix:/tmp/memory_backend.sock

[Install]
WantedBy=multi-user.target
```

#### 3.2 Nginx 配置
```nginx
server {
    listen 80;
    server_name your_domain.com;  # 替换为实际域名

    location / {
        proxy_pass http://unix:/tmp/memory_backend.sock;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

### 4. 启动服务
```bash
# 启动后端服务
sudo systemctl start memory_backend
sudo systemctl enable memory_backend

# 启动 Nginx
sudo systemctl restart nginx
```

### 5. 维护指南

#### 5.1 查看日志
```bash
# 应用日志
sudo journalctl -u memory_backend

# Nginx 日志
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

#### 5.2 更新部署
```bash
cd /var/www/memory_backend
git pull
source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
sudo systemctl restart memory_backend
```

## API 文档
部署完成后，可以通过以下地址访问 API 文档：
- Swagger UI: `http://your_domain/docs`
- ReDoc: `http://your_domain/redoc`

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

## 数据库会话管理

系统使用 SQLAlchemy 的会话管理机制：

```python
# 在 API 路由中使用数据库会话
@app.get("/memories/")
def read_memories(db: Session = Depends(get_db)):
    memories = db.query(Memory).all()
    return memories
```

特点：
- 自动连接池管理
- 自动会话清理
- 支持事务管理
- 内置连接健康检查

配置参数：
- pool_pre_ping: 启用连接健康检查
- echo: 在调试模式下打印 SQL 语句
- autocommit: 默认关闭自动提交
- autoflush: 默认关闭自动刷新

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

## 开发说明

### 阶段性开发计划
1. 第一阶段：基础认证功能（已完成 ✅）
   - [x] 用户注册
   - [x] 用户登录
   - [x] JWT认证
   - [x] 基础CRUD操作

2. 第二阶段：记忆管理（进行中）
   - [x] Memory模型关联
   - [x] 时间轴功能
   - [x] 核心关注点功能
      - [x] 重要事项管理
      - [x] 时间投入跟踪
      - [ ] 其他关注点类型

3. 第三阶段：目标追踪（待实现）
   - [ ] Dream模型关联
   - [ ] 进度追踪功能
   - [ ] 模板功能

4. 第四阶段：高级功能（待实现）
   - [ ] LLM集成
   - [ ] 情感分析
   - [ ] 关联分析

### 已实现的 API 端点

1. 认证相关
```bash
# 用户注册
POST /api/v1/auth/register
Content-Type: application/json
{
    "email": "user@example.com",
    "username": "username",
    "password": "password123"
}

# 用户登录
POST /api/v1/auth/login
Content-Type: application/x-www-form-urlencoded
username=user@example.com&password=password123
```

2. 记忆管理
```bash
# 创建记忆
POST /api/v1/memories/
Authorization: Bearer {token}
Content-Type: application/json
{
    "content": "记忆内容",
    "memory_type": "quick_note",
    "tags": ["标签1", "标签2"]
}

# 获取记忆列表
GET /api/v1/memories/
Authorization: Bearer {token}

# 获取记忆详情
GET /api/v1/memories/{memory_id}
Authorization: Bearer {token}

# 更新记忆
PATCH /api/v1/memories/{memory_id}
Authorization: Bearer {token}
Content-Type: application/json
{
    "content": "更新的内容",
    "tags": ["新标签"]
}

# 删除记忆
DELETE /api/v1/memories/{memory_id}
Authorization: Bearer {token}
```

3. 重要事项管理
```bash
# 创建重要事项
POST /api/v1/core-focus/important
Content-Type: application/json
{
    "content": "任务内容",
    "target_minutes": 240,
    "date": "2024-01-11",
    "tags": ["标签1", "标签2"],
    "description": "详细说明"
}

# 查看每日重要事项
GET /api/v1/core-focus/important/daily?date=2024-01-11

# 开始重要事项活动
POST /api/v1/core-focus/important/{matter_id}/start
Content-Type: application/json
{
    "content": "活动说明"
}

# 结束重要事项活动
POST /api/v1/core-focus/important/{matter_id}/end
Content-Type: application/json
{
    "content": "完成说明"
}

# 查看重要事项活动历史
GET /api/v1/core-focus/important/{matter_id}/activities
```

## 项目进展

### 2024-01-11 重要事项功能
完成了重要事项功能的开发：
- 支持创建重要事项并设置目标时间
- 实现与时间轴活动的关联
- 提供活动历史查询接口
- 支持完成度实时计算
- 优化了活动记录格式
- 添加了格式化时间显示
- 实现了活动标签继承


