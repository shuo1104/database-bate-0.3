# -*- coding: utf-8 -*-
"""
API测试脚本
快速测试后端API功能
"""

import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_health():
    """测试健康检查"""
    print("\n=== 测试健康检查 ===")
    response = requests.get("http://localhost:8000/health")
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    return response.status_code == 200


def test_register():
    """测试用户注册"""
    print("\n=== 测试用户注册 ===")
    data = {
        "username": "testuser",
        "password": "test123456",
        "real_name": "测试用户",
        "email": "test@example.com"
    }
    response = requests.post(f"{BASE_URL}/auth/register", json=data)
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    return response.status_code == 200


def test_login():
    """测试用户登录"""
    print("\n=== 测试用户登录 ===")
    data = {
        "username": "testuser",
        "password": "test123456"
    }
    response = requests.post(f"{BASE_URL}/auth/login", json=data)
    print(f"状态码: {response.status_code}")
    result = response.json()
    print(f"响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
    
    if response.status_code == 200 and result.get("success"):
        token = result["data"]["token"]["access_token"]
        print(f"\n✅ 登录成功! Access Token: {token[:50]}...")
        return token
    return None


def test_get_current_user(token):
    """测试获取当前用户信息"""
    print("\n=== 测试获取当前用户信息 ===")
    headers = {
        "Authorization": f"Bearer {token}"
    }
    response = requests.get(f"{BASE_URL}/auth/current/info", headers=headers)
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    return response.status_code == 200


def test_update_profile(token):
    """测试更新个人信息"""
    print("\n=== 测试更新个人信息 ===")
    headers = {
        "Authorization": f"Bearer {token}"
    }
    data = {
        "real_name": "测试用户（已修改）",
        "position": "研发工程师"
    }
    response = requests.put(f"{BASE_URL}/auth/current/profile", headers=headers, json=data)
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    return response.status_code == 200


def run_all_tests():
    """运行所有测试"""
    print("=" * 80)
    print("FastAPI 后端 API 测试")
    print("=" * 80)
    
    # 测试健康检查
    if not test_health():
        print("\n❌ 健康检查失败！请确保服务已启动。")
        return
    
    # 测试注册（如果用户已存在会失败，这是正常的）
    test_register()
    
    # 测试登录
    token = test_login()
    if not token:
        print("\n❌ 登录失败！")
        return
    
    # 测试获取用户信息
    if not test_get_current_user(token):
        print("\n❌ 获取用户信息失败！")
        return
    
    # 测试更新个人信息
    if not test_update_profile(token):
        print("\n❌ 更新个人信息失败！")
        return
    
    print("\n" + "=" * 80)
    print("✅ 所有测试通过！")
    print("=" * 80)


if __name__ == "__main__":
    try:
        run_all_tests()
    except requests.exceptions.ConnectionError:
        print("\n❌ 无法连接到服务器！")
        print("请先启动后端服务:")
        print("    python main.py run --env=dev")
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {e}")

