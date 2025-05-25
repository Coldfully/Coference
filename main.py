# -*- coding: utf-8 -*-
"""!
@brief 主 FastAPI 应用文件，用于管理会议。
@details 提供 API 端点来获取会议列表、添加新会议，提供前端页面。
"""

import datetime
import os
from typing import List, Optional, AsyncGenerator

from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from sqlalchemy import Integer, String, Date, Text, DateTime, ForeignKeyConstraint
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base, Mapped, mapped_column
import traceback

# --- 全局变量和配置 ---

#: 加载 .env 文件中的环境变量
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./conference.db")  # 默认为 SQLite (如果 .env 未设置)
if "mysql" not in DATABASE_URL and "sqlite" in DATABASE_URL:
    print("Warning: DATABASE_URL not found or not MySQL. Using default SQLite for demo.")

#: FastAPI 实例
app = FastAPI(title="会议管理系统", description="简易的会议管理系统 API")

#: 挂载静态文件目录
app.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static")), name="static")
app.mount("/source", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "source")), name="source")

#: 配置模板目录
templates = Jinja2Templates(directory="templates")

# --- SQLAlchemy 数据库设置 ---

#: SQLAlchemy 异步引擎
engine = create_async_engine(DATABASE_URL, echo=True)  # echo=True 用于调试，会打印 SQL 语句

#: SQLAlchemy 异步会话工厂
AsyncSessionLocal = async_sessionmaker(
    autocommit=False, autoflush=False, bind=engine, class_=AsyncSession
)

#: SQLAlchemy 声明式基类
Base = declarative_base()


# --- SQLAlchemy 数据模型 ---
class ConferenceDB(Base):
    """!
    @brief SQLAlchemy 模型，数据库中的 'conferences' 表。
    """
    __tablename__ = "conferences"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    location: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    def to_pydantic(self) -> "Conference":
        """! @brief 将 SQLAlchemy 模型转换为 Pydantic 模型。 """
        return Conference(
            id=self.id,
            name=self.name,
            date=self.date,
            location=self.location,
            description=self.description,
            created_at=self.created_at,
            updated_at=self.updated_at
        )


class EmployeeDB(Base):
    """!
    @brief SQLAlchemy 模型，数据库中的 'employees' 表。
    """
    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    department: Mapped[str] = mapped_column(String(100), nullable=False)
    position: Mapped[str] = mapped_column(String(100), nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    def to_pydantic(self) -> "Employee":
        """! @brief 将 SQLAlchemy 模型转换为 Pydantic 模型。 """
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


class EmployeeConferenceDB(Base):
    """!
    @brief SQLAlchemy 模型，数据库中的 'employee_conference' 表。
    """
    __tablename__ = "employee_conference"

    employee_id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    conference_id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)

    __table_args__ = (
        ForeignKeyConstraint(['employee_id'], ['employees.id'], ondelete='CASCADE'),
        ForeignKeyConstraint(['conference_id'], ['conferences.id'], ondelete='CASCADE'),
    )

    def to_pydantic(self) -> "EmployeeConference":
        """! @brief 将 SQLAlchemy 模型转换为 Pydantic 模型。 """
        return EmployeeConference(
            employee_id=self.employee_id,
            conference_id=self.conference_id
        )


class ConferenceBookingDB(Base):
    """!
    @brief SQLAlchemy 模型，数据库中的 'conference_bookings' 表。
    """
    __tablename__ = "conference_bookings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    conference_id: Mapped[int] = mapped_column(Integer, nullable=False)
    employee_id: Mapped[int] = mapped_column(Integer, nullable=False)
    booking_date: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, default=datetime.datetime.utcnow)

    def to_pydantic(self) -> "ConferenceBooking":
        """! @brief 将 SQLAlchemy 模型转换为 Pydantic 模型。 """
        return ConferenceBooking(
            id=self.id,
            conference_id=self.conference_id,
            employee_id=self.employee_id,
            booking_date=self.booking_date
        )


# --- Pydantic 数据模型 ---

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


