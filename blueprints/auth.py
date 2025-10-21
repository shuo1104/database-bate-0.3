"""
用户认证蓝图
处理登录、登出、用户管理等功能
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify, current_app
import secrets
from functools import wraps
import mysql.connector
import logging
from datetime import datetime
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from core.utils import get_db_connection, make_json_safe
from core.validators import validate_username, validate_password, validate_email, ValidationError
from core.extensions import limiter

# 创建蓝图
auth_bp = Blueprint('auth', __name__, template_folder='templates')

# 初始化Argon2密码哈希器
ph = PasswordHasher()

# 获取logger
logger = logging.getLogger(__name__)


def login_required(f):
    """登录验证装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('请先登录', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """管理员权限验证装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('请先登录', 'warning')
            return redirect(url_for('auth.login'))
        if session.get('user_role') != 'admin':
            flash('需要管理员权限', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function


# 在整个应用层面拦截每个请求：已登录用户若被删除/禁用，则立即清理会话并拒绝继续访问
@auth_bp.before_app_request
def ensure_user_still_valid():
    endpoint = (request.endpoint or '')
    # 放行登录/登出/静态资源/诊断页
    if (endpoint.startswith('static') or
        endpoint in ('auth.login', 'auth.logout', 'diagnostic')):
        return

    if 'user_id' not in session:
        return

    user_id = session.get('user_id')
    client_token = session.get('session_token')
    cnx = get_db_connection()
    if not cnx:
        return  # 数据库暂不可用时不强制登出，避免影响其他功能
    cursor = cnx.cursor(dictionary=True)
    try:
        cursor.execute("SELECT IsActive, ReservedField1 FROM tbl_Users WHERE UserID = %s", (user_id,))
        row = cursor.fetchone()
        # 账号已删除/禁用 或 单点令牌不匹配（被挤下线）
        if (not row or not row.get('IsActive', 0) or (row.get('ReservedField1') and row.get('ReservedField1') != client_token)):
            session.clear()
            is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
            if is_ajax:
                return jsonify({ 'active': False, 'reason': 'kicked_or_invalid' }), 401
            flash('账号状态变更或在其他设备登录，已退出。', 'warning')
            return redirect(url_for('auth.login'))
    finally:
        cursor.close()
        cnx.close()


@auth_bp.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute; 20 per hour", methods=['POST'])
def login():
    """登录页面 - 带频率限制（5次/分钟，20次/小时）"""
    if 'user_id' in session:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('请输入用户名和密码', 'warning')
            return render_template('login.html')
        
        cnx = get_db_connection()
        if not cnx:
            flash('数据库连接失败', 'danger')
            return render_template('login.html')
        
        cursor = cnx.cursor(dictionary=True)
        
        try:
            # 查询用户
            cursor.execute("""
                SELECT UserID, Username, PasswordHash, RealName, Position, Role, IsActive
                FROM tbl_Users
                WHERE Username = %s
            """, (username,))
            user = cursor.fetchone()
            
            if not user:
                flash('用户名或密码错误', 'danger')
                logger.warning(f"登录失败: 用户名不存在 - {username} from {request.remote_addr}")
                return render_template('login.html')
            
            if not user['IsActive']:
                flash('账号已被禁用，请联系管理员', 'warning')
                logger.warning(f"登录失败: 账号已禁用 - {username}")
                return render_template('login.html')
            
            # 验证密码
            try:
                ph.verify(user['PasswordHash'], password)
                
                # 检查是否需要重新哈希（Argon2参数更新）
                if ph.check_needs_rehash(user['PasswordHash']):
                    new_hash = ph.hash(password)
                    cursor.execute("""
                        UPDATE tbl_Users SET PasswordHash = %s WHERE UserID = %s
                    """, (new_hash, user['UserID']))
                    cnx.commit()
                
                # 生成单点登录会话令牌
                session_token = secrets.token_urlsafe(32)

                # 更新最后登录时间与会话令牌（使用备用字段存储）
                cursor.execute("""
                    UPDATE tbl_Users SET LastLogin = %s, ReservedField1 = %s WHERE UserID = %s
                """, (datetime.now(), session_token, user['UserID']))
                cnx.commit()
                
                # 设置session
                session.permanent = True  # 启用持久化 session，应用 PERMANENT_SESSION_LIFETIME 设置
                session['user_id'] = user['UserID']
                session['username'] = user['Username']
                session['real_name'] = user['RealName']
                session['position'] = user['Position']
                session['user_role'] = user['Role']
                session['session_token'] = session_token
                
                flash(f'欢迎回来，{user["RealName"] or user["Username"]}！', 'success')
                logger.info(f"用户登录成功: {username} from {request.remote_addr}")
                return redirect(url_for('index'))
                
            except VerifyMismatchError:
                flash('用户名或密码错误', 'danger')
                logger.warning(f"登录失败: 密码错误 - {username} from {request.remote_addr}")
                return render_template('login.html')
        
        finally:
            cursor.close()
            cnx.close()
    
    return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    """登出"""
    # 清空数据库中的会话令牌
    user_id = session.get('user_id')
    if user_id:
        cnx = get_db_connection()
        if cnx:
            cur = cnx.cursor()
            try:
                cur.execute("UPDATE tbl_Users SET ReservedField1 = NULL WHERE UserID = %s", (user_id,))
                cnx.commit()
            finally:
                cur.close()
                cnx.close()

    session.clear()
    # 返回一个特殊页面，强制跳转顶层窗口到登录页
    return render_template('logout_redirect.html')


@auth_bp.route('/profile')
@login_required
def profile():
    """个人信息页面"""
    cnx = get_db_connection()
    if not cnx:
        flash('数据库连接失败', 'danger')
        return redirect(url_for('index'))
    
    cursor = cnx.cursor(dictionary=True)
    
    try:
        cursor.execute("""
            SELECT UserID, Username, RealName, Position, Role, Email, CreatedAt, LastLogin
            FROM tbl_Users
            WHERE UserID = %s
        """, (session['user_id'],))
        user = cursor.fetchone()
        
        return render_template('profile.html', user=user)
    
    finally:
        cursor.close()
        cnx.close()


@auth_bp.route('/profile/update', methods=['POST'])
@login_required
def update_profile():
    """更新个人信息"""
    real_name = request.form.get('real_name')
    position = request.form.get('position')
    email = request.form.get('email')
    
    cnx = get_db_connection()
    if not cnx:
        flash('数据库连接失败', 'danger')
        return redirect(url_for('auth.profile'))
    
    cursor = cnx.cursor()
    
    try:
        cursor.execute("""
            UPDATE tbl_Users
            SET RealName = %s, Position = %s, Email = %s
            WHERE UserID = %s
        """, (real_name, position, email, session['user_id']))
        cnx.commit()
        
        # 更新session
        session['real_name'] = real_name
        session['position'] = position
        
        flash('个人信息已更新', 'success')
    
    finally:
        cursor.close()
        cnx.close()
    
    return redirect(url_for('auth.profile'))


@auth_bp.route('/profile/change_password', methods=['POST'])
@login_required
def change_password():
    """修改密码 - 带输入验证"""
    old_password = request.form.get('old_password', '')
    new_password = request.form.get('new_password', '')
    confirm_password = request.form.get('confirm_password', '')
    
    if not all([old_password, new_password, confirm_password]):
        flash('请填写所有密码字段', 'warning')
        return redirect(url_for('auth.profile'))
    
    if new_password != confirm_password:
        flash('两次输入的新密码不一致', 'warning')
        return redirect(url_for('auth.profile'))
    
    # 验证新密码强度
    try:
        validate_password(new_password)
    except ValidationError as e:
        flash(str(e), 'warning')
        return redirect(url_for('auth.profile'))
    
    cnx = get_db_connection()
    if not cnx:
        flash('数据库连接失败', 'danger')
        return redirect(url_for('auth.profile'))
    
    cursor = cnx.cursor(dictionary=True)
    
    try:
        cursor.execute("SELECT PasswordHash FROM tbl_Users WHERE UserID = %s", (session['user_id'],))
        user = cursor.fetchone()
        
        # 验证旧密码
        try:
            ph.verify(user['PasswordHash'], old_password)
            
            # 生成新密码哈希
            new_hash = ph.hash(new_password)
            cursor.execute("""
                UPDATE tbl_Users SET PasswordHash = %s WHERE UserID = %s
            """, (new_hash, session['user_id']))
            cnx.commit()
            
            flash('密码修改成功，请重新登录', 'success')
            return redirect(url_for('auth.logout'))
            
        except VerifyMismatchError:
            flash('旧密码错误', 'danger')
            return redirect(url_for('auth.profile'))
    
    finally:
        cursor.close()
        cnx.close()


@auth_bp.route('/users')
@admin_required
def user_management():
    """用户管理页面（仅管理员）"""
    cnx = get_db_connection()
    if not cnx:
        flash('数据库连接失败', 'danger')
        return redirect(url_for('index'))
    
    cursor = cnx.cursor(dictionary=True)
    
    try:
        cursor.execute("""
            SELECT UserID, Username, RealName, Position, Role, Email, IsActive, CreatedAt, LastLogin
            FROM tbl_Users
            ORDER BY CreatedAt DESC
        """)
        users = cursor.fetchall()
        
        return render_template('user_management.html', users=users)
    
    finally:
        cursor.close()
        cnx.close()


@auth_bp.route('/users/add', methods=['POST'])
@admin_required
def add_user():
    """添加用户（仅管理员）- 带完整输入验证"""
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '')
    real_name = request.form.get('real_name', '').strip()
    position = request.form.get('position', '').strip()
    role = request.form.get('role', 'user')
    email = request.form.get('email', '').strip()
    
    # 输入验证
    try:
        validate_username(username)
        validate_password(password)
        if email:
            validate_email(email)
        
        # 验证角色
        if role not in ['admin', 'user']:
            raise ValidationError('无效的用户角色')
            
    except ValidationError as e:
        flash(str(e), 'warning')
        logger.warning(f"用户添加验证失败: {e}")
        return redirect(url_for('auth.user_management'))
    
    cnx = get_db_connection()
    if not cnx:
        flash('数据库连接失败', 'danger')
        return redirect(url_for('auth.user_management'))
    
    cursor = cnx.cursor()
    
    try:
        # 检查用户名是否已存在
        cursor.execute("SELECT UserID FROM tbl_Users WHERE Username = %s", (username,))
        if cursor.fetchone():
            flash('用户名已存在', 'warning')
            logger.info(f"用户添加失败: 用户名 {username} 已存在")
            return redirect(url_for('auth.user_management'))
        
        # 生成密码哈希
        password_hash = ph.hash(password)
        
        cursor.execute("""
            INSERT INTO tbl_Users (Username, PasswordHash, RealName, Position, Role, Email)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (username, password_hash, real_name, position, role, email))
        cnx.commit()
        
        flash(f'用户 {username} 创建成功', 'success')
        logger.info(f"管理员创建用户: {username}, 角色: {role}")
    
    except mysql.connector.Error as err:
        flash(f'创建用户失败：{err}', 'danger')
    
    finally:
        cursor.close()
        cnx.close()
    
    return redirect(url_for('auth.user_management'))


