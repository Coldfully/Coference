import datetime
from pydantic import BaseModel, Field

class EmployeeConference(BaseModel):
    """!
    @brief 表示员工-会议关联的 Pydantic 模型。
    """
    employee_id: int = Field(..., example=1)
    conference_id: int = Field(..., example=1)

    class Config:
        orm_mode = True

class ConferenceBookingBase(BaseModel):
    """!
    @brief 会议预定 Pydantic 模型。
    """
    conference_id: int = Field(..., example=1)
    employee_id: int = Field(..., example=1)

class ConferenceBookingCreate(ConferenceBookingBase):
    """!
    @brief 创建新会议预定时使用的 Pydantic 模型。
    """
    pass

class ConferenceBooking(ConferenceBookingBase):
    """!
    @brief 表示一个会议预定对象的完整 Pydantic 模型。
    """
    id: int = Field(..., example=1)
    booking_date: datetime.datetime = Field(..., example="2024-03-20T10:00:00")

    class Config:
        orm_mode = True 