# --- 数据库会话依赖 ---
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """!
    @brief FastAPI 依赖项，用于获取数据库会话。
    @details 在每个请求开始时创建一个会话，在请求结束时关闭。
    @yields AsyncSession 数据库会话。
    """
    print("DB Session: Acquiring session from pool.")
    async with AsyncSessionLocal() as session:
        print("DB Session: Acquired. Yielding to endpoint.")
        try:
            yield session
            # If the endpoint called session.commit() and no exception occurred here or after,
            # the transaction will be persisted.
            print("DB Session: Endpoint finished. Transaction implicitly managed by 'async with' if committed.")
        except Exception as e_get_db:
            print(
                f"!!! DB Session: Exception bubbled up to get_db or occurred during session handling. Rolling back. !!!")
            print(f"get_db error type: {type(e_get_db)}")
            print(f"get_db error message: {str(e_get_db)}")
            print("get_db stack trace:")
            print(traceback.format_exc())
            await session.rollback()
            raise  # Re-raise the exception for FastAPI to handle
        finally:
            # Session is automatically closed by 'async with AsyncSessionLocal() as session:'
            print("DB Session: Releasing session back to pool (implicitly by 'async with').")


# --- 应用启动和关闭事件 ---
@app.on_event("startup")
async def startup_event():
    """!
    @brief 应用启动时执行的事件。
    @details 创建数据库表（如果不存在）。
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("数据库表已初始化。")


# --- API 端点 ---

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """!
    @brief 提供前端 HTML 页面。
    @param request FastAPI 的请求对象。
    @return HTMLResponse 渲染后的 index.html 页面。
    """
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/api/conferences", response_model=List[Conference])
async def get_conferences(db: AsyncSession = Depends(get_db)):
    """!
    @brief 获取所有会议的列表。
    @param db 数据库会话，通过依赖注入获取。
    @return List[Conference] 包含所有会议信息的列表。
    """
    from sqlalchemy import select
    result = await db.execute(select(ConferenceDB).order_by(ConferenceDB.id))
    conferences_db_models = result.scalars().all()
    return [conf.to_pydantic() for conf in conferences_db_models]


@app.post("/api/conferences", response_model=Conference, status_code=201)
async def create_conference(conference_in: ConferenceCreate, db: AsyncSession = Depends(get_db)):
    """!
    @brief 创建一个新的会议。
    @param conference_in ConferenceCreate Pydantic 模型，包含新会议的数据。
    @param db 数据库会话。
    @return Conference 新创建的会议对象。
    """
    db_conference = ConferenceDB(**conference_in.model_dump())
    db.add(db_conference)
    await db.commit()
    await db.refresh(db_conference)
    return db_conference.to_pydantic()


@app.get("/api/conferences/{conference_id}", response_model=Conference)
async def get_conference(conference_id: int, db: AsyncSession = Depends(get_db)):
    """!
    @brief 获取指定 ID 的会议信息。
    @param conference_id 要获取的会议的 ID。
    @param db 数据库会话。
    @return Conference 指定 ID 的会议对象。
    @exception HTTPException 如果会议未找到 (404)。
    """
    db_conference = await db.get(ConferenceDB, conference_id)
    if db_conference is None:
        raise HTTPException(status_code=404, detail="Conference not found")
    return db_conference.to_pydantic()


@app.put("/api/conferences/{conference_id}", response_model=Conference)
async def update_conference(conference_id: int, conference_in: ConferenceUpdate, db: AsyncSession = Depends(get_db)):
    """!
    @brief 更新指定 ID 的会议信息。
    @param conference_id 要更新的会议的 ID。
    @param conference_in ConferenceUpdate Pydantic 模型，包含要更新的会议数据。
    @param db 数据库会话。
    @return Conference 更新后的会议对象。
    @exception HTTPException 如果会议未找到 (404)。
    """
    db_conference = await db.get(ConferenceDB, conference_id)
    if db_conference is None:
        raise HTTPException(status_code=404, detail="Conference not found")

    update_data = conference_in.model_dump(exclude_unset=True)  # 只获取已设置的字段
    for key, value in update_data.items():
        setattr(db_conference, key, value)

    await db.commit()
    await db.refresh(db_conference)
    return db_conference.to_pydantic()


@app.delete("/api/conferences/{conference_id}", response_model=dict)
async def delete_conference(conference_id: int, db: AsyncSession = Depends(get_db)):
    """!
    @brief 删除指定 ID 的会议。
    @param conference_id 要删除的会议的 ID。
    @param db 数据库会话。
    @return dict 包含成功消息的 dictionary。
    @exception HTTPException 如果会议未找到 (404)。
    """
    db_conference = await db.get(ConferenceDB, conference_id)
    if db_conference is None:
        raise HTTPException(status_code=404, detail="Conference not found")

    await db.delete(db_conference)
    await db.commit()
    return {"message": f"Conference with id {conference_id} deleted successfully"}


# 员工管理相关端点
@app.get("/api/employees", response_model=List[Employee])
async def get_employees(db: AsyncSession = Depends(get_db)):
    """!
    @brief 获取所有员工的列表。
    @param db 数据库会话。
    @return List[Employee] 包含所有员工信息的列表。
    """
    from sqlalchemy import select
    result = await db.execute(select(EmployeeDB).order_by(EmployeeDB.id))
    employees = result.scalars().all()
    return [emp.to_pydantic() for emp in employees]

@app.post("/api/employees", response_model=Employee, status_code=201)
async def create_employee(employee_in: EmployeeCreate, db: AsyncSession = Depends(get_db)):
    """!
    @brief 创建一个新的员工。
    @param employee_in EmployeeCreate Pydantic 模型。
    @param db 数据库会话。
    @return Employee 新创建的员工对象。
    """
    db_employee = EmployeeDB(**employee_in.model_dump())
    db.add(db_employee)
    await db.commit()
    await db.refresh(db_employee)
    return db_employee.to_pydantic()

@app.get("/api/employees/{employee_id}", response_model=Employee)
async def get_employee(employee_id: int, db: AsyncSession = Depends(get_db)):
    """!
    @brief 获取指定 ID 的员工信息。
    @param employee_id 要获取的员工的 ID。
    @param db 数据库会话。
    @return Employee 指定 ID 的员工对象。
    """
    db_employee = await db.get(EmployeeDB, employee_id)
    if db_employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    return db_employee.to_pydantic()

@app.put("/api/employees/{employee_id}", response_model=Employee)
async def update_employee(employee_id: int, employee_in: EmployeeUpdate, db: AsyncSession = Depends(get_db)):
    """!
    @brief 更新指定 ID 的员工信息。
    @param employee_id 要更新的员工的 ID。
    @param employee_in EmployeeUpdate Pydantic 模型。
    @param db 数据库会话。
    @return Employee 更新后的员工对象。
    """
    db_employee = await db.get(EmployeeDB, employee_id)
    if db_employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")

    update_data = employee_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_employee, key, value)

    await db.commit()
    await db.refresh(db_employee)
    return db_employee.to_pydantic()

@app.delete("/api/employees/{employee_id}", response_model=dict)
async def delete_employee(employee_id: int, db: AsyncSession = Depends(get_db)):
    """!
    @brief 删除指定 ID 的员工。
    @param employee_id 要删除的员工的 ID。
    @param db 数据库会话。
    @return dict 包含成功消息的 dictionary。
    """
    db_employee = await db.get(EmployeeDB, employee_id)
    if db_employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")

    await db.delete(db_employee)
    await db.commit()
    return {"message": f"Employee with id {employee_id} deleted successfully"}

# 会议预定相关端点
@app.post("/api/conferences/{conference_id}/book", response_model=EmployeeConference, status_code=201)
async def book_conference(
    conference_id: int,
    employee_id: int,
    db: AsyncSession = Depends(get_db)
):
    """!
    @brief 为员工预定会议。
    @param conference_id 要预定的会议 ID。
    @param employee_id 预定会议的员工 ID。
    @param db 数据库会话。
    @return EmployeeConference 新创建的预定记录。
    """
    # 检查会议是否存在
    conference = await db.get(ConferenceDB, conference_id)
    if conference is None:
        raise HTTPException(status_code=404, detail="Conference not found")
    
    # 检查员工是否存在
    employee = await db.get(EmployeeDB, employee_id)
    if employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")

    # 创建预定记录
    booking = EmployeeConferenceDB(
        conference_id=conference_id,
        employee_id=employee_id
    )
    db.add(booking)
    await db.commit()
    await db.refresh(booking)
    return booking.to_pydantic()

@app.get("/api/employees/{employee_id}/conferences", response_model=List[Conference])
async def get_employee_conferences(employee_id: int, db: AsyncSession = Depends(get_db)):
    """!
    @brief 获取指定员工的所有预定会议。
    @param employee_id 员工 ID。
    @param db 数据库会话。
    @return List[Conference] 员工预定的所有会议列表。
    """
    from sqlalchemy import select
    from sqlalchemy.orm import join

    # 检查员工是否存在
    employee = await db.get(EmployeeDB, employee_id)
    if employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")

    # 通过关联表查询会议
    query = select(ConferenceDB).join(
        EmployeeConferenceDB,
        ConferenceDB.id == EmployeeConferenceDB.conference_id
    ).where(EmployeeConferenceDB.employee_id == employee_id)
    
    result = await db.execute(query)
    conferences = result.scalars().all()
    return [conf.to_pydantic() for conf in conferences]

@app.get("/api/conferences/{conference_id}/attendees", response_model=List[Employee])
async def get_conference_attendees(conference_id: int, db: AsyncSession = Depends(get_db)):
    """!
    @brief 获取指定会议的所有与会人员。
    @param conference_id 会议 ID。
    @param db 数据库会话。
    @return List[Employee] 会议的所有与会人员列表。
    """
    from sqlalchemy import select
    from sqlalchemy.orm import join

    # 检查会议是否存在
    conference = await db.get(ConferenceDB, conference_id)
    if conference is None:
        raise HTTPException(status_code=404, detail="Conference not found")

    # 通过关联表查询员工
    query = select(EmployeeDB).join(
        EmployeeConferenceDB,
        EmployeeDB.id == EmployeeConferenceDB.employee_id
    ).where(EmployeeConferenceDB.conference_id == conference_id)
    
    result = await db.execute(query)
    employees = result.scalars().all()
    return [emp.to_pydantic() for emp in employees]

@app.get("/api/conferences/bookings", response_model=List[EmployeeConference])
async def get_all_bookings(db: AsyncSession = Depends(get_db)):
    """!
    @brief 获取所有会议预定记录。
    @param db 数据库会话。
    @return List[EmployeeConference] 所有预定记录列表。
    """
    from sqlalchemy import select
    result = await db.execute(select(EmployeeConferenceDB).order_by(EmployeeConferenceDB.conference_id))
    bookings = result.scalars().all()
    return [booking.to_pydantic() for booking in bookings]

@app.delete("/api/conferences/{conference_id}/bookings/{employee_id}", response_model=dict)
async def cancel_booking(conference_id: int, employee_id: int, db: AsyncSession = Depends(get_db)):
    """!
    @brief 取消员工的会议预定。
    @param conference_id 会议 ID。
    @param employee_id 员工 ID。
    @param db 数据库会话。
    @return dict 包含成功消息的 dictionary。
    """
    # 检查预定记录是否存在
    from sqlalchemy import select
    query = select(EmployeeConferenceDB).where(
        EmployeeConferenceDB.conference_id == conference_id,
        EmployeeConferenceDB.employee_id == employee_id
    )
    result = await db.execute(query)
    booking = result.scalar_one_or_none()
    
    if booking is None:
        raise HTTPException(status_code=404, detail="Booking not found")

    await db.delete(booking)
    await db.commit()
    return {"message": f"Booking cancelled successfully"}
