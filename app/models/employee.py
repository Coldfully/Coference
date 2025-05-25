"""!
@file employee.py
@brief 员工数据库模型模块
@details 定义员工相关的数据库模型和转换方法
@date 2025.5.25
"""

import datetime
from sqlalchemy import Integer, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.models.database import Base

class EmployeeDB(Base):
    """!
    @brief SQLAlchemy 模型，数据库中的 'employees' 表。
    @details 存储员工的基本信息，包括姓名、邮箱、部门等。
    """
    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    department: Mapped[str] = mapped_column(String(100), nullable=False)
    position: Mapped[str] = mapped_column(String(100), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    def to_pydantic(self) -> "Employee":
        """! 
        @brief 将 SQLAlchemy 模型转换为 Pydantic 模型。
        @return Employee 转换后的 Pydantic 模型实例。
        """
        from app.schemas.employee import Employee
        return Employee(
            id=self.id,
            name=self.name,
            email=self.email,
            department=self.department,
            position=self.position,
            phone=self.phone,
            created_at=self.created_at,
            updated_at=self.updated_at
        ) 