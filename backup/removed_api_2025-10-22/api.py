"""
RESTful API Blueprint
提供前后端分离的API接口
"""
from flask import Blueprint, request, jsonify
import logging
from datetime import datetime
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from core.utils import get_db_connection, make_json_safe
from api.auth import (
    generate_access_token, 
    generate_refresh_token,
    verify_token,
    token_required,
    admin_required,
    get_current_user
)
from core.validators import (
    validate_username,
    validate_password,
    validate_email,
    validate_string_length,
    validate_integer,
    validate_decimal,
    validate_date_string,
    ValidationError
)
from core.constants import (
    MAX_FORMULA_WEIGHT_PERCENTAGE,
    MAX_TRADE_NAME_LENGTH,
    MAX_PROJECT_NAME_LENGTH
)

# 创建API Blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api/v1')

# 获取logger
logger = logging.getLogger(__name__)

# 密码哈希器
ph = PasswordHasher()


# ============================================
# 认证API
# ============================================

@api_bp.route('/auth/login', methods=['POST'])
def api_login():
    """
    API登录接口
    
    POST /api/v1/auth/login
    Body: {
        "username": "用户名",
        "password": "密码"
    }
    
    Response: {
        "success": true,
        "data": {
            "access_token": "...",
            "refresh_token": "...",
            "user": {...}
        }
    }
    """
    data = request.get_json()
    
    if not data:
        return jsonify({
            'success': False,
            'message': '请提供JSON数据'
        }), 400
    
    username = data.get('username', '').strip()
    password = data.get('password', '')
    
    if not username or not password:
        return jsonify({
            'success': False,
            'message': '用户名和密码不能为空'
        }), 400
    
    cnx = get_db_connection()
    if not cnx:
        return jsonify({
            'success': False,
            'message': '数据库连接失败'
        }), 500
    
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
            logger.warning(f"API登录失败: 用户不存在 - {username} from {request.remote_addr}")
            return jsonify({
                'success': False,
                'message': '用户名或密码错误'
            }), 401
        
        if not user['IsActive']:
            logger.warning(f"API登录失败: 账号已禁用 - {username}")
            return jsonify({
                'success': False,
                'message': '账号已被禁用'
            }), 403
        
        # 验证密码
        try:
            ph.verify(user['PasswordHash'], password)
            
            # 更新最后登录时间
            cursor.execute("""
                UPDATE tbl_Users SET LastLogin = %s WHERE UserID = %s
            """, (datetime.now(), user['UserID']))
            cnx.commit()
            
            # 生成JWT令牌
            access_token = generate_access_token(
                user['UserID'],
                user['Username'],
                user['Role']
            )
            refresh_token = generate_refresh_token(user['UserID'])
            
            logger.info(f"API登录成功: {username} from {request.remote_addr}")
            
            return jsonify({
                'success': True,
                'data': {
                    'access_token': access_token,
                    'refresh_token': refresh_token,
                    'user': {
                        'user_id': user['UserID'],
                        'username': user['Username'],
                        'real_name': user['RealName'],
                        'position': user['Position'],
                        'role': user['Role']
                    }
                },
                'message': '登录成功'
            }), 200
            
        except VerifyMismatchError:
            logger.warning(f"API登录失败: 密码错误 - {username} from {request.remote_addr}")
            return jsonify({
                'success': False,
                'message': '用户名或密码错误'
            }), 401
    
    finally:
        cursor.close()
        cnx.close()


@api_bp.route('/auth/refresh', methods=['POST'])
def api_refresh_token():
    """
    刷新访问令牌
    
    POST /api/v1/auth/refresh
    Body: {
        "refresh_token": "..."
    }
    
    Response: {
        "success": true,
        "data": {
            "access_token": "..."
        }
    }
    """
    data = request.get_json()
    
    if not data or not data.get('refresh_token'):
        return jsonify({
            'success': False,
            'message': '缺少刷新令牌'
        }), 400
    
    # 验证刷新令牌
    payload = verify_token(data['refresh_token'], 'refresh')
    if not payload:
        return jsonify({
            'success': False,
            'message': '无效或已过期的刷新令牌'
        }), 401
    
    # 查询用户信息（确保用户仍然有效）
    cnx = get_db_connection()
    if not cnx:
        return jsonify({
            'success': False,
            'message': '数据库连接失败'
        }), 500
    
    cursor = cnx.cursor(dictionary=True)
    
    try:
        cursor.execute("""
            SELECT UserID, Username, Role, IsActive
            FROM tbl_Users
            WHERE UserID = %s
        """, (payload['user_id'],))
        user = cursor.fetchone()
        
        if not user or not user['IsActive']:
            return jsonify({
                'success': False,
                'message': '用户账号无效'
            }), 401
        
        # 生成新的访问令牌
        new_access_token = generate_access_token(
            user['UserID'],
            user['Username'],
            user['Role']
        )
        
        return jsonify({
            'success': True,
            'data': {
                'access_token': new_access_token
            },
            'message': '令牌刷新成功'
        }), 200
    
    finally:
        cursor.close()
        cnx.close()


