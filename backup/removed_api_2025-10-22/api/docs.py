"""
API文档生成模块
使用Swagger/OpenAPI规范
"""
from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from flask import jsonify
import json


# 创建API规范
spec = APISpec(
    title="化学配方管理系统 API",
    version="1.0.0",
    openapi_version="3.0.2",
    info=dict(
        description="前后端分离的RESTful API接口文档",
        contact=dict(
            name="API Support",
            email="support@example.com"
        ),
        license=dict(
            name="MIT",
            url="https://opensource.org/licenses/MIT"
        )
    ),
    servers=[
        dict(
            url="http://localhost:5000/api/v1",
            description="开发环境"
        ),
        dict(
            url="https://api.example.com/api/v1",
            description="生产环境"
        )
    ],
    plugins=[MarshmallowPlugin()],
)

# 添加安全方案
spec.components.security_scheme(
    "bearerAuth",
    {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT",
        "description": "JWT认证令牌，格式: Bearer <token>"
    }
)

# 定义通用响应模式
spec.components.schema(
    "SuccessResponse",
    {
        "type": "object",
        "properties": {
            "success": {"type": "boolean", "example": True},
            "data": {"type": "object"},
            "message": {"type": "string", "example": "操作成功"}
        }
    }
)

spec.components.schema(
    "ErrorResponse",
    {
        "type": "object",
        "properties": {
            "success": {"type": "boolean", "example": False},
            "message": {"type": "string", "example": "错误信息"}
        }
    }
)

# 用户登录请求
spec.components.schema(
    "LoginRequest",
    {
        "type": "object",
        "required": ["username", "password"],
        "properties": {
            "username": {"type": "string", "description": "用户名", "example": "admin"},
            "password": {"type": "string", "description": "密码", "example": "password123"}
        }
    }
)

# 用户登录响应
spec.components.schema(
    "LoginResponse",
    {
        "type": "object",
        "properties": {
            "success": {"type": "boolean", "example": True},
            "data": {
                "type": "object",
                "properties": {
                    "access_token": {"type": "string", "description": "访问令牌"},
                    "refresh_token": {"type": "string", "description": "刷新令牌"},
                    "user": {
                        "type": "object",
                        "properties": {
                            "user_id": {"type": "integer", "example": 1},
                            "username": {"type": "string", "example": "admin"},
                            "real_name": {"type": "string", "example": "管理员"},
                            "role": {"type": "string", "example": "admin"}
                        }
                    }
                }
            },
            "message": {"type": "string", "example": "登录成功"}
        }
    }
)

# 项目对象
spec.components.schema(
    "Project",
    {
        "type": "object",
        "properties": {
            "ProjectID": {"type": "integer", "example": 1},
            "ProjectName": {"type": "string", "example": "新型喷墨配方"},
            "FormulaCode": {"type": "string", "example": "ABC-21102025-INK-01"},
            "ProjectType_FK": {"type": "integer", "example": 1},
            "TypeName": {"type": "string", "example": "喷墨"},
            "FormulatorName": {"type": "string", "example": "张三"},
            "FormulationDate": {"type": "string", "format": "date", "example": "2025-10-21"},
            "SubstrateApplication": {"type": "string", "example": "纸张"},
            "CreatedAt": {"type": "string", "format": "date-time"}
        }
    }
)

# 项目列表响应
spec.components.schema(
    "ProjectListResponse",
    {
        "type": "object",
        "properties": {
            "success": {"type": "boolean", "example": True},
            "data": {
                "type": "object",
                "properties": {
                    "projects": {
                        "type": "array",
                        "items": {"$ref": "#/components/schemas/Project"}
                    },
                    "pagination": {
                        "type": "object",
                        "properties": {
                            "page": {"type": "integer", "example": 1},
                            "per_page": {"type": "integer", "example": 20},
                            "total": {"type": "integer", "example": 100},
                            "pages": {"type": "integer", "example": 5}
                        }
                    }
                }
            }
        }
    }
)

# 添加API端点文档

# ========== 认证API ==========
spec.path(
    path="/auth/login",
    operations={
        "post": {
            "tags": ["认证"],
            "summary": "用户登录",
            "description": "使用用户名和密码登录，返回JWT令牌",
            "requestBody": {
                "required": True,
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/LoginRequest"}
                    }
                }
            },
            "responses": {
                "200": {
                    "description": "登录成功",
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/LoginResponse"}
                        }
                    }
                },
                "401": {
                    "description": "认证失败",
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                        }
                    }
                }
            }
        }
    }
)

