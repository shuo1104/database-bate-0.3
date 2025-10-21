from flask import Blueprint, render_template, request, redirect, url_for, flash
import logging
from core.utils import get_db_connection
from core.validators import validate_string_length, validate_decimal, validate_integer, ValidationError
from core.constants import MAX_TRADE_NAME_LENGTH, MAX_SUPPLIER_LENGTH

fillers_bp = Blueprint('fillers', __name__, template_folder='templates')

# 获取logger
logger = logging.getLogger(__name__)

@fillers_bp.route('/fillers')
def filler_list():
    """第二级: 无机材料列表页面（带分页）。"""
    # 获取分页参数
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    # 验证分页参数
    if page < 1:
        page = 1
    if per_page not in [10, 20, 50, 100]:
        per_page = 20
    
    # 计算偏移量
    offset = (page - 1) * per_page
    
    cnx = get_db_connection()
    if not cnx:
        flash("数据库连接失败！", "danger")
        return render_template('filler_list.html', fillers=[], page=1, total_pages=0, total=0, per_page=per_page)
    
    cursor = cnx.cursor(dictionary=True)
    
    # 查询总记录数
    cursor.execute("SELECT COUNT(*) as total FROM tbl_InorganicFillers")
    total = cursor.fetchone()['total']
    
    # 计算总页数
    total_pages = (total + per_page - 1) // per_page if total > 0 else 1
    
    # 确保页码不超过总页数
    if page > total_pages and total_pages > 0:
        page = total_pages
        offset = (page - 1) * per_page
    
    # 查询当前页数据
    query = """
        SELECT f.*, ft.FillerTypeName
        FROM tbl_InorganicFillers f
        LEFT JOIN tbl_Config_FillerTypes ft ON f.FillerType_FK = ft.FillerTypeID
        ORDER BY f.FillerID DESC
        LIMIT %s OFFSET %s
    """
    cursor.execute(query, (per_page, offset))
    fillers = cursor.fetchall()
    cursor.close()
    cnx.close()
    
    return render_template('filler_list.html',
                         fillers=fillers,
                         page=page,
                         per_page=per_page,
                         total=total,
                         total_pages=total_pages)

