from flask import Blueprint, render_template, request, redirect, url_for, flash
import logging
from core.utils import get_db_connection
from core.validators import validate_string_length, validate_decimal, validate_integer, ValidationError
from core.constants import MAX_TRADE_NAME_LENGTH, MAX_SUPPLIER_LENGTH

materials_bp = Blueprint('materials', __name__, template_folder='templates')

# 获取logger
logger = logging.getLogger(__name__)

@materials_bp.route('/materials')
def material_list():
    """第二级: 原料列表页面（带分页）。"""
    # 获取分页参数
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    # 获取筛选参数
    filter_category = (request.args.get('category') or '').strip()
    filter_supplier = (request.args.get('supplier') or '').strip()
    filter_q = (request.args.get('q') or '').strip()
    
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
        return render_template('material_list.html', materials=[], page=1, total_pages=0, total=0, per_page=per_page)
    
    cursor = cnx.cursor(dictionary=True)
    
    where_clauses = []
    params = []
    if filter_category:
        where_clauses.append("mc.CategoryName = %s")
        params.append(filter_category)
    if filter_supplier:
        where_clauses.append("m.Supplier = %s")
        params.append(filter_supplier)
    if filter_q:
        where_clauses.append("(m.TradeName LIKE %s OR m.CAS_Number LIKE %s)")
        like_val = f"%{filter_q}%"
        params.extend([like_val, like_val])
    where_sql = (" WHERE " + " AND ".join(where_clauses)) if where_clauses else ""
    
    # 查询总记录数（含筛选）
    count_sql = (
        "SELECT COUNT(*) as total FROM tbl_RawMaterials m "
        "LEFT JOIN tbl_Config_MaterialCategories mc ON m.Category_FK = mc.CategoryID"
        + where_sql
    )
    cursor.execute(count_sql, tuple(params))
    total = cursor.fetchone()['total']
    
    # 计算总页数
    total_pages = (total + per_page - 1) // per_page if total > 0 else 1
    
    # 确保页码不超过总页数
    if page > total_pages and total_pages > 0:
        page = total_pages
        offset = (page - 1) * per_page
    
    # 查询当前页数据（含筛选）
    query = (
        "SELECT m.*, mc.CategoryName "
        "FROM tbl_RawMaterials m "
        "LEFT JOIN tbl_Config_MaterialCategories mc ON m.Category_FK = mc.CategoryID "
        + where_sql +
        " ORDER BY m.MaterialID DESC LIMIT %s OFFSET %s"
    )
    cursor.execute(query, tuple(params + [per_page, offset]))
    materials = cursor.fetchall()
    
    # 提供筛选下拉可选项（全量）
    cursor.execute("SELECT CategoryName FROM tbl_Config_MaterialCategories ORDER BY CategoryName")
    categories = [r['CategoryName'] for r in cursor.fetchall()]
    cursor.execute("SELECT DISTINCT Supplier FROM tbl_RawMaterials WHERE COALESCE(Supplier,'') <> '' ORDER BY Supplier")
    suppliers = [r['Supplier'] for r in cursor.fetchall()]
    cursor.close()
    cnx.close()
    
    return render_template('material_list.html',
                         materials=materials,
                         page=page,
                         per_page=per_page,
                         total=total,
                         total_pages=total_pages,
                         categories=categories,
                         suppliers=suppliers,
                         filter_category=filter_category,
                         filter_supplier=filter_supplier,
                         filter_q=filter_q)