@api_bp.route('/auth/me', methods=['GET'])
@token_required
def api_get_current_user():
    """
    获取当前用户信息
    
    GET /api/v1/auth/me
    Headers: Authorization: Bearer <token>
    
    Response: {
        "success": true,
        "data": {
            "user": {...}
        }
    }
    """
    user_info = get_current_user()
    
    # 从数据库获取完整信息
    cnx = get_db_connection()
    if not cnx:
        return jsonify({
            'success': False,
            'message': '数据库连接失败'
        }), 500
    
    cursor = cnx.cursor(dictionary=True)
    
    try:
        cursor.execute("""
            SELECT UserID, Username, RealName, Position, Role, Email, CreatedAt, LastLogin
            FROM tbl_Users
            WHERE UserID = %s
        """, (user_info['user_id'],))
        user = cursor.fetchone()
        
        if not user:
            return jsonify({
                'success': False,
                'message': '用户不存在'
            }), 404
        
        return jsonify({
            'success': True,
            'data': {
                'user': make_json_safe(user)
            }
        }), 200
    
    finally:
        cursor.close()
        cnx.close()


# ============================================
# 项目管理API
# ============================================

@api_bp.route('/projects', methods=['GET'])
@token_required
def api_list_projects():
    """
    获取项目列表
    
    GET /api/v1/projects?page=1&per_page=20
    Headers: Authorization: Bearer <token>
    
    Response: {
        "success": true,
        "data": {
            "projects": [...],
            "pagination": {
                "page": 1,
                "per_page": 20,
                "total": 100
            }
        }
    }
    """
    # 分页参数
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    # 限制每页数量
    per_page = min(per_page, 100)
    offset = (page - 1) * per_page
    
    cnx = get_db_connection()
    if not cnx:
        return jsonify({
            'success': False,
            'message': '数据库连接失败'
        }), 500
    
    cursor = cnx.cursor(dictionary=True)
    
    try:
        # 获取总数
        cursor.execute("SELECT COUNT(*) as total FROM tbl_ProjectInfo")
        total = cursor.fetchone()['total']
        
        # 获取分页数据
        cursor.execute("""
            SELECT p.*, pt.TypeName 
            FROM tbl_ProjectInfo p
            LEFT JOIN tbl_Config_ProjectTypes pt ON p.ProjectType_FK = pt.TypeID
            ORDER BY p.ProjectID DESC
            LIMIT %s OFFSET %s
        """, (per_page, offset))
        projects = cursor.fetchall()
        
        return jsonify({
            'success': True,
            'data': {
                'projects': make_json_safe(projects),
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': total,
                    'pages': (total + per_page - 1) // per_page
                }
            }
        }), 200
    
    finally:
        cursor.close()
        cnx.close()


@api_bp.route('/projects/<int:project_id>', methods=['GET'])
@token_required
def api_get_project(project_id):
    """
    获取单个项目详情
    
    GET /api/v1/projects/{id}
    Headers: Authorization: Bearer <token>
    
    Response: {
        "success": true,
        "data": {
            "project": {...},
            "composition": [...],
            "test_results": {...}
        }
    }
    """
    cnx = get_db_connection()
    if not cnx:
        return jsonify({
            'success': False,
            'message': '数据库连接失败'
        }), 500
    
    cursor = cnx.cursor(dictionary=True)
    
    try:
        # 获取项目信息
        cursor.execute("""
            SELECT p.*, pt.TypeName 
            FROM tbl_ProjectInfo p
            LEFT JOIN tbl_Config_ProjectTypes pt ON p.ProjectType_FK = pt.TypeID
            WHERE p.ProjectID = %s
        """, (project_id,))
        project = cursor.fetchone()
        
        if not project:
            return jsonify({
                'success': False,
                'message': '项目不存在'
            }), 404
        
        # 获取配方成分
        cursor.execute("""
            SELECT fc.*, 
                   rm.TradeName as MaterialName,
                   inf.TradeName as FillerName
            FROM tbl_FormulaComposition fc
            LEFT JOIN tbl_RawMaterials rm ON fc.MaterialID_FK = rm.MaterialID
            LEFT JOIN tbl_InorganicFillers inf ON fc.FillerID_FK = inf.FillerID
            WHERE fc.ProjectID_FK = %s
            ORDER BY fc.CompositionID
        """, (project_id,))
        composition = cursor.fetchall()
        
        # 获取测试结果（根据项目类型）
        test_results = None
        type_name = project.get('TypeName')
        test_table_mapping = {
            '喷墨': 'tbl_TestResults_Ink',
            '涂层': 'tbl_TestResults_Coating',
            '3D打印': 'tbl_TestResults_3DPrint',
            '复合材料': 'tbl_TestResults_Composite'
        }
        
        test_table = test_table_mapping.get(type_name)
        if test_table:
            cursor.execute(f"SELECT * FROM {test_table} WHERE ProjectID_FK = %s", (project_id,))
            test_results = cursor.fetchone()
        
        return jsonify({
            'success': True,
            'data': {
                'project': make_json_safe(project),
                'composition': make_json_safe(composition),
                'test_results': make_json_safe(test_results)
            }
        }), 200
    
    finally:
        cursor.close()
        cnx.close()


