# API 使用指南

## 📖 概述

化学配方管理系统提供完整的RESTful API接口，支持前后端分离架构。

**Base URL**: `http://localhost:5000/api/v1`

**认证方式**: JWT Bearer Token

**数据格式**: JSON

---

## 🚀 快速开始

### 1. API文档

访问 Swagger UI 在线文档：
```
http://localhost:5000/api/docs/swagger
```

获取 OpenAPI 规范（JSON）：
```
http://localhost:5000/api/docs
```

### 2. 认证流程

```javascript
// 1. 登录获取令牌
const loginResponse = await fetch('http://localhost:5000/api/v1/auth/login', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        username: 'admin',
        password: 'password123'
    })
});

const { data } = await loginResponse.json();
const accessToken = data.access_token;
const refreshToken = data.refresh_token;

// 2. 使用令牌访问API
const projectsResponse = await fetch('http://localhost:5000/api/v1/projects', {
    headers: {
        'Authorization': `Bearer ${accessToken}`
    }
});

const projects = await projectsResponse.json();
```

---

## 🔐 认证API

### POST /auth/login
用户登录，获取JWT令牌

**请求**:
```json
{
    "username": "admin",
    "password": "password123"
}
```

**响应 200**:
```json
{
    "success": true,
    "data": {
        "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
        "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
        "user": {
            "user_id": 1,
            "username": "admin",
            "real_name": "管理员",
            "position": "系统管理员",
            "role": "admin"
        }
    },
    "message": "登录成功"
}
```

**响应 401**:
```json
{
    "success": false,
    "message": "用户名或密码错误"
}
```

---

### POST /auth/refresh
刷新访问令牌

**请求**:
```json
{
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**响应 200**:
```json
{
    "success": true,
    "data": {
        "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
    },
    "message": "令牌刷新成功"
}
```

---

### GET /auth/me
获取当前用户信息

**Headers**: `Authorization: Bearer <token>`

**响应 200**:
```json
{
    "success": true,
    "data": {
        "user": {
            "UserID": 1,
            "Username": "admin",
            "RealName": "管理员",
            "Position": "系统管理员",
            "Role": "admin",
            "Email": "admin@example.com",
            "CreatedAt": "2025-10-21T10:00:00",
            "LastLogin": "2025-10-21T15:30:00"
        }
    }
}
```

---

## 📊 项目管理API

### GET /projects
获取项目列表（分页）

**Headers**: `Authorization: Bearer <token>`

**Query Parameters**:
- `page` (int): 页码，默认1
- `per_page` (int): 每页数量，默认20，最大100

**示例**: `/api/v1/projects?page=1&per_page=20`

**响应 200**:
```json
{
    "success": true,
    "data": {
        "projects": [
            {
                "ProjectID": 1,
                "ProjectName": "新型喷墨配方",
                "FormulaCode": "ABC-21102025-INK-01",
                "ProjectType_FK": 1,
                "TypeName": "喷墨",
                "FormulatorName": "张三",
                "FormulationDate": "2025-10-21",
                "SubstrateApplication": "纸张",
                "CreatedAt": "2025-10-21T10:30:00"
            }
        ],
        "pagination": {
            "page": 1,
            "per_page": 20,
            "total": 100,
            "pages": 5
        }
    }
}
```

---

### GET /projects/{id}
获取单个项目详情

**Headers**: `Authorization: Bearer <token>`

**Path Parameters**:
- `id` (int): 项目ID

**示例**: `/api/v1/projects/1`

**响应 200**:
```json
{
    "success": true,
    "data": {
        "project": {
            "ProjectID": 1,
            "ProjectName": "新型喷墨配方",
            "FormulaCode": "ABC-21102025-INK-01",
            "FormulatorName": "张三",
            "FormulationDate": "2025-10-21"
        },
        "composition": [
            {
                "CompositionID": 1,
                "MaterialName": "丙烯酸树脂",
                "WeightPercentage": "45.50"
            }
        ],
        "test_results": {
            "TestID": 1,
            "Viscosity": "12.5",
            "Density": "1.05"
        }
    }
}
```

**响应 404**:
```json
{
    "success": false,
    "message": "项目不存在"
}
```

---

### POST /projects
创建新项目

**Headers**: 
- `Authorization: Bearer <token>`
- `Content-Type: application/json`

**请求**:
```json
{
    "project_name": "新型喷墨配方",
    "project_type_fk": 1,
    "formulator_name": "张三",
    "formulation_date": "2025-10-21",
    "substrate_application": "纸张"
}
```

**响应 201**:
```json
{
    "success": true,
    "data": {
        "project_id": 123,
        "formula_code": "ABC-21102025-INK-01"
    },
    "message": "项目创建成功"
}
```

**响应 400**:
```json
{
    "success": false,
    "message": "项目名称不能为空"
}
```

---

## 👥 用户管理API

### GET /users
获取用户列表（管理员）

**Headers**: `Authorization: Bearer <token>`

**权限**: 需要管理员权限

**响应 200**:
```json
{
    "success": true,
    "data": {
        "users": [
            {
                "UserID": 1,
                "Username": "admin",
                "RealName": "管理员",
                "Position": "系统管理员",
                "Role": "admin",
                "Email": "admin@example.com",
                "IsActive": 1,
                "CreatedAt": "2025-10-21T10:00:00",
                "LastLogin": "2025-10-21T15:30:00"
            }
        ]
    }
}
```

**响应 403**:
```json
{
    "success": false,
    "message": "需要管理员权限"
}
```

---

## 🏥 系统API

### GET /health
健康检查

**无需认证**

**响应 200**:
```json
{
    "success": true,
    "data": {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": "2025-10-21T15:30:00"
    }
}
```

---

## 💻 前端集成示例

### React + Axios

```javascript
// api.js - API配置
import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000/api/v1';

