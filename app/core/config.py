"""!
@file config.py
@brief 应用程序配置文件
@details 包含数据库连接和应用基本配置信息
@date 2025.5.25
"""

import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 数据库配置
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./conference.db")

# 应用配置
APP_TITLE = "会议管理系统"
APP_DESCRIPTION = "简易的会议管理系统 API" 