@auth_bp.route('/users/<int:user_id>/toggle', methods=['POST'])
@admin_required
def toggle_user_status(user_id):
    """启用/禁用用户（仅管理员）"""
    if user_id == session['user_id']:
        flash('不能禁用自己的账号', 'warning')
        return redirect(url_for('auth.user_management'))
    
    cnx = get_db_connection()
    if not cnx:
        flash('数据库连接失败', 'danger')
        return redirect(url_for('auth.user_management'))
    
    cursor = cnx.cursor(dictionary=True)
    
    try:
        cursor.execute("SELECT IsActive FROM tbl_Users WHERE UserID = %s", (user_id,))
        user = cursor.fetchone()
        
        if user:
            new_status = 0 if user['IsActive'] else 1
            # 若禁用用户，清空会话令牌，强制其下线
            if new_status == 0:
                cursor.execute("UPDATE tbl_Users SET IsActive = %s, ReservedField1 = NULL WHERE UserID = %s", (new_status, user_id))
            else:
                cursor.execute("UPDATE tbl_Users SET IsActive = %s WHERE UserID = %s", (new_status, user_id))
            cnx.commit()
            
            flash('用户状态已更新', 'success')
        else:
            flash('用户不存在', 'danger')
    
    finally:
        cursor.close()
        cnx.close()
    
    return redirect(url_for('auth.user_management'))


