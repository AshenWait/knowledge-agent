from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

engine = create_engine(settings.database_url, echo=False)#拿到数据库信息

#创建会话工厂db = SessionLocal()然后通过 db 查询、插入、提交数据
"""_summary_

autoflush=False
表示不要自动把改动刷到数据库，交给我们控制。
autocommit=False
表示不要自动提交事务，后面要手动
"""
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


"""
# 实际上相当于执行以下操作：
connection = engine.connect()  # 1. 建立连接
try:
    # 2. 在这里执行数据库操作
    # ... 你的代码 ...
finally:
    connection.close()  # 3. 无论是否出错，都关闭连接
"""
def check_database_connection() -> bool:
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        return result.scalar_one() == 1