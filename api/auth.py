"""
API JWT认证模块
提供基于JWT的API认证功能
"""
import jwt
import datetime
from functools import wraps
from flask import request, jsonify, current_app
import config
import logging

logger = logging.getLogger(__name__)

# JWT配置
JWT_SECRET = config.SECRET_KEY
JWT_ALGORITHM = 'HS256'
JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(hours=1)  # 访问令牌1小时
JWT_REFRESH_TOKEN_EXPIRES = datetime.timedelta(days=7)  # 刷新令牌7天


def generate_access_token(user_id, username, role):
    """
    生成访问令牌
    
    Args:
        user_id: 用户ID
        username: 用户名
        role: 用户角色
    
    Returns:
        str: JWT令牌
    """
    payload = {
        'user_id': user_id,
        'username': username,
        'role': role,
        'type': 'access',
        'exp': datetime.datetime.utcnow() + JWT_ACCESS_TOKEN_EXPIRES,
        'iat': datetime.datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def generate_refresh_token(user_id):
    """
    生成刷新令牌
    
    Args:
        user_id: 用户ID
    
    Returns:
        str: JWT刷新令牌
    """
    payload = {
        'user_id': user_id,
        'type': 'refresh',
        'exp': datetime.datetime.utcnow() + JWT_REFRESH_TOKEN_EXPIRES,
        'iat': datetime.datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def verify_token(token, token_type='access'):
    """
    验证JWT令牌
    
    Args:
        token: JWT令牌
        token_type: 令牌类型 ('access' 或 'refresh')
    
    Returns:
        dict: 解码后的payload，验证失败返回None
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        
        # 验证令牌类型
        if payload.get('type') != token_type:
            logger.warning(f"令牌类型不匹配: 期望{token_type}, 实际{payload.get('type')}")
            return None
        
        return payload
    
    except jwt.ExpiredSignatureError:
        logger.warning("JWT令牌已过期")
        return None
    except jwt.InvalidTokenError as e:
        logger.warning(f"无效的JWT令牌: {e}")
        return None


def token_required(f):
    """
    API路由装饰器：要求有效的JWT令牌
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # 从Authorization头获取令牌
        auth_header = request.headers.get('Authorization')
        if auth_header:
            try:
                # 格式: "Bearer <token>"
                token = auth_header.split(' ')[1]
            except IndexError:
                return jsonify({
                    'success': False,
                    'message': 'Authorization头格式错误，应为: Bearer <token>'
                }), 401
        
        if not token:
            return jsonify({
                'success': False,
                'message': '缺少认证令牌'
            }), 401
        
        # 验证令牌
        payload = verify_token(token, 'access')
        if not payload:
            return jsonify({
                'success': False,
                'message': '无效或已过期的令牌'
            }), 401
        
        # 将用户信息添加到request对象
        request.current_user = {
            'user_id': payload['user_id'],
            'username': payload['username'],
            'role': payload['role']
        }
        
        return f(*args, **kwargs)
    
    return decorated


def admin_required(f):
    """
    API路由装饰器：要求管理员权限
    """
    @wraps(f)
    @token_required
    def decorated(*args, **kwargs):
        if request.current_user.get('role') != 'admin':
            return jsonify({
                'success': False,
                'message': '需要管理员权限'
            }), 403
        
        return f(*args, **kwargs)
    
    return decorated


def get_current_user():
    """
    获取当前认证用户信息
    
    Returns:
        dict: 用户信息，未认证返回None
    """
    return getattr(request, 'current_user', None)

