from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.database import get_db
from app.models.employee import EmployeeDB
from app.schemas.employee import Employee, EmployeeCreate, EmployeeUpdate

router = APIRouter()

@router.get("/", response_model=List[Employee])
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

@router.post("/", response_model=Employee, status_code=201)
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

@router.get("/{employee_id}", response_model=Employee)
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

@router.put("/{employee_id}", response_model=Employee)
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

@router.delete("/{employee_id}", response_model=dict)
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