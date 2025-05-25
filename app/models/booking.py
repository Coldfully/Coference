"""!
@file booking.py
@brief 会议预定数据库模型模块
@details 定义会议预定相关的数据库模型和转换方法
@date 2025.5.25
"""

import datetime
from sqlalchemy import Integer, DateTime, ForeignKeyConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.models.database import Base

class EmployeeConferenceDB(Base):
    """!
    @brief SQLAlchemy 模型，数据库中的 'employee_conference' 表。
    @details 存储员工和会议之间的关联关系。
    """
    __tablename__ = "employee_conference"

    employee_id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    conference_id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)

    __table_args__ = (
        ForeignKeyConstraint(['employee_id'], ['employees.id'], ondelete='CASCADE'),
        ForeignKeyConstraint(['conference_id'], ['conferences.id'], ondelete='CASCADE'),
    )

    def to_pydantic(self) -> "EmployeeConference":
        """! 
        @brief 将 SQLAlchemy 模型转换为 Pydantic 模型。
        @return EmployeeConference 转换后的 Pydantic 模型实例。
        """
        from app.schemas.booking import EmployeeConference
        return EmployeeConference(
            employee_id=self.employee_id,
            conference_id=self.conference_id
        )

class ConferenceBookingDB(Base):
    """!
    @brief SQLAlchemy 模型，数据库中的 'conference_bookings' 表。
    @details 存储会议预定的详细信息，包括预定时间等。
    """
    __tablename__ = "conference_bookings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    conference_id: Mapped[int] = mapped_column(Integer, nullable=False)
    employee_id: Mapped[int] = mapped_column(Integer, nullable=False)
    booking_date: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, default=datetime.datetime.utcnow)

    def to_pydantic(self) -> "ConferenceBooking":
        """! 
        @brief 将 SQLAlchemy 模型转换为 Pydantic 模型。
        @return ConferenceBooking 转换后的 Pydantic 模型实例。
        """
        from app.schemas.booking import ConferenceBooking
        return ConferenceBooking(
            id=self.id,
            conference_id=self.conference_id,
            employee_id=self.employee_id,
            booking_date=self.booking_date
        ) 