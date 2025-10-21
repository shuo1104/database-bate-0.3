"""
Pytest配置和共享fixtures
"""
import pytest
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app as flask_app
from config import DB_CONFIG


@pytest.fixture
def app():
    """创建Flask应用fixture"""
    flask_app.config.update({
        "TESTING": True,
        "WTF_CSRF_ENABLED": False,  # 测试时禁用CSRF
    })
    
    yield flask_app


@pytest.fixture
def client(app):
    """创建测试客户端"""
    return app.test_client()


@pytest.fixture
def runner(app):
    """创建CLI运行器"""
    return app.test_cli_runner()


@pytest.fixture
def auth_client(client):
    """
    创建已认证的测试客户端
    需要先有测试用户存在于数据库中
    """
    # 这里应该登录一个测试用户
    # 实际实现需要根据你的认证逻辑
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['username'] = 'test_user'
        sess['user_role'] = 'admin'
    
    return client


@pytest.fixture
def mock_db_connection(mocker):
    """模拟数据库连接"""
    mock_conn = mocker.MagicMock()
    mock_cursor = mocker.MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    
    return mock_conn, mock_cursor

