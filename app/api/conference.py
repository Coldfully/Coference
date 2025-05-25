from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.database import get_db
from app.models.conference import ConferenceDB
from app.schemas.conference import Conference, ConferenceCreate, ConferenceUpdate

router = APIRouter()

@router.get("/", response_model=List[Conference])
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

@router.post("/", response_model=Conference, status_code=201)
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

@router.get("/{conference_id}", response_model=Conference)
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

@router.put("/{conference_id}", response_model=Conference)
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

    update_data = conference_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_conference, key, value)

    await db.commit()
    await db.refresh(db_conference)
    return db_conference.to_pydantic()

@router.delete("/{conference_id}", response_model=dict)
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