// 创建axios实例
const api = axios.create({
    baseURL: API_BASE_URL,
    timeout: 10000,
    headers: {
        'Content-Type': 'application/json'
    }
});

// 请求拦截器 - 添加令牌
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('access_token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// 响应拦截器 - 处理令牌过期
api.interceptors.response.use(
    (response) => response,
    async (error) => {
        const originalRequest = error.config;
        
        // 令牌过期，尝试刷新
        if (error.response?.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true;
            
            try {
                const refreshToken = localStorage.getItem('refresh_token');
                const { data } = await axios.post(
                    `${API_BASE_URL}/auth/refresh`,
                    { refresh_token: refreshToken }
                );
                
                localStorage.setItem('access_token', data.data.access_token);
                originalRequest.headers.Authorization = `Bearer ${data.data.access_token}`;
                
                return api(originalRequest);
            } catch (refreshError) {
                // 刷新失败，重定向到登录
                localStorage.removeItem('access_token');
                localStorage.removeItem('refresh_token');
                window.location.href = '/login';
                return Promise.reject(refreshError);
            }
        }
        
        return Promise.reject(error);
    }
);

export default api;
```

```javascript
// authService.js - 认证服务
import api from './api';

export const authService = {
    // 登录
    login: async (username, password) => {
        const { data } = await api.post('/auth/login', {
            username,
            password
        });
        
        if (data.success) {
            localStorage.setItem('access_token', data.data.access_token);
            localStorage.setItem('refresh_token', data.data.refresh_token);
            localStorage.setItem('user', JSON.stringify(data.data.user));
        }
        
        return data;
    },
    
    // 登出
    logout: () => {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');
    },
    
    // 获取当前用户
    getCurrentUser: async () => {
        const { data } = await api.get('/auth/me');
        return data.data.user;
    }
};
```

```javascript
// projectService.js - 项目服务
import api from './api';

export const projectService = {
    // 获取项目列表
    getProjects: async (page = 1, perPage = 20) => {
        const { data } = await api.get('/projects', {
            params: { page, per_page: perPage }
        });
        return data.data;
    },
    
    // 获取项目详情
    getProject: async (projectId) => {
        const { data } = await api.get(`/projects/${projectId}`);
        return data.data;
    },
    
    // 创建项目
    createProject: async (projectData) => {
        const { data } = await api.post('/projects', projectData);
        return data.data;
    }
};
```

```jsx
// ProjectList.jsx - 项目列表组件
import React, { useState, useEffect } from 'react';
import { projectService } from './services/projectService';

function ProjectList() {
    const [projects, setProjects] = useState([]);
    const [pagination, setPagination] = useState({});
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    
    useEffect(() => {
        loadProjects();
    }, []);
    
    const loadProjects = async (page = 1) => {
        try {
            setLoading(true);
            const data = await projectService.getProjects(page, 20);
            setProjects(data.projects);
            setPagination(data.pagination);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };
    
    if (loading) return <div>加载中...</div>;
    if (error) return <div>错误: {error}</div>;
    
    return (
        <div>
            <h2>项目列表</h2>
            <table>
                <thead>
                    <tr>
                        <th>配方编码</th>
                        <th>项目名称</th>
                        <th>类型</th>
                        <th>设计师</th>
                        <th>日期</th>
                    </tr>
                </thead>
                <tbody>
                    {projects.map(project => (
                        <tr key={project.ProjectID}>
                            <td>{project.FormulaCode}</td>
                            <td>{project.ProjectName}</td>
                            <td>{project.TypeName}</td>
                            <td>{project.FormulatorName}</td>
                            <td>{project.FormulationDate}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
            
            <div>
                <button 
                    onClick={() => loadProjects(pagination.page - 1)}
                    disabled={pagination.page === 1}
                >
                    上一页
                </button>
                <span>第 {pagination.page} / {pagination.pages} 页</span>
                <button 
                    onClick={() => loadProjects(pagination.page + 1)}
                    disabled={pagination.page === pagination.pages}
                >
                    下一页
                </button>
            </div>
        </div>
    );
}

export default ProjectList;
```

---

### Vue 3 + Composition API

```javascript
// api.js
import axios from 'axios';

const api = axios.create({
    baseURL: 'http://localhost:5000/api/v1',
    timeout: 10000
});

// 请求拦截器
api.interceptors.request.use((config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

export default api;
```

```vue
<template>
  <div>
    <h2>项目列表</h2>
    <div v-if="loading">加载中...</div>
    <div v-else-if="error">错误: {{ error }}</div>
    <table v-else>
      <thead>
        <tr>
          <th>配方编码</th>
          <th>项目名称</th>
          <th>类型</th>
          <th>设计师</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="project in projects" :key="project.ProjectID">
          <td>{{ project.FormulaCode }}</td>
          <td>{{ project.ProjectName }}</td>
          <td>{{ project.TypeName }}</td>
          <td>{{ project.FormulatorName }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from './api';

const projects = ref([]);
const loading = ref(true);
const error = ref(null);

const loadProjects = async () => {
    try {
        loading.value = true;
        const { data } = await api.get('/projects');
        projects.value = data.data.projects;
    } catch (err) {
        error.value = err.message;
    } finally {
        loading.value = false;
    }
};

onMounted(() => {
    loadProjects();
});
</script>
```

---

## 🔒 安全最佳实践

### 1. 令牌存储
```javascript
// ❌ 不推荐: 使用 localStorage（容易受XSS攻击）
localStorage.setItem('access_token', token);

// ✅ 推荐: 使用 httpOnly Cookie（后端设置）
// 或使用内存存储（刷新页面会丢失，需重新登录）
```

### 2. 令牌刷新
```javascript
// 在令牌即将过期前自动刷新
setInterval(async () => {
    const refreshToken = localStorage.getItem('refresh_token');
    const { data } = await api.post('/auth/refresh', { refresh_token: refreshToken });
    localStorage.setItem('access_token', data.data.access_token);
}, 50 * 60 * 1000); // 50分钟刷新一次（访问令牌1小时有效）
```

### 3. HTTPS
```javascript
// 生产环境必须使用HTTPS
const API_BASE_URL = process.env.NODE_ENV === 'production'
    ? 'https://api.yourdomain.com/api/v1'
    : 'http://localhost:5000/api/v1';
```

---

## 📝 错误处理

### 标准错误响应

所有错误响应遵循统一格式：

```json
{
    "success": false,
    "message": "错误描述信息"
}
```

### HTTP状态码

| 状态码 | 说明 |
|--------|------|
| 200 | 成功 |
| 201 | 创建成功 |
| 400 | 请求参数错误 |
| 401 | 未认证或令牌无效 |
| 403 | 权限不足 |
| 404 | 资源不存在 |
| 429 | 请求过于频繁 |
| 500 | 服务器内部错误 |

---

## 🧪 测试

### 使用 curl

```bash
# 登录
curl -X POST http://localhost:5000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "password123"}'

# 获取项目列表
curl -X GET http://localhost:5000/api/v1/projects \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# 创建项目
curl -X POST http://localhost:5000/api/v1/projects \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "project_name": "测试项目",
    "project_type_fk": 1,
    "formulator_name": "测试",
    "formulation_date": "2025-10-21"
  }'
```

### 使用 Postman

1. 创建新Collection "化学配方API"
2. 添加环境变量：
   - `base_url`: http://localhost:5000/api/v1
   - `access_token`: (自动更新)
3. 设置Collection级别的Authorization为Bearer Token
4. 创建请求并使用 `{{base_url}}` 和 `{{access_token}}`

---

## 📚 相关文档

- [README.md](README.md) - 项目文档
- [CHANGELOG.md](CHANGELOG.md) - 更新日志
- [Swagger UI](http://localhost:5000/api/docs/swagger) - 在线API文档

---

## 🆘 常见问题

### Q: 令牌过期怎么办？
A: 使用刷新令牌获取新的访问令牌，或重新登录。

### Q: CORS错误？
A: 确保前端域名已添加到 `.env` 的 `CORS_ORIGINS` 配置中。

### Q: 401错误？
A: 检查令牌是否有效，Header格式是否正确（`Authorization: Bearer <token>`）。

### Q: 如何测试API？
A: 访问 http://localhost:5000/api/docs/swagger 使用Swagger UI在线测试。

---

**版本**: 1.0.0  
**更新日期**: 2025-10-21