@materials_bp.route('/material/add', methods=['GET', 'POST'])
def add_material():
    """第三级: 添加一个新原料。"""
    cnx = get_db_connection()
    if not cnx:
        flash("数据库连接失败！", "danger")
        return redirect(url_for('materials.material_list'))
    
    cursor = cnx.cursor(dictionary=True)

    if request.method == 'POST':
        # 获取并清理表单数据
        trade_name = request.form.get('TradeName', '').strip()
        category_fk = request.form.get('Category_FK', '').strip()
        supplier = request.form.get('Supplier', '').strip()
        cas_number = request.form.get('CAS_Number', '').strip()
        density = request.form.get('Density', '').strip()
        viscosity = request.form.get('Viscosity', '').strip()
        function_desc = request.form.get('FunctionDescription', '').strip()
        
        # 输入验证
        try:
            validate_string_length(trade_name, MAX_TRADE_NAME_LENGTH, "商品名称", required=True)
            if supplier:
                validate_string_length(supplier, MAX_SUPPLIER_LENGTH, "供应商", required=False)
            if cas_number:
                validate_string_length(cas_number, 255, "CAS号", required=False)
            if category_fk:
                validate_integer(category_fk, min_value=1, field_name="类别")
                category_fk = int(category_fk)
            else:
                category_fk = None
            if density:
                density = validate_decimal(density, min_value=0, max_value=50, field_name="密度")
            else:
                density = None
            if viscosity:
                viscosity = validate_decimal(viscosity, min_value=0, field_name="粘度")
            else:
                viscosity = None
            if function_desc:
                validate_string_length(function_desc, 1000, "功能说明", required=False)
        except ValidationError as e:
            flash(str(e), 'warning')
            logger.warning(f"原料添加验证失败: {e}")
            cursor.execute("SELECT * FROM tbl_Config_MaterialCategories")
            categories = cursor.fetchall()
            cursor.close()
            cnx.close()
            return render_template('material_form.html', categories=categories, action='add', material=request.form)
        
        sql = """
            INSERT INTO tbl_RawMaterials 
            (TradeName, Category_FK, Supplier, CAS_Number, Density, Viscosity, FunctionDescription)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        values = (trade_name, category_fk, supplier, cas_number, density, viscosity, function_desc)
        cursor.execute(sql, values)
        cnx.commit()
        flash('新原料已成功创建！', 'success')
        cursor.close()
        cnx.close()
        return redirect(url_for('materials.material_list'))

    cursor.execute("SELECT * FROM tbl_Config_MaterialCategories")
    categories = cursor.fetchall()
    cursor.close()
    cnx.close()
    return render_template('material_form.html', categories=categories, action='add', material={})

@materials_bp.route('/material/edit/<int:material_id>', methods=['GET', 'POST'])
def edit_material(material_id):
    """第三级: 编辑一个已存在的原料。"""
    cnx = get_db_connection()
    if not cnx:
        flash("数据库连接失败！", "danger")
        return redirect(url_for('materials.material_list'))
    
    cursor = cnx.cursor(dictionary=True)

    if request.method == 'POST':
        # 获取并清理表单数据
        trade_name = request.form.get('TradeName', '').strip()
        category_fk = request.form.get('Category_FK', '').strip()
        supplier = request.form.get('Supplier', '').strip()
        cas_number = request.form.get('CAS_Number', '').strip()
        density = request.form.get('Density', '').strip()
        viscosity = request.form.get('Viscosity', '').strip()
        function_desc = request.form.get('FunctionDescription', '').strip()
        
        # 输入验证
        try:
            validate_string_length(trade_name, MAX_TRADE_NAME_LENGTH, "商品名称", required=True)
            if supplier:
                validate_string_length(supplier, MAX_SUPPLIER_LENGTH, "供应商", required=False)
            if cas_number:
                validate_string_length(cas_number, 255, "CAS号", required=False)
            if category_fk:
                validate_integer(category_fk, min_value=1, field_name="类别")
                category_fk = int(category_fk)
            else:
                category_fk = None
            if density:
                density = validate_decimal(density, min_value=0, max_value=50, field_name="密度")
            else:
                density = None
            if viscosity:
                viscosity = validate_decimal(viscosity, min_value=0, field_name="粘度")
            else:
                viscosity = None
            if function_desc:
                validate_string_length(function_desc, 1000, "功能说明", required=False)
        except ValidationError as e:
            flash(str(e), 'warning')
            logger.warning(f"原料编辑验证失败: {e}")
            cursor.execute("SELECT * FROM tbl_RawMaterials WHERE MaterialID = %s", (material_id,))
            material = cursor.fetchone()
            cursor.execute("SELECT * FROM tbl_Config_MaterialCategories")
            categories = cursor.fetchall()
            cursor.close()
            cnx.close()
            return render_template('material_form.html', material=material, categories=categories, action='edit')
        
        sql = """
            UPDATE tbl_RawMaterials SET
            TradeName = %s, Category_FK = %s, Supplier = %s, CAS_Number = %s,
            Density = %s, Viscosity = %s, FunctionDescription = %s
            WHERE MaterialID = %s
        """
        values = (trade_name, category_fk, supplier, cas_number, density, viscosity, function_desc, material_id)
        cursor.execute(sql, values)
        cnx.commit()
        flash(f'原料 {material_id} 已更新。', 'success')
        cursor.close()
        cnx.close()
        return redirect(url_for('materials.material_list'))

    cursor.execute("SELECT * FROM tbl_RawMaterials WHERE MaterialID = %s", (material_id,))
    material = cursor.fetchone()
    cursor.execute("SELECT * FROM tbl_Config_MaterialCategories")
    categories = cursor.fetchall()
    cursor.close()
    cnx.close()
    
    if not material:
        flash(f'未找到原料ID {material_id}。', 'danger')
        return redirect(url_for('materials.material_list'))
        
    return render_template('material_form.html', material=material, categories=categories, action='edit')

@materials_bp.route('/material/batch_action', methods=['POST'])
def material_batch_action():
    """处理原料的批量操作。"""
    action = request.form.get('action')
    selected_ids = request.form.getlist('selected_ids')

    if not selected_ids:
        flash('请至少选择一个原料。', 'warning')
        return redirect(url_for('materials.material_list'))

    cnx = get_db_connection()
    if not cnx:
        flash("数据库连接失败！", "danger")
        return redirect(url_for('materials.material_list'))
    
    cursor = cnx.cursor(dictionary=True)

    if action == 'delete':
        placeholders = ','.join(['%s'] * len(selected_ids))
        sql = f"DELETE FROM tbl_RawMaterials WHERE MaterialID IN ({placeholders})"
        cursor.execute(sql, tuple(selected_ids))
        cnx.commit()
        flash(f'成功删除了 {len(selected_ids)} 个原料。', 'success')
    
    cursor.close()
    cnx.close()
    return redirect(url_for('materials.material_list'))