spec.path(
    path="/auth/refresh",
    operations={
        "post": {
            "tags": ["认证"],
            "summary": "刷新访问令牌",
            "description": "使用刷新令牌获取新的访问令牌",
            "requestBody": {
                "required": True,
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "required": ["refresh_token"],
                            "properties": {
                                "refresh_token": {"type": "string", "description": "刷新令牌"}
                            }
                        }
                    }
                }
            },
            "responses": {
                "200": {
                    "description": "刷新成功",
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "success": {"type": "boolean"},
                                    "data": {
                                        "type": "object",
                                        "properties": {
                                            "access_token": {"type": "string"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
)

spec.path(
    path="/auth/me",
    operations={
        "get": {
            "tags": ["认证"],
            "summary": "获取当前用户信息",
            "description": "获取当前认证用户的详细信息",
            "security": [{"bearerAuth": []}],
            "responses": {
                "200": {
                    "description": "成功",
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/SuccessResponse"}
                        }
                    }
                },
                "401": {
                    "description": "未认证",
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                        }
                    }
                }
            }
        }
    }
)

# ========== 项目API ==========
spec.path(
    path="/projects",
    operations={
        "get": {
            "tags": ["项目管理"],
            "summary": "获取项目列表",
            "description": "分页获取所有项目",
            "security": [{"bearerAuth": []}],
            "parameters": [
                {
                    "name": "page",
                    "in": "query",
                    "description": "页码",
                    "schema": {"type": "integer", "default": 1}
                },
                {
                    "name": "per_page",
                    "in": "query",
                    "description": "每页数量",
                    "schema": {"type": "integer", "default": 20, "maximum": 100}
                }
            ],
            "responses": {
                "200": {
                    "description": "成功",
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/ProjectListResponse"}
                        }
                    }
                }
            }
        },
        "post": {
            "tags": ["项目管理"],
            "summary": "创建新项目",
            "description": "创建一个新的化学配方项目",
            "security": [{"bearerAuth": []}],
            "requestBody": {
                "required": True,
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "required": ["project_name", "project_type_fk", "formulator_name", "formulation_date"],
                            "properties": {
                                "project_name": {"type": "string", "example": "新型喷墨配方"},
                                "project_type_fk": {"type": "integer", "example": 1},
                                "formulator_name": {"type": "string", "example": "张三"},
                                "formulation_date": {"type": "string", "format": "date", "example": "2025-10-21"},
                                "substrate_application": {"type": "string", "example": "纸张"}
                            }
                        }
                    }
                }
            },
            "responses": {
                "201": {
                    "description": "创建成功",
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/SuccessResponse"}
                        }
                    }
                }
            }
        }
    }
)

spec.path(
    path="/projects/{project_id}",
    operations={
        "get": {
            "tags": ["项目管理"],
            "summary": "获取项目详情",
            "description": "获取指定项目的详细信息，包括配方成分和测试结果",
            "security": [{"bearerAuth": []}],
            "parameters": [
                {
                    "name": "project_id",
                    "in": "path",
                    "required": True,
                    "description": "项目ID",
                    "schema": {"type": "integer"}
                }
            ],
            "responses": {
                "200": {
                    "description": "成功",
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/SuccessResponse"}
                        }
                    }
                },
                "404": {
                    "description": "项目不存在",
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                        }
                    }
                }
            }
        }
    }
)

# ========== 用户管理API ==========
spec.path(
    path="/users",
    operations={
        "get": {
            "tags": ["用户管理"],
            "summary": "获取用户列表",
            "description": "获取所有用户（管理员）",
            "security": [{"bearerAuth": []}],
            "responses": {
                "200": {
                    "description": "成功",
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/SuccessResponse"}
                        }
                    }
                },
                "403": {
                    "description": "权限不足",
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                        }
                    }
                }
            }
        }
    }
)

# ========== 健康检查 ==========
spec.path(
    path="/health",
    operations={
        "get": {
            "tags": ["系统"],
            "summary": "健康检查",
            "description": "检查API服务是否正常运行",
            "responses": {
                "200": {
                    "description": "服务正常",
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "success": {"type": "boolean"},
                                    "data": {
                                        "type": "object",
                                        "properties": {
                                            "status": {"type": "string", "example": "healthy"},
                                            "version": {"type": "string", "example": "1.0.0"},
                                            "timestamp": {"type": "string", "format": "date-time"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
)


def get_api_docs():
    """
    获取API文档（OpenAPI规范）
    
    Returns:
        dict: OpenAPI规范字典
    """
    return spec.to_dict()


def get_api_docs_json():
    """
    获取API文档JSON字符串
    
    Returns:
        str: OpenAPI规范JSON
    """
    return json.dumps(spec.to_dict(), indent=2, ensure_ascii=False)