@api_bp.route('/projects', methods=['POST'])
@token_required
def api_create_project():
    """
    创建新项目
    
    POST /api/v1/projects
    Headers: Authorization: Bearer <token>
    Body: {
        "project_name": "...",
        "project_type_fk": 1,
        "formulator_name": "...",
        "formulation_date": "2025-10-21",
        "substrate_application": "..."
    }
    
    Response: {
        "success": true,
        "data": {
            "project_id": 123,
            "formula_code": "ABC-21102025-INK-01"
        },
        "message": "项目创建成功"
    }
    """
    data = request.get_json()
    
    if not data:
        return jsonify({
            'success': False,
            'message': '请提供JSON数据'
        }), 400
    
    # 输入验证
    try:
        project_name = validate_string_length(
            data.get('project_name', '').strip(),
            MAX_PROJECT_NAME_LENGTH,
            "项目名称",
            required=True
        )
        project_type_fk = validate_integer(
            data.get('project_type_fk'),
            min_value=1,
            field_name="项目类型"
        )
        formulator_name = validate_string_length(
            data.get('formulator_name', '').strip(),
            255,
            "配方设计师",
            required=True
        )
        formulation_date_str = validate_date_string(
            data.get('formulation_date', '').strip(),
            "配方设计日期"
        )
        substrate_application = data.get('substrate_application', '').strip()
        if substrate_application:
            validate_string_length(substrate_application, 1000, "目标基材", required=False)
    
    except ValidationError as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400
    
    cnx = get_db_connection()
    if not cnx:
        return jsonify({
            'success': False,
            'message': '数据库连接失败'
        }), 500
    
    cursor = cnx.cursor(dictionary=True)
    
    try:
        formulation_date = datetime.strptime(formulation_date_str, '%Y-%m-%d').date()
        
        # 生成配方编码
        cursor.execute("SELECT TypeCode FROM tbl_Config_ProjectTypes WHERE TypeID = %s", (project_type_fk,))
        type_code_result = cursor.fetchone()
        type_code = type_code_result['TypeCode'] if type_code_result else 'XXX'
        
        cursor.execute("""
            SELECT COUNT(*) as count FROM tbl_ProjectInfo 
            WHERE FormulationDate = %s AND ProjectType_FK = %s
        """, (formulation_date_str, project_type_fk))
        sequence_num = cursor.fetchone()['count'] + 1
        
        initials = "".join(c for c in formulator_name if c.isupper()) or formulator_name[:2].upper()
        date_str = formulation_date.strftime('%d%m%Y')
        formula_code = f"{initials}-{date_str}-{type_code}-{sequence_num:02d}"
        
        # 插入项目
        cursor.execute("""
            INSERT INTO tbl_ProjectInfo 
            (ProjectName, ProjectType_FK, SubstrateApplication, FormulatorName, FormulationDate, FormulaCode)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (project_name, project_type_fk, substrate_application, formulator_name, formulation_date, formula_code))
        
        cnx.commit()
        project_id = cursor.lastrowid
        
        logger.info(f"API创建项目: {project_name} by user {get_current_user()['username']}")
        
        return jsonify({
            'success': True,
            'data': {
                'project_id': project_id,
                'formula_code': formula_code
            },
            'message': '项目创建成功'
        }), 201
    
    except Exception as e:
        cnx.rollback()
        logger.error(f"API创建项目失败: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'创建失败: {str(e)}'
        }), 500
    
    finally:
        cursor.close()
        cnx.close()


# ============================================
# 用户管理API（管理员）
# ============================================

@api_bp.route('/users', methods=['GET'])
@admin_required
def api_list_users():
    """
    获取用户列表（管理员）
    
    GET /api/v1/users
    Headers: Authorization: Bearer <token>
    
    Response: {
        "success": true,
        "data": {
            "users": [...]
        }
    }
    """
    cnx = get_db_connection()
    if not cnx:
        return jsonify({
            'success': False,
            'message': '数据库连接失败'
        }), 500
    
    cursor = cnx.cursor(dictionary=True)
    
    try:
        cursor.execute("""
            SELECT UserID, Username, RealName, Position, Role, Email, IsActive, CreatedAt, LastLogin
            FROM tbl_Users
            ORDER BY CreatedAt DESC
        """)
        users = cursor.fetchall()
        
        return jsonify({
            'success': True,
            'data': {
                'users': make_json_safe(users)
            }
        }), 200
    
    finally:
        cursor.close()
        cnx.close()


# ============================================
# 健康检查
# ============================================

@api_bp.route('/health', methods=['GET'])
def api_health_check():
    """
    API健康检查
    
    GET /api/v1/health
    
    Response: {
        "success": true,
        "data": {
            "status": "healthy",
            "timestamp": "2025-10-21T10:30:00"
        }
    }
    """
    return jsonify({
        'success': True,
        'data': {
            'status': 'healthy',
            'version': '1.0.0',
            'timestamp': datetime.utcnow().isoformat()
        }
    }), 200

