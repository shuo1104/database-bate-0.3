# Flask → FastAPI 迁移指南

**光创化物 R&D 配方数据库管理系统后端迁移文档**

---

## 📊 迁移概览

### **已完成的工作** ✅

1. **项目结构搭建**
   - ✅ 创建了完整的FastAPI项目目录结构
   - ✅ 采用标准的分层架构 (Model/Schema/CRUD/Service/Controller)
   - ✅ 模块化设计，易于扩展

2. **核心基础设施**
   - ✅ 配置管理系统 (`app/config/settings.py`)
   - ✅ 异步数据库引擎 (SQLAlchemy 2.0)
   - ✅ 日志系统 (文件轮转 + 控制台)
   - ✅ 统一响应封装
   - ✅ 全局异常处理

3. **认证系统**
   - ✅ JWT认证 (Access + Refresh Token)
   - ✅ 密码Bcrypt加密
   - ✅ 用户CRUD操作
   - ✅ 完整的认证API

4. **中间件**
   - ✅ CORS中间件
   - ✅ 请求日志中间件
   - ✅ 认证中间件（可选）

### **待完成的工作** 🚧

1. **数据模型迁移**
   - [ ] 项目信息表 (`tbl_ProjectInfo`)
   - [ ] 原料表 (`tbl_RawMaterials`)
   - [ ] 填料表 (`tbl_InorganicFillers`)
   - [ ] 配方成分表 (`tbl_FormulaComposition`)
   - [ ] 测试结果表 (4张表)
   - [ ] 配置表 (3张表)

2. **业务模块迁移**
   - [ ] 项目管理模块
   - [ ] 原料管理模块
   - [ ] 填料管理模块
   - [ ] 配方管理模块

3. **高级功能**
   - [ ] 分页查询
   - [ ] 数据导出 (CSV/Excel)
   - [ ] 批量操作
   - [ ] 文件上传

---

## 🔄 架构对比

### **Flask (旧架构)**

```
app.py
├── Flask(__name__)
├── Blueprint (projects, materials, fillers, formulas, auth)
└── 原生 mysql-connector 操作数据库

认证: Session + Cookie
响应: jsonify(...)
路由: @blueprint.route('/path')
```

### **FastAPI (新架构)**

```
main.py
└── create_app()
    ├── register_middlewares()
    ├── register_exceptions()
    └── register_routers()
        └── api/v1/
            └── modules/
                └── module_name/
                    ├── model.py (ORM)
                    ├── schema.py (Pydantic)
                    ├── crud.py (数据访问)
                    ├── service.py (业务逻辑)
                    └── controller.py (路由)

认证: JWT (Access + Refresh Token)
响应: SuccessResponse(data=...)
路由: @router.get('/path')
```

---

## 📝 代码迁移示例

### **1. Flask Blueprint → FastAPI Router**

**Flask (旧)**:
```python
# blueprints/materials.py
from flask import Blueprint, request, jsonify

materials_bp = Blueprint('materials', __name__)

@materials_bp.route('/materials', methods=['GET'])
@login_required
def material_list():
    cnx = get_db_connection()
    cursor = cnx.cursor(dictionary=True)
    cursor.execute("SELECT * FROM tbl_RawMaterials")
    materials = cursor.fetchall()
    cursor.close()
    cnx.close()
    return jsonify(materials)
```

**FastAPI (新)**:
```python
# app/api/v1/modules/materials/controller.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user_id
from app.common.response import SuccessResponse
from .service import MaterialService

router = APIRouter()

@router.get("/list", summary="获取原料列表")
async def get_material_list(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """获取所有原料"""
    result = await MaterialService.get_all(db)
    return SuccessResponse(data=result, msg="查询成功")
```

### **2. Session认证 → JWT认证**

**Flask (旧)**:
```python
from flask import session

# 登录
session['user_id'] = user.UserID
session['username'] = user.Username

# 验证
@login_required
def some_route():
    user_id = session['user_id']
```

**FastAPI (新)**:
```python
from app.core.security import create_access_token, get_current_user_id

# 登录
token_data = {"user_id": user.UserID, "username": user.Username}
access_token = create_access_token(token_data)
return {"access_token": access_token}

# 验证
@router.get("/protected")
async def some_route(user_id: int = Depends(get_current_user_id)):
    pass
```

