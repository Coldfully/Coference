import datetime
from typing import Optional
from pydantic import BaseModel, Field

class EmployeeBase(BaseModel):
    """!
    @brief 员工 Pydantic 模型。
    """
    name: str = Field(..., min_length=1, max_length=100, example="张三")
    email: str = Field(..., min_length=1, max_length=100, example="zhangsan@example.com")
    department: str = Field(..., min_length=1, max_length=100, example="技术部")
    position: str = Field(..., min_length=1, max_length=100, example="工程师")
    phone: Optional[str] = Field(None, min_length=1, max_length=20, example="13800138000")

class EmployeeCreate(EmployeeBase):
    """!
    @brief 创建新员工时使用的 Pydantic 模型。
    """
    pass

class EmployeeUpdate(EmployeeBase):
    """!
    @brief 更新员工信息时使用的 Pydantic 模型。
    """
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[str] = Field(None, min_length=1, max_length=100)
    department: Optional[str] = Field(None, min_length=1, max_length=100)
    position: Optional[str] = Field(None, min_length=1, max_length=100)
    phone: Optional[str] = Field(None, min_length=1, max_length=20)

class Employee(EmployeeBase):
    """!
    @brief 表示一个员工对象的完整 Pydantic 模型，包含 ID。
    """
    id: int = Field(..., example=1)
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        orm_mode = True 