@auth_bp.route('/users/<int:user_id>/reset_password', methods=['POST'])
@admin_required
def reset_user_password(user_id):
    """重置用户密码（仅管理员）
    - 普通表单提交：使用 flash + 重定向
    - AJAX 提交（X-Requested-With=XMLHttpRequest）：返回 JSON，支持自动生成强密码
    """
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    new_password = (request.form.get('new_password') or '').strip()

    # 对于 AJAX 调用，若密码为空或过短，则自动生成强密码
    def generate_strong_password(length: int = 12) -> str:
        import secrets, string
        alphabet = string.ascii_letters + string.digits + '!@#$%^&*_-'
        return ''.join(secrets.choice(alphabet) for _ in range(length))

    if is_ajax:
        if len(new_password) < 6:
            new_password = generate_strong_password(12)
    else:
        if not new_password or len(new_password) < 6:
            flash('密码长度至少6位', 'warning')
            return redirect(url_for('auth.user_management'))

    cnx = get_db_connection()
    if not cnx:
        if is_ajax:
            return jsonify({ 'success': False, 'message': '数据库连接失败' }), 500
        flash('数据库连接失败', 'danger')
        return redirect(url_for('auth.user_management'))

    cursor = cnx.cursor()

    try:
        password_hash = ph.hash(new_password)
        cursor.execute(
            """
            UPDATE tbl_Users SET PasswordHash = %s WHERE UserID = %s
            """,
            (password_hash, user_id),
        )
        cnx.commit()

        if is_ajax:
            return jsonify({ 'success': True, 'new_password': new_password })
        flash('密码已重置', 'success')

    except mysql.connector.Error as err:
        if is_ajax:
            return jsonify({ 'success': False, 'message': str(err) }), 500
        flash(f'密码重置失败：{err}', 'danger')

    finally:
        cursor.close()
        cnx.close()

    return redirect(url_for('auth.user_management'))


