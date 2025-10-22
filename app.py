from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_wtf.csrf import CSRFError
import mysql.connector
from mysql.connector import errorcode
from config import config
import csv
from io import StringIO
import decimal
import json
from datetime import datetime, date
import traceback

# Import core utilities
from core.utils import get_db_connection, make_json_safe
from core.logger import setup_logger
from core.extensions import csrf, limiter, init_extensions

# Import Blueprints
from blueprints.projects import projects_bp
from blueprints.materials import materials_bp
from blueprints.fillers import fillers_bp
from blueprints.formulas import formulas_bp
from blueprints.auth import auth_bp, login_required

app = Flask(__name__)
# 配置日志系统
logger = setup_logger(app)

# Flask和CSRF配置
app.secret_key = config.SECRET_KEY
app.config['SECRET_KEY'] = config.SECRET_KEY  # 确保Flask和扩展都能访问
app.config['WTF_CSRF_ENABLED'] = True
app.config['WTF_CSRF_TIME_LIMIT'] = None  # 禁用CSRF token过期，避免长时间页面停留导致的问题
app.config['PERMANENT_SESSION_LIFETIME'] = config.SESSION_LIFETIME
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # 防止 CSRF 攻击
app.config['SESSION_COOKIE_HTTPONLY'] = True  # 防止 XSS 攻击
app.config['SESSION_COOKIE_SECURE'] = False  # 开发环境使用HTTP
app.config['SESSION_COOKIE_NAME'] = 'session'  # 明确设置session cookie名称

# 调试信息：确认SECRET_KEY已加载
if len(config.SECRET_KEY) < 10:
    logger.error(f"⚠️ SECRET_KEY过短或未设置！当前长度: {len(config.SECRET_KEY)}")
else:
    logger.info(f"✓ SECRET_KEY已加载（长度: {len(config.SECRET_KEY)}）")

# 初始化所有扩展
init_extensions(app)
logger.info("CSRF 保护已启用")
logger.info("请求频率限制已启用")

# Register Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(projects_bp)
app.register_blueprint(materials_bp)
app.register_blueprint(fillers_bp)
app.register_blueprint(formulas_bp)
logger.info("所有 Blueprints 已注册")

@app.after_request
def set_security_headers(response):
    """设置安全响应头"""
    # 防止点击劫持
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    # 防止MIME类型嗅探
    response.headers['X-Content-Type-Options'] = 'nosniff'
    # XSS保护
    response.headers['X-XSS-Protection'] = '1; mode=block'
    # 内容安全策略 (CSP) - 允许CDN资源加载
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.bootcdn.net; "
        "style-src 'self' 'unsafe-inline' https://cdn.bootcdn.net; "
        "font-src 'self' data: https://cdn.bootcdn.net; "
        "img-src 'self' data: https:; "
        "connect-src 'self' https://cdn.bootcdn.net;"
    )
    # 引用来源策略
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    # 权限策略
    response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
    
    # 静态资源缓存策略 - 加速后续加载
    if request.path.startswith('/static/'):
        # 静态文件缓存1年
        response.headers['Cache-Control'] = 'public, max-age=31536000, immutable'
    elif request.endpoint and 'api' not in request.endpoint:
        # HTML页面缓存10分钟
        response.headers['Cache-Control'] = 'public, max-age=600'
    
    return response

@app.route('/')
@login_required
def index():
    """第一级: 导航页面。"""
    return render_template('index.html')

@app.route('/diagnostic')
def diagnostic():
    """系统诊断页面（无需登录）"""
    return render_template('diagnostic.html')

@app.route('/check_session')
def check_session():
    """检查Session是否有效"""
    if 'user_id' in session:
        return jsonify({
            'active': True,
            'user_id': session.get('user_id'),
            'username': session.get('username')
        })
    else:
        return jsonify({'active': False})

@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    """处理CSRF错误"""
    logger.warning(f"CSRF验证失败: {e.description}")
    return jsonify({
        'success': False,
        'message': 'CSRF验证失败，请刷新页面重试。',
        'error': 'csrf_error'
    }), 400

@app.errorhandler(429)
def ratelimit_handler(e):
    """处理请求频率限制"""
    logger.warning(f"请求频率超限: {request.remote_addr}")
    return jsonify({
        'success': False,
        'message': '请求过于频繁，请稍后再试。',
        'error': 'rate_limit_exceeded'
    }), 429

@app.errorhandler(404)
def not_found_error(error):
    """处理404错误"""
    logger.info(f"404错误: {request.url} from {request.remote_addr}")
    if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
        return jsonify({'success': False, 'message': '请求的资源不存在'}), 404
    return render_template('404.html'), 404

@app.errorhandler(403)
def forbidden_error(error):
    """处理403错误"""
    logger.warning(f"403错误: {request.url} from {request.remote_addr}")
    if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
        return jsonify({'success': False, 'message': '无权访问此资源'}), 403
    flash('您没有权限访问此资源', 'danger')
    return redirect(url_for('index'))

@app.errorhandler(500)
def internal_error(error):
    """处理500错误"""
    logger.error(f"500内部错误: {error}", exc_info=True)
    if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
        return jsonify({'success': False, 'message': '服务器内部错误，请稍后再试'}), 500
    return render_template('500.html'), 500

@app.errorhandler(Exception)
def handle_exception(e):
    """处理未捕获的异常"""
    logger.error(f"未捕获的异常: {e}", exc_info=True)
    if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
        return jsonify({'success': False, 'message': '发生错误，请稍后再试'}), 500
    return render_template('500.html'), 500

if __name__ == '__main__':
    # 使用配置文件中的设置
    # 生产环境应该使用 gunicorn 或 uwsgi 等 WSGI 服务器
    logger.info(f"启动应用服务器 - Host: {config.HOST}, Port: {config.PORT}, Debug: {config.DEBUG}")
    if config.DEBUG:
        logger.warning("⚠️  警告: Debug模式已开启，请勿在生产环境使用！")
    app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)
