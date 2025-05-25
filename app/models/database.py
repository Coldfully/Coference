"""!
@file database.py
@brief 数据库连接和会话管理模块
@details 提供数据库连接、会话管理和基础模型类
@date 2025.5.25
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.core.config import DATABASE_URL

# SQLAlchemy 异步引擎
engine = create_async_engine(DATABASE_URL, echo=True)

# SQLAlchemy 异步会话工厂
AsyncSessionLocal = async_sessionmaker(
    autocommit=False, autoflush=False, bind=engine, class_=AsyncSession
)

# SQLAlchemy 声明式基类
Base = declarative_base()

# 数据库会话依赖
async def get_db() -> AsyncSession:
    """!
    @brief FastAPI 依赖项，用于获取数据库会话。
    @details 在每个请求开始时创建一个会话，在请求结束时关闭。
    @yields AsyncSession 数据库会话。
    @exception Exception 当数据库操作发生错误时抛出异常。
    """
    print("DB Session: Acquiring session from pool.")
    async with AsyncSessionLocal() as session:
        print("DB Session: Acquired. Yielding to endpoint.")
        try:
            yield session
            print("DB Session: Endpoint finished. Transaction implicitly managed by 'async with' if committed.")
        except Exception as e_get_db:
            print(f"!!! DB Session: Exception bubbled up to get_db or occurred during session handling. Rolling back. !!!")
            print(f"get_db error type: {type(e_get_db)}")
            print(f"get_db error message: {str(e_get_db)}")
            print("get_db stack trace:")
            import traceback
            print(traceback.format_exc())
            await session.rollback()
            raise
        finally:
            print("DB Session: Releasing session back to pool (implicitly by 'async with').") 