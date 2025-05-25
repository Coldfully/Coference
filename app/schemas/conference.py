import datetime
from typing import Optional
from pydantic import BaseModel, Field

class ConferenceBase(BaseModel):
    """!
    @brief 会议 Pydantic 模型。
    """
    name: str = Field(..., min_length=1, max_length=255, example="会议名称")
    date: datetime.date = Field(..., example="2008-1-1")
    location: str = Field(..., min_length=1, max_length=255, example="会议地点")
    description: Optional[str] = Field(None, example="会议描述")

class ConferenceCreate(ConferenceBase):
    """!
    @brief 创建新会议时使用的 Pydantic 模型。
    """
    pass

class ConferenceUpdate(ConferenceBase):
    """!
    @brief 更新会议时使用的 Pydantic 模型
    """
    name: Optional[str] = Field(None, min_length=1, max_length=255, example="会议名称更改")
    date: Optional[datetime.date] = Field(None, example="2008-2-2")
    location: Optional[str] = Field(None, min_length=1, max_length=255, example="会议地点更改")
    description: Optional[str] = Field(None, example="会议描述更改")

class Conference(ConferenceBase):
    """!
    @brief 表示一个会议对象的完整 Pydantic 模型，包含 ID。
    """
    id: int = Field(..., example=1)
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        orm_mode = True 