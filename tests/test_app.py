"""
测试Flask应用基础功能
"""
import pytest


class TestAppConfiguration:
    """测试应用配置"""
    
    def test_app_exists(self, app):
        """测试应用存在"""
        assert app is not None
    
    def test_app_is_testing(self, app):
        """测试应用处于测试模式"""
        assert app.config['TESTING'] is True
    
    def test_csrf_disabled_in_testing(self, app):
        """测试模式下CSRF已禁用"""
        assert app.config['WTF_CSRF_ENABLED'] is False


class TestRoutes:
    """测试路由"""
    
    def test_index_redirect_when_not_logged_in(self, client):
        """测试未登录时访问首页会重定向"""
        response = client.get('/')
        assert response.status_code == 302  # Redirect
        assert '/login' in response.location
    
    def test_login_page_accessible(self, client):
        """测试登录页面可访问"""
        response = client.get('/login')
        assert response.status_code == 200
    
    def test_diagnostic_page_accessible(self, client):
        """测试诊断页面可访问（无需登录）"""
        response = client.get('/diagnostic')
        assert response.status_code == 200


class TestErrorHandlers:
    """测试错误处理器"""
    
    def test_404_handler(self, client):
        """测试404错误处理"""
        response = client.get('/nonexistent-page')
        assert response.status_code == 404
    
    def test_404_returns_html(self, client):
        """测试404返回HTML"""
        response = client.get('/nonexistent-page')
        assert b'404' in response.data or response.status_code == 404
    
    def test_404_json_response(self, client):
        """测试404的JSON响应"""
        response = client.get(
            '/nonexistent-page',
            headers={'Accept': 'application/json'}
        )
        assert response.status_code == 404


class TestSecurityHeaders:
    """测试安全响应头"""
    
    def test_security_headers_present(self, client):
        """测试安全头是否存在"""
        response = client.get('/login')
        
        # 检查关键安全头
        assert 'X-Frame-Options' in response.headers
        assert 'X-Content-Type-Options' in response.headers
        assert 'X-XSS-Protection' in response.headers
        assert 'Content-Security-Policy' in response.headers
        assert 'Referrer-Policy' in response.headers
    
    def test_xframe_options_value(self, client):
        """测试X-Frame-Options值"""
        response = client.get('/login')
        assert response.headers['X-Frame-Options'] == 'SAMEORIGIN'
    
    def test_content_type_options_value(self, client):
        """测试X-Content-Type-Options值"""
        response = client.get('/login')
        assert response.headers['X-Content-Type-Options'] == 'nosniff'


class TestSessionManagement:
    """测试Session管理"""
    
    def test_check_session_no_session(self, client):
        """测试无Session时的检查"""
        response = client.get('/check_session')
        assert response.status_code == 200
        data = response.get_json()
        assert data['active'] is False
    
    def test_check_session_with_session(self, auth_client):
        """测试有Session时的检查"""
        response = auth_client.get('/check_session')
        assert response.status_code == 200
        data = response.get_json()
        assert data['active'] is True
        assert 'user_id' in data
        assert 'username' in data