@auth_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@admin_required
def delete_user(user_id):
    """删除用户（仅管理员）
    - AJAX 请求返回 JSON 并在前端无刷新删除行
    - 非 AJAX 请求走 flash + 重定向
    """
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    if user_id == session.get('user_id'):
        if is_ajax:
            return jsonify({ 'success': False, 'message': '不能删除当前登录账号' }), 400
        flash('不能删除当前登录账号', 'warning')
        return redirect(url_for('auth.user_management'))

    cnx = get_db_connection()
    if not cnx:
        if is_ajax:
            return jsonify({ 'success': False, 'message': '数据库连接失败' }), 500
        flash('数据库连接失败', 'danger')
        return redirect(url_for('auth.user_management'))

    cursor = cnx.cursor()
    try:
        cursor.execute("DELETE FROM tbl_Users WHERE UserID = %s", (user_id,))
        cnx.commit()
        if cursor.rowcount == 0:
            if is_ajax:
                return jsonify({ 'success': False, 'message': '用户不存在' }), 404
            flash('用户不存在', 'danger')
        else:
            if is_ajax:
                return jsonify({ 'success': True })
            flash('用户已删除', 'success')
    except mysql.connector.Error as err:
        if is_ajax:
            return jsonify({ 'success': False, 'message': str(err) }), 500
        flash(f'删除失败：{err}', 'danger')
    finally:
        cursor.close()
        cnx.close()

    return redirect(url_for('auth.user_management'))

