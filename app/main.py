"""!
@file main.py
@brief 主 FastAPI 应用文件，用于管理会议。
@details 提供 API 端点来获取会议列表、添加新会议，提供前端页面。
@date 2025.5.25
"""

import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.core.config import APP_TITLE, APP_DESCRIPTION
from app.models.database import engine, Base
from app.api import conference, employee, booking

# FastAPI 实例
app = FastAPI(title=APP_TITLE, description=APP_DESCRIPTION)

# 挂载静态文件目录
app.mount("/static", StaticFiles(directory="static"), name="static")

# 配置模板目录
templates = Jinja2Templates(directory="templates")

# 注册路由
app.include_router(conference.router, prefix="/api/conferences", tags=["conferences"])
app.include_router(employee.router, prefix="/api/employees", tags=["employees"])
app.include_router(booking.router, prefix="/api", tags=["bookings"])

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """!
    @brief 提供前端 HTML 页面。
    @param request FastAPI 的请求对象。
    @return HTMLResponse 渲染后的 index.html 页面。
    """
    return templates.TemplateResponse("index.html", {"request": request})

@app.on_event("startup")
async def startup_event():
    """!
    @brief 应用启动时执行的事件。
    @details 创建数据库表（如果不存在）。
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("数据库表已初始化。") 