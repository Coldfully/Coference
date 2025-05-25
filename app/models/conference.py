"""!
@file conference.py
@brief 会议数据库模型模块
@details 定义会议相关的数据库模型和转换方法
@date 2025.5.25
"""

import datetime
from sqlalchemy import Integer, String, Date, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.models.database import Base

class ConferenceDB(Base):
    """!
    @brief SQLAlchemy 模型，数据库中的 'conferences' 表。
    @details 存储会议的基本信息，包括名称、日期、地点等。
    """
    __tablename__ = "conferences"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    location: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    def to_pydantic(self) -> "Conference":
        """! 
        @brief 将 SQLAlchemy 模型转换为 Pydantic 模型。
        @return Conference 转换后的 Pydantic 模型实例。
        """
        from app.schemas.conference import Conference
        return Conference(
            id=self.id,
            name=self.name,
            date=self.date,
            location=self.location,
            description=self.description,
            created_at=self.created_at,
            updated_at=self.updated_at
        ) 