@fillers_bp.route('/filler/add', methods=['GET', 'POST'])
def add_filler():
    """第三级: 添加一个新无机材料。"""
    cnx = get_db_connection()
    if not cnx:
        flash("数据库连接失败！", "danger")
        return redirect(url_for('fillers.filler_list'))
    
    cursor = cnx.cursor(dictionary=True)
    
    if request.method == 'POST':
        # 获取并清理表单数据
        trade_name = request.form.get('TradeName', '').strip()
        filler_type_fk = request.form.get('FillerType_FK', '').strip()
        supplier = request.form.get('Supplier', '').strip()
        particle_size = request.form.get('ParticleSize', '').strip()
        is_silanized = 1 if request.form.get('IsSilanized') == 'on' else 0
        coupling_agent = request.form.get('CouplingAgent', '').strip()
        surface_area = request.form.get('SurfaceArea', '').strip()
        
        # 输入验证
        try:
            validate_string_length(trade_name, MAX_TRADE_NAME_LENGTH, "商品名称", required=True)
            if supplier:
                validate_string_length(supplier, MAX_SUPPLIER_LENGTH, "供应商", required=False)
            if particle_size:
                validate_string_length(particle_size, 255, "粒径", required=False)
            if coupling_agent:
                validate_string_length(coupling_agent, 255, "偶联剂", required=False)
            if filler_type_fk:
                validate_integer(filler_type_fk, min_value=1, field_name="填料类型")
                filler_type_fk = int(filler_type_fk)
            else:
                filler_type_fk = None
            if surface_area:
                surface_area = validate_decimal(surface_area, min_value=0, field_name="比表面积")
            else:
                surface_area = None
        except ValidationError as e:
            flash(str(e), 'warning')
            logger.warning(f"填料添加验证失败: {e}")
            cursor.execute("SELECT * FROM tbl_Config_FillerTypes")
            filler_types = cursor.fetchall()
            cursor.close()
            cnx.close()
            return render_template('filler_form.html', action='add', filler=request.form, filler_types=filler_types)
        
        sql = """
            INSERT INTO tbl_InorganicFillers 
            (TradeName, FillerType_FK, Supplier, ParticleSize, IsSilanized, CouplingAgent, SurfaceArea)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        values = (trade_name, filler_type_fk, supplier, particle_size, is_silanized, coupling_agent, surface_area)
        cursor.execute(sql, values)
        cnx.commit()
        flash('新无机材料已成功创建！', 'success')
        cursor.close()
        cnx.close()
        return redirect(url_for('fillers.filler_list'))

    cursor.execute("SELECT * FROM tbl_Config_FillerTypes")
    filler_types = cursor.fetchall()
    cursor.close()
    cnx.close()
    return render_template('filler_form.html', action='add', filler={}, filler_types=filler_types)

@fillers_bp.route('/filler/edit/<int:filler_id>', methods=['GET', 'POST'])
def edit_filler(filler_id):
    """第三级: 编辑一个已存在的无机材料。"""
    cnx = get_db_connection()
    if not cnx:
        flash("数据库连接失败！", "danger")
        return redirect(url_for('fillers.filler_list'))
    
    cursor = cnx.cursor(dictionary=True)

    if request.method == 'POST':
        # 获取并清理表单数据
        trade_name = request.form.get('TradeName', '').strip()
        filler_type_fk = request.form.get('FillerType_FK', '').strip()
        supplier = request.form.get('Supplier', '').strip()
        particle_size = request.form.get('ParticleSize', '').strip()
        is_silanized = 1 if request.form.get('IsSilanized') == 'on' else 0
        coupling_agent = request.form.get('CouplingAgent', '').strip()
        surface_area = request.form.get('SurfaceArea', '').strip()
        
        # 输入验证
        try:
            validate_string_length(trade_name, MAX_TRADE_NAME_LENGTH, "商品名称", required=True)
            if supplier:
                validate_string_length(supplier, MAX_SUPPLIER_LENGTH, "供应商", required=False)
            if particle_size:
                validate_string_length(particle_size, 255, "粒径", required=False)
            if coupling_agent:
                validate_string_length(coupling_agent, 255, "偶联剂", required=False)
            if filler_type_fk:
                validate_integer(filler_type_fk, min_value=1, field_name="填料类型")
                filler_type_fk = int(filler_type_fk)
            else:
                filler_type_fk = None
            if surface_area:
                surface_area = validate_decimal(surface_area, min_value=0, field_name="比表面积")
            else:
                surface_area = None
        except ValidationError as e:
            flash(str(e), 'warning')
            logger.warning(f"填料编辑验证失败: {e}")
            cursor.execute("SELECT * FROM tbl_InorganicFillers WHERE FillerID = %s", (filler_id,))
            filler = cursor.fetchone()
            cursor.execute("SELECT * FROM tbl_Config_FillerTypes")
            filler_types = cursor.fetchall()
            cursor.close()
            cnx.close()
            return render_template('filler_form.html', filler=filler, action='edit', filler_types=filler_types)
        
        sql = """
            UPDATE tbl_InorganicFillers SET
            TradeName = %s, FillerType_FK = %s, Supplier = %s, ParticleSize = %s,
            IsSilanized = %s, CouplingAgent = %s, SurfaceArea = %s
            WHERE FillerID = %s
        """
        values = (trade_name, filler_type_fk, supplier, particle_size, is_silanized, coupling_agent, surface_area, filler_id)
        cursor.execute(sql, values)
        cnx.commit()
        flash(f'无机材料 {filler_id} 已更新。', 'success')
        cursor.close()
        cnx.close()
        return redirect(url_for('fillers.filler_list'))

    cursor.execute("SELECT * FROM tbl_InorganicFillers WHERE FillerID = %s", (filler_id,))
    filler = cursor.fetchone()
    cursor.execute("SELECT * FROM tbl_Config_FillerTypes")
    filler_types = cursor.fetchall()
    cursor.close()
    cnx.close()
    
    if not filler:
        flash(f'未找到无机材料ID {filler_id}。', 'danger')
        return redirect(url_for('fillers.filler_list'))
        
    return render_template('filler_form.html', filler=filler, action='edit', filler_types=filler_types)

@fillers_bp.route('/filler/batch_action', methods=['POST'])
def filler_batch_action():
    """处理无机材料的批量操作。"""
    action = request.form.get('action')
    selected_ids = request.form.getlist('selected_ids')

    if not selected_ids:
        flash('请至少选择一个无机材料。', 'warning')
        return redirect(url_for('fillers.filler_list'))

    cnx = get_db_connection()
    if not cnx:
        flash("数据库连接失败！", "danger")
        return redirect(url_for('fillers.filler_list'))
    
    cursor = cnx.cursor()

    if action == 'delete':
        placeholders = ','.join(['%s'] * len(selected_ids))
        sql = f"DELETE FROM tbl_InorganicFillers WHERE FillerID IN ({placeholders})"
        cursor.execute(sql, tuple(selected_ids))
        cnx.commit()
        flash(f'成功删除了 {len(selected_ids)} 个无机材料。', 'success')

    cursor.close()
    cnx.close()
    return redirect(url_for('fillers.filler_list'))
