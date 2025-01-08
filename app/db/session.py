from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# 创建数据库引擎
# settings.get_database_url 返回类似：postgresql://user:password@localhost/dbname
engine = create_engine(
    settings.get_database_url,
    # pool_pre_ping=True 会在每次连接前ping一下数据库，确保连接有效
    pool_pre_ping=True,
    # echo=True 会打印所有SQL语句，方便调试
    echo=settings.SQL_DEBUG
)

# 创建会话工厂
# autocommit=False：默认不自动提交事务
# autoflush=False：默认不自动刷新
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """
    数据库会话依赖项
    
    用法:
    ```python
    @app.get("/users/")
    def read_users(db: Session = Depends(get_db)):
        users = db.query(User).all()
        return users
    ```
    
    yield 语句使这个函数成为一个上下文管理器:
    1. 创建数据库会话
    2. 使用会话执行操作
    3. 操作完成后自动关闭会话
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 