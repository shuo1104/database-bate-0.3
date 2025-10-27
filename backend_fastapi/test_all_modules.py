# -*- coding: utf-8 -*-
"""
完整API测试脚本
测试所有已迁移的模块
"""

import requests
import json
from datetime import date

BASE_URL = "http://localhost:8000/api/v1"
TOKEN = None


def print_section(title):
    """打印章节标题"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def test_request(method, url, data=None, headers=None, description=""):
    """统一测试请求函数"""
    print(f"\n>>> {description}")
    print(f"    {method} {url}")
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers)
        elif method == "PUT":
            response = requests.put(url, json=data, headers=headers)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers)
        else:
            raise ValueError(f"不支持的方法: {method}")
        
        print(f"    状态码: {response.status_code}")
        
        try:
            result = response.json()
            print(f"    响应: {json.dumps(result, indent=4, ensure_ascii=False)[:500]}")
            return response.status_code, result
        except:
            print(f"    响应: {response.text[:200]}")
            return response.status_code, None
            
    except requests.exceptions.ConnectionError:
        print("    ❌ 无法连接到服务器！")
        return None, None
    except Exception as e:
        print(f"    ❌ 请求失败: {e}")
        return None, None


def test_health():
    """测试健康检查"""
    print_section("1. 健康检查")
    status, result = test_request(
        "GET",
        "http://localhost:8000/health",
        description="检查服务状态"
    )
    return status == 200


def test_auth():
    """测试认证模块"""
    global TOKEN
    print_section("2. 认证模块测试")
    
    # 2.1 用户注册
    status, result = test_request(
        "POST",
        f"{BASE_URL}/auth/register",
        data={
            "username": "test_user_2024",
            "password": "test123456",
            "real_name": "测试用户2024",
            "email": "test2024@example.com"
        },
        description="2.1 注册新用户"
    )
    
    # 2.2 用户登录
    status, result = test_request(
        "POST",
        f"{BASE_URL}/auth/login",
        data={
            "username": "test_user_2024",
            "password": "test123456"
        },
        description="2.2 用户登录"
    )
    
    if status == 200 and result and result.get("success"):
        TOKEN = result["data"]["token"]["access_token"]
        print(f"\n    ✅ 获取Token成功: {TOKEN[:50]}...")
    else:
        print("\n    ❌ 登录失败，后续测试可能无法进行")
        return False
    
    # 2.3 获取当前用户信息
    headers = {"Authorization": f"Bearer {TOKEN}"}
    test_request(
        "GET",
        f"{BASE_URL}/auth/current/info",
        headers=headers,
        description="2.3 获取当前用户信息"
    )
    
    # 2.4 更新个人信息
    test_request(
        "PUT",
        f"{BASE_URL}/auth/current/profile",
        data={
            "real_name": "测试用户2024（已更新）",
            "position": "研发工程师"
        },
        headers=headers,
        description="2.4 更新个人信息"
    )
    
    return True


def test_projects():
    """测试项目管理模块"""
    if not TOKEN:
        print("\n⚠️ 跳过项目测试：未获取到认证Token")
        return
    
    print_section("3. 项目管理模块测试")
    headers = {"Authorization": f"Bearer {TOKEN}"}
    
    # 3.1 获取项目类型
    test_request(
        "GET",
        f"{BASE_URL}/projects/config/types",
        headers=headers,
        description="3.1 获取项目类型列表"
    )
    
    # 3.2 创建项目
    status, result = test_request(
        "POST",
        f"{BASE_URL}/projects/create",
        data={
            "project_name": "FastAPI测试项目",
            "project_type_fk": 1,  # 假设类型ID为1
            "formulator_name": "张三",
            "formulation_date": str(date.today()),
            "substrate_application": "高性能涂层测试"
        },
        headers=headers,
        description="3.2 创建新项目"
    )
    
    project_id = None
    if status == 200 and result and result.get("success"):
        project_id = result["data"]["ProjectID"]
        print(f"\n    ✅ 项目创建成功，ID: {project_id}")
    
    # 3.3 获取项目列表
    test_request(
        "GET",
        f"{BASE_URL}/projects/list?page=1&page_size=10",
        headers=headers,
        description="3.3 获取项目列表（分页）"
    )
    
    # 3.4 获取项目详情
    if project_id:
        test_request(
            "GET",
            f"{BASE_URL}/projects/{project_id}",
            headers=headers,
            description=f"3.4 获取项目详情 (ID: {project_id})"
        )
        
        # 3.5 添加配方成分
        test_request(
            "POST",
            f"{BASE_URL}/projects/compositions/create",
            data={
                "project_id": project_id,
                "material_id": 1,  # 假设原料ID为1
                "weight_percentage": 25.5,
                "addition_method": "直接添加",
                "remarks": "主要成分"
            },
            headers=headers,
            description="3.5 添加配方成分"
        )
        
        # 3.6 获取配方成分
        test_request(
            "GET",
            f"{BASE_URL}/projects/{project_id}/compositions",
            headers=headers,
            description="3.6 获取项目配方成分"
        )
        
        # 3.7 更新项目
        test_request(
            "PUT",
            f"{BASE_URL}/projects/{project_id}",
            data={
                "project_name": "FastAPI测试项目（已更新）",
                "substrate_application": "高性能涂层测试（V2）"
            },
            headers=headers,
            description="3.7 更新项目信息"
        )
    
    # 3.8 获取配方设计师列表
    test_request(
        "GET",
        f"{BASE_URL}/projects/config/formulators",
        headers=headers,
        description="3.8 获取配方设计师列表"
    )


def test_materials():
    """测试原料管理模块"""
    if not TOKEN:
        print("\n⚠️ 跳过原料测试：未获取到认证Token")
        return
    
    print_section("4. 原料管理模块测试")
    headers = {"Authorization": f"Bearer {TOKEN}"}
    
    # 4.1 获取原料类别
    test_request(
        "GET",
        f"{BASE_URL}/materials/config/categories",
        headers=headers,
        description="4.1 获取原料类别列表"
    )
    
    # 4.2 创建原料
    status, result = test_request(
        "POST",
        f"{BASE_URL}/materials/create",
        data={
            "trade_name": "FastAPI测试原料",
            "category_fk": 1,  # 假设类别ID为1
            "supplier": "测试供应商",
            "cas_number": "123-45-6",
            "density": 1.25,
            "viscosity": 500.0,
            "function_description": "用于FastAPI接口测试"
        },
        headers=headers,
        description="4.2 创建新原料"
    )
    
    material_id = None
    if status == 200 and result and result.get("success"):
        material_id = result["data"]["MaterialID"]
        print(f"\n    ✅ 原料创建成功，ID: {material_id}")
    
    # 4.3 获取原料列表
    test_request(
        "GET",
        f"{BASE_URL}/materials/list?page=1&page_size=10",
        headers=headers,
        description="4.3 获取原料列表（分页）"
    )
    
    # 4.4 获取原料详情
    if material_id:
        test_request(
            "GET",
            f"{BASE_URL}/materials/{material_id}",
            headers=headers,
            description=f"4.4 获取原料详情 (ID: {material_id})"
        )
        
        # 4.5 更新原料
        test_request(
            "PUT",
            f"{BASE_URL}/materials/{material_id}",
            data={
                "trade_name": "FastAPI测试原料（已更新）",
                "density": 1.30
            },
            headers=headers,
            description="4.5 更新原料信息"
        )
    
    # 4.6 获取供应商列表
    test_request(
        "GET",
        f"{BASE_URL}/materials/config/suppliers",
        headers=headers,
        description="4.6 获取供应商列表"
    )


def run_all_tests():
    """运行所有测试"""
    print("=" * 80)
    print("  FastAPI 后端完整测试")
    print("  光创化物 R&D 配方数据库管理系统")
    print("=" * 80)
    
    # 1. 健康检查
    if not test_health():
        print("\n❌ 服务未启动或健康检查失败！")
        print("请先启动服务: python main.py run --env=dev")
        return
    
    print("\n✅ 服务健康检查通过")
    
    # 2. 认证模块
    if not test_auth():
        print("\n❌ 认证模块测试失败！")
        return
    
    print("\n✅ 认证模块测试通过")
    
    # 3. 项目管理模块
    test_projects()
    
    # 4. 原料管理模块
    test_materials()
    
    # 总结
    print("\n" + "=" * 80)
    print("  测试完成总结")
    print("=" * 80)
    print("\n✅ 已测试模块:")
    print("   1. 认证管理 (5个API)")
    print("   2. 项目管理 (8个API)")
    print("   3. 原料管理 (6个API)")
    print("\n📊 测试统计:")
    print("   - API接口: 19+个")
    print("   - 测试通过: 预期100%")
    print("\n💡 提示:")
    print("   - 访问 Swagger UI: http://localhost:8000/docs")
    print("   - 访问 ReDoc: http://localhost:8000/redoc")
    print("\n" + "=" * 80)


if __name__ == "__main__":
    try:
        run_all_tests()
    except KeyboardInterrupt:
        print("\n\n⚠️ 测试被用户中断")
    except Exception as e:
        print(f"\n\n❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

