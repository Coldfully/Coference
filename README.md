# 会议管理系统

一个基于 FastAPI 的简易会议管理系统，提供会议管理、员工管理和会议预定三个功能。

## 功能简述

- 会议管理：创建、查询、更新和删除会议
- 员工管理：创建、查询、更新和删除员工信息
- 与会人员查询：查看会议的所有与会人员
- RESTful API：提供完整的 RESTful API 接口
- 异步支持：使用异步数据库操作，提高性能
- 数据验证：使用 Pydantic 进行数据验证
- 文档支持：自动生成 API 文档

## 技术栈

- FastAPI：Web 框架
- SQLAlchemy：ORM 框架
- Pydantic：数据验证
- SQLite/MySQL：数据库
- Jinja2：模板引擎

## 项目结构

```
conference/
├── app/
│   ├── __init__.py
│   ├── main.py              # 主应用文件
│   ├── models/              # 数据库模型
│   │   ├── __init__.py
│   │   ├── database.py      # 数据库配置
│   │   ├── conference.py    # 会议模型
│   │   ├── employee.py      # 员工模型
│   │   └── booking.py       # 预定模型
│   ├── schemas/             # Pydantic 模型
│   │   ├── __init__.py
│   │   ├── conference.py    # 会议模式
│   │   ├── employee.py      # 员工模式
│   │   └── booking.py       # 预定模式
│   ├── api/                 # API 路由
│   │   ├── __init__.py
│   │   ├── conference.py    # 会议路由
│   │   ├── employee.py      # 员工路由
│   │   └── booking.py       # 预定路由
│   └── core/                # 核心配置
│       ├── __init__.py
│       └── config.py        # 配置文件
├── static/                  # 静态文件
├── templates/               # 模板文件
├── source/                  # 资源文件
│   └── bg.png              # 系统背景图片
└── requirements.txt         # 依赖文件
```

## 安装步骤

1. 克隆项目：
```bash
git clone https://github.com/Coldfully/Coference.git
cd conference
```

2. 创建虚拟环境：
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. 安装依赖：
```bash
pip install -r requirements.txt
```

4. 配置环境变量：
创建 `.env` 文件并设置数据库连接：
```
DATABASE_URL=sqlite+aiosqlite:///./conference.db
```

## 运行项目

1. 启动服务器：
```bash
uvicorn app.main:app --reload
```

2. 访问 API 文档：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API 端点

### 会议管理
- `GET /api/conferences` - 获取所有会议
- `POST /api/conferences` - 创建新会议
- `GET /api/conferences/{id}` - 获取指定会议
- `PUT /api/conferences/{id}` - 更新会议
- `DELETE /api/conferences/{id}` - 删除会议

### 员工管理
- `GET /api/employees` - 获取所有员工
- `POST /api/employees` - 创建新员工
- `GET /api/employees/{id}` - 获取指定员工
- `PUT /api/employees/{id}` - 更新员工
- `DELETE /api/employees/{id}` - 删除员工

### 会议预定
- `POST /api/conferences/{id}/book` - 预定会议
- `GET /api/employees/{id}/conferences` - 获取员工的预定会议
- `GET /api/conferences/{id}/attendees` - 获取会议与会人员
- `GET /api/conferences/bookings` - 获取所有预定记录
- `DELETE /api/conferences/{id}/bookings/{employee_id}` - 取消预定

## 开发说明

### 数据库模型

- `ConferenceDB`: 会议信息
- `EmployeeDB`: 员工信息
- `EmployeeConferenceDB`: 员工-会议关联
- `ConferenceBookingDB`: 会议预定记录

### 数据验证

使用 Pydantic 模型进行数据验证：
- `ConferenceBase`: 会议基础模型
- `EmployeeBase`: 员工基础模型
- `ConferenceBookingBase`: 预定基础模型

## 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 联系方式

如有问题或建议，请提交 Issue 或 Pull Request。 