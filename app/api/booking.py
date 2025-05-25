from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import join
from app.models.database import get_db
from app.models.booking import EmployeeConferenceDB, ConferenceBookingDB
from app.models.conference import ConferenceDB
from app.models.employee import EmployeeDB
from app.schemas.booking import EmployeeConference, ConferenceBooking, ConferenceBookingCreate
from app.schemas.conference import Conference
from app.schemas.employee import Employee

router = APIRouter()

@router.post("/conferences/{conference_id}/book", response_model=EmployeeConference, status_code=201)
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

@router.get("/employees/{employee_id}/conferences", response_model=List[Conference])
async def get_employee_conferences(employee_id: int, db: AsyncSession = Depends(get_db)):
    """!
    @brief 获取指定员工的所有预定会议。
    @param employee_id 员工 ID。
    @param db 数据库会话。
    @return List[Conference] 员工预定的所有会议列表。
    """
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

@router.get("/conferences/{conference_id}/attendees", response_model=List[Employee])
async def get_conference_attendees(conference_id: int, db: AsyncSession = Depends(get_db)):
    """!
    @brief 获取指定会议的所有与会人员。
    @param conference_id 会议 ID。
    @param db 数据库会话。
    @return List[Employee] 会议的所有与会人员列表。
    """
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

@router.get("/conferences/bookings", response_model=List[EmployeeConference])
async def get_all_bookings(db: AsyncSession = Depends(get_db)):
    """!
    @brief 获取所有会议预定记录。
    @param db 数据库会话。
    @return List[EmployeeConference] 所有预定记录列表。
    """
    result = await db.execute(select(EmployeeConferenceDB).order_by(EmployeeConferenceDB.conference_id))
    bookings = result.scalars().all()
    return [booking.to_pydantic() for booking in bookings]

@router.delete("/conferences/{conference_id}/bookings/{employee_id}", response_model=dict)
async def cancel_booking(conference_id: int, employee_id: int, db: AsyncSession = Depends(get_db)):
    """!
    @brief 取消员工的会议预定。
    @param conference_id 会议 ID。
    @param employee_id 员工 ID。
    @param db 数据库会话。
    @return dict 包含成功消息的 dictionary。
    """
    # 检查预定记录是否存在
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