### **3. 数据库操作**

**Flask (旧)**:
```python
cnx = get_db_connection()
cursor = cnx.cursor(dictionary=True)
cursor.execute("SELECT * FROM tbl_Users WHERE UserID = %s", (user_id,))
user = cursor.fetchone()
cursor.close()
cnx.close()
```

**FastAPI (新)**:
```python
from sqlalchemy import select
from app.core.database import get_db

async def get_user(db: AsyncSession, user_id: int):
    stmt = select(UserModel).where(UserModel.UserID == user_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()
```

---

## 🚀 启动和测试

### **启动后端服务**

```bash
cd backend_fastapi

# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置数据库（编辑 env/.env.dev）
# DB_HOST=localhost
# DB_USER=root
# DB_PASSWORD=your_password

# 3. 启动服务
python main.py run --env=dev
```

### **测试API**

```bash
# 方式1: 使用Swagger UI
打开浏览器访问: http://localhost:8000/docs

# 方式2: 使用测试脚本
python test_api.py

# 方式3: 使用curl
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

---

## 📚 下一步开发指南

### **步骤1: 创建数据模型**

参考 `app/api/v1/modules/auth/model.py`

```python
from app.core.database import Base
from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column

class MaterialModel(Base):
    __tablename__ = "tbl_RawMaterials"
    
    MaterialID: Mapped[int] = mapped_column(Integer, primary_key=True)
    TradeName: Mapped[str] = mapped_column(String(255))
    # ... 其他字段
```

### **步骤2: 创建Schema**

参考 `app/api/v1/modules/auth/schema.py`

```python
from pydantic import BaseModel, Field

class MaterialCreateRequest(BaseModel):
    trade_name: str = Field(..., max_length=255)
    category_id: Optional[int] = None
    # ... 其他字段
```

### **步骤3: 创建CRUD**

参考 `app/api/v1/modules/auth/crud.py`

```python
class MaterialCRUD:
    @staticmethod
    async def get_all(db: AsyncSession):
        stmt = select(MaterialModel)
        result = await db.execute(stmt)
        return result.scalars().all()
```

### **步骤4: 创建Service**

参考 `app/api/v1/modules/auth/service.py`

```python
class MaterialService:
    @staticmethod
    async def get_all(db: AsyncSession):
        materials = await MaterialCRUD.get_all(db)
        return [MaterialResponse.model_validate(m) for m in materials]
```

### **步骤5: 创建Controller**

参考 `app/api/v1/modules/auth/controller.py`

```python
router = APIRouter()

@router.get("/list")
async def list_materials(db: AsyncSession = Depends(get_db)):
    result = await MaterialService.get_all(db)
    return SuccessResponse(data=result)
```

### **步骤6: 注册路由**

在 `app/api/v1/__init__.py` 中:

```python
from app.api.v1.modules.materials.controller import router as materials_router
api_router.include_router(materials_router, prefix="/materials", tags=["原料管理"])
```

---

## ⚠️ 注意事项

### **数据库字段命名**

- 原表使用大写驼峰 (`UserID`, `TradeName`)
- Pydantic模型使用小写下划线 (`user_id`, `trade_name`)
- 使用 `alias` 和 `populate_by_name` 实现映射

### **异步编程**

- 所有数据库操作必须使用 `await`
- 路由函数必须声明为 `async def`
- 使用 `AsyncSession` 而非同步Session

### **依赖注入**

- 数据库会话: `db: AsyncSession = Depends(get_db)`
- 当前用户: `user_id: int = Depends(get_current_user_id)`

---

## 🎯 迁移优先级

1. **高优先级** (核心功能)
   - [x] 用户认证模块
   - [ ] 项目管理模块
   - [ ] 配方管理模块

2. **中优先级** (基础数据)
   - [ ] 原料管理模块
   - [ ] 填料管理模块

3. **低优先级** (辅助功能)
   - [ ] 数据导出
   - [ ] 批量操作
   - [ ] 高级搜索

---

## 🤝 需要帮助？

如有问题，请查看:
- 📖 README.md - 项目概览
- 📖 本文档 - 迁移指南
- 📖 代码注释 - 详细说明
- 📖 Swagger文档 - http://localhost:8000/docs

---

**文档版本**: 1.0  
**最后更新**: 2025-10-24  
**维护团队**: 光创化物 R&D

