from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app, make_response
import mysql.connector
import decimal
import json
import csv
from io import StringIO
from datetime import datetime, date
import traceback
import logging

from core.utils import get_db_connection, make_json_safe
from core.constants import MAX_FORMULA_WEIGHT_PERCENTAGE, TEST_RESULT_TABLE_MAPPING, COMPONENT_TYPE_MATERIAL, COMPONENT_TYPE_FILLER
from core.validators import validate_decimal, validate_string_length, validate_date_string, validate_integer, ValidationError

# Create a Blueprint
projects_bp = Blueprint('projects', __name__, template_folder='templates')

# 获取logger
logger = logging.getLogger(__name__)

# Helper function to get test result table name based on project type
def get_test_result_table(type_name):
    """根据项目类型返回对应的测试结果表名"""
    return TEST_RESULT_TABLE_MAPPING.get(type_name, None)

@projects_bp.route('/projects')
def project_list():
    """Level 2: Project Info List Page with Pagination."""
    # 获取分页参数
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)  # 默认每页20条
    
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
        return render_template('project_list.html', projects=[], page=1, total_pages=0, total=0, per_page=per_page)
    
    cursor = cnx.cursor(dictionary=True)
    
    # 查询总记录数
    cursor.execute("SELECT COUNT(*) as total FROM tbl_ProjectInfo")
    total = cursor.fetchone()['total']
    
    # 计算总页数
    total_pages = (total + per_page - 1) // per_page if total > 0 else 1
    
    # 确保页码不超过总页数
    if page > total_pages and total_pages > 0:
        page = total_pages
        offset = (page - 1) * per_page
    
    # 查询当前页数据
    query = """
        SELECT p.*, pt.TypeName 
        FROM tbl_ProjectInfo p
        LEFT JOIN tbl_Config_ProjectTypes pt ON p.ProjectType_FK = pt.TypeID
        ORDER BY p.ProjectID DESC
        LIMIT %s OFFSET %s
    """
    cursor.execute(query, (per_page, offset))
    projects = cursor.fetchall()
    cursor.close()
    cnx.close()
    
    return render_template('project_list.html', 
                         projects=projects,
                         page=page,
                         per_page=per_page,
                         total=total,
                         total_pages=total_pages)

@projects_bp.route('/project/add', methods=['GET', 'POST'])
def add_project():
    """Level 3: Add a new project."""
    cnx = get_db_connection()
    if not cnx:
        flash("数据库连接失败！", "danger")
        return redirect(url_for('projects.project_list'))
    
    cursor = cnx.cursor(dictionary=True)

    if request.method == 'POST':
        project_name = request.form.get('ProjectName', '').strip()
        project_type_fk = request.form.get('ProjectType_FK')
        formulator_name = request.form.get('FormulatorName', '').strip()
        formulation_date_str = request.form.get('FormulationDate', '').strip()
        substrate_application = request.form.get('SubstrateApplication', '').strip()
        
        # 输入验证
        try:
            validate_string_length(project_name, 255, "项目名称", required=True)
            validate_string_length(formulator_name, 255, "配方设计师", required=True)
            validate_integer(project_type_fk, min_value=1, field_name="项目类型")
            validate_date_string(formulation_date_str, "配方设计日期")
            if substrate_application:
                validate_string_length(substrate_application, 1000, "目标基材或应用领域", required=False)
        except ValidationError as e:
            flash(str(e), 'warning')
            logger.warning(f"项目添加验证失败: {e}")
            cursor.execute("SELECT * FROM tbl_Config_ProjectTypes")
            project_types = cursor.fetchall()
            cursor.close()
            cnx.close()
            return render_template('project_form.html', project=request.form, project_types=project_types, action='add')

        formulation_date = datetime.strptime(formulation_date_str, '%Y-%m-%d').date()
        
        cursor.execute("SELECT TypeCode FROM tbl_Config_ProjectTypes WHERE TypeID = %s", (project_type_fk,))
        type_code_result = cursor.fetchone()
        type_code = type_code_result['TypeCode'] if type_code_result else 'XXX'
        
        cursor.execute("""
            SELECT COUNT(*) as count FROM tbl_ProjectInfo 
            WHERE FormulationDate = %s AND ProjectType_FK = %s
        """, (formulation_date_str, project_type_fk))
        sequence_num = cursor.fetchone()['count'] + 1
        sequence_str = f"{sequence_num:02d}"

        initials = "".join(c for c in formulator_name if c.isupper()) or formulator_name[:2].upper()
        date_str = formulation_date.strftime('%d%m%Y')
        formula_code = f"{initials}-{date_str}-{type_code}-{sequence_str}"

        sql = """
            INSERT INTO tbl_ProjectInfo 
            (ProjectName, ProjectType_FK, SubstrateApplication, FormulatorName, FormulationDate, FormulaCode)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        values = (
            project_name,
            project_type_fk,
            request.form.get('SubstrateApplication'),
            formulator_name,
            formulation_date,
            formula_code
        )
        cursor.execute(sql, values)
        cnx.commit()
        flash('新项目已成功创建！', 'success')
        cursor.close()
        cnx.close()
        return redirect(url_for('projects.project_list'))

    cursor.execute("SELECT * FROM tbl_Config_ProjectTypes")
    project_types = cursor.fetchall()
    cursor.close()
    cnx.close()
    return render_template('project_form.html', project_types=project_types, action='add', project={})

@projects_bp.route('/project/edit/<int:project_id>', methods=['GET', 'POST'])
def edit_project(project_id):
    """Level 3: Edit an existing project."""
    focus = request.args.get('focus', None) 

    cnx = get_db_connection()
    if not cnx:
        flash("数据库连接失败！", "danger")
        return redirect(url_for('projects.project_list'))
    
    cursor = cnx.cursor(dictionary=True)

    if request.method == 'POST':
        sql = """
            UPDATE tbl_ProjectInfo SET
            ProjectName = %s, ProjectType_FK = %s, SubstrateApplication = %s,
            FormulatorName = %s, FormulationDate = %s
            WHERE ProjectID = %s
        """
        values = (
            request.form.get('ProjectName'),
            request.form.get('ProjectType_FK'),
            request.form.get('SubstrateApplication'),
            request.form.get('FormulatorName'),
            request.form.get('FormulationDate'),
            project_id
        )
        cursor.execute(sql, values)
        cnx.commit()
        flash(f'项目 {project_id} 已更新。', 'success')
        cursor.close()
        cnx.close()
        return redirect(url_for('projects.project_list'))

    cursor.execute("""
        SELECT p.*, pt.TypeName 
        FROM tbl_ProjectInfo p
        LEFT JOIN tbl_Config_ProjectTypes pt ON p.ProjectType_FK = pt.TypeID
        WHERE p.ProjectID = %s
    """, (project_id,))
    project = cursor.fetchone()
    
    cursor.execute("SELECT * FROM tbl_Config_ProjectTypes")
    project_types = cursor.fetchall()
    
    if not project:
        flash(f'未找到项目ID {project_id}。', 'danger')
        cursor.close()
        cnx.close()
        return redirect(url_for('projects.project_list'))
    
    composition_query = """
        SELECT fc.CompositionID, fc.WeightPercentage, fc.AdditionMethod, fc.Remarks,
               rm.TradeName as MaterialName, 
               inf.TradeName as FillerName
        FROM tbl_FormulaComposition fc
        LEFT JOIN tbl_RawMaterials rm ON fc.MaterialID_FK = rm.MaterialID
        LEFT JOIN tbl_InorganicFillers inf ON fc.FillerID_FK = inf.FillerID
        WHERE fc.ProjectID_FK = %s ORDER BY fc.CompositionID
    """
    cursor.execute(composition_query, (project_id,))
    composition = cursor.fetchall()
    
    cursor.execute("SELECT MaterialID, TradeName FROM tbl_RawMaterials ORDER BY TradeName")
    all_materials = cursor.fetchall()
    
    cursor.execute("SELECT FillerID, TradeName FROM tbl_InorganicFillers ORDER BY TradeName")
    all_fillers = cursor.fetchall()
  
    # 根据项目类型查询对应的测试结果表
    test_results = {}
    test_table = get_test_result_table(project.get('TypeName'))
    if test_table:
        cursor.execute(f"SELECT * FROM {test_table} WHERE ProjectID_FK = %s", (project_id,))
        test_results = cursor.fetchone() or {}

    cursor.close()
    cnx.close()
        
    return render_template('project_form.html', 
                           project=project, 
                           project_types=project_types, 
                           action='edit',
                           composition=composition,
                           all_materials=all_materials,
                           all_fillers=all_fillers,
                           test_results=test_results,
                           focus=focus)

@projects_bp.route('/project/test_results/save/<int:project_id>', methods=['POST'])
def save_test_results(project_id):
    """Save or update test results for a project."""
    cnx = get_db_connection()
    cursor = cnx.cursor(dictionary=True)

    # 获取项目类型
    cursor.execute("""
        SELECT pt.TypeName 
        FROM tbl_ProjectInfo p
        LEFT JOIN tbl_Config_ProjectTypes pt ON p.ProjectType_FK = pt.TypeID
        WHERE p.ProjectID = %s
    """, (project_id,))
    project_type = cursor.fetchone()
    
    if not project_type:
        flash('项目不存在！', 'danger')
        cursor.close()
        cnx.close()
        return redirect(url_for('projects.project_list'))
    
    # 根据项目类型确定测试结果表
    test_table = get_test_result_table(project_type['TypeName'])
    if not test_table:
        flash('未知的项目类型！', 'danger')
        cursor.close()
        cnx.close()
        return redirect(url_for('projects.edit_project', project_id=project_id))

    # 检查是否已存在测试结果
    cursor.execute(f"SELECT ResultID FROM {test_table} WHERE ProjectID_FK = %s", (project_id,))
    existing_result = cursor.fetchone()

    form_keys = list(request.form.keys())
    set_clause = ", ".join([f"{key} = %s" for key in form_keys])
    values = [request.form.get(key) or None for key in form_keys]

    if existing_result:
        sql = f"UPDATE {test_table} SET {set_clause} WHERE ProjectID_FK = %s"
        values.append(project_id)
        cursor.execute(sql, tuple(values))
    else:
        columns = ", ".join(form_keys)
        placeholders = ", ".join(["%s"] * len(form_keys))
        sql = f"INSERT INTO {test_table} (ProjectID_FK, {columns}) VALUES (%s, {placeholders})"
        values.insert(0, project_id)
        cursor.execute(sql, tuple(values))

    cnx.commit()
    flash('测试结果已成功保存！', 'success')
    cursor.close()
    cnx.close()

    return redirect(url_for('projects.edit_project', project_id=project_id))

@projects_bp.route('/composition/add', methods=['POST'])
def add_composition():
    """通过AJAX向项目的配方中添加一个新成分。"""
    project_id = request.form.get('project_id')
    component_type = request.form.get('component_type')
    component_id = request.form.get('component_id')
    weight = request.form.get('weight')
    addition_method = request.form.get('addition_method')
    remarks = request.form.get('remarks')

    if not all([project_id, component_type, component_id, weight]):
        return jsonify({'success': False, 'message': '缺少必要参数。'})
    
    # 输入验证
    try:
        project_id = int(project_id)
        component_id = int(component_id)
        weight_decimal = validate_decimal(weight, min_value=0, max_value=100, field_name="重量百分比")
        
        if component_type not in [COMPONENT_TYPE_MATERIAL, COMPONENT_TYPE_FILLER]:
            return jsonify({'success': False, 'message': '无效的组件类型。'})
    except ValidationError as e:
        return jsonify({'success': False, 'message': str(e)})
    except (ValueError, TypeError):
        return jsonify({'success': False, 'message': '参数格式错误。'})

    cnx = get_db_connection()
    if not cnx:
        return jsonify({'success': False, 'message': '数据库连接失败。'})
    cursor = cnx.cursor(dictionary=True)

    try:
        
        cursor.execute("SELECT SUM(WeightPercentage) as total FROM tbl_FormulaComposition WHERE ProjectID_FK = %s", (project_id,))
        result_sum = cursor.fetchone()
        current_total = decimal.Decimal('0')
        if result_sum and result_sum['total'] is not None:
            current_total = result_sum['total']

        if current_total + weight_decimal > decimal.Decimal(str(MAX_FORMULA_WEIGHT_PERCENTAGE)):
            return jsonify({'success': False, 'message': f'添加失败：总重量百分比将超过{MAX_FORMULA_WEIGHT_PERCENTAGE}%。'})

        material_fk = component_id if component_type == 'material' else None
        filler_fk = component_id if component_type == 'filler' else None

        sql = """
            INSERT INTO tbl_FormulaComposition (ProjectID_FK, MaterialID_FK, FillerID_FK, WeightPercentage, AdditionMethod, Remarks)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(sql, (project_id, material_fk, filler_fk, weight_decimal, addition_method, remarks))
        cnx.commit()
        
        new_composition_id = cursor.lastrowid
        
        if component_type == 'material':
            cursor.execute("SELECT TradeName FROM tbl_RawMaterials WHERE MaterialID = %s", (component_id,))
        else:
            cursor.execute("SELECT TradeName FROM tbl_InorganicFillers WHERE FillerID = %s", (component_id,))
        
        name_result = cursor.fetchone()
        if not name_result:
            cnx.rollback()
            return jsonify({'success': False, 'message': f'严重错误：找不到ID为 {component_id} 的成分。'})
            
        component_name = name_result['TradeName']

        return jsonify({
            'success': True, 'message': '成分添加成功！',
            'composition_id': new_composition_id, 'component_name': component_name,
            'weight': str(weight_decimal), 'addition_method': addition_method, 'remarks': remarks
        })
    except decimal.InvalidOperation:
        return jsonify({'success': False, 'message': '无效的重量值。'})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'发生意外的服务器错误: {e}'})
    finally:
        if cnx.is_connected():
            cursor.close()
            cnx.close()

@projects_bp.route('/composition/delete/<int:composition_id>', methods=['POST'])
def delete_composition(composition_id):
    """通过AJAX从项目的配方中删除一个成分。"""
    cnx = get_db_connection()
    cursor = cnx.cursor()
    cursor.execute("DELETE FROM tbl_FormulaComposition WHERE CompositionID = %s", (composition_id,))
    cnx.commit()
    success = cursor.rowcount > 0
    cursor.close()
    cnx.close()
    if success:
        return jsonify({'success': True, 'message': '成分已删除。'})
    else:
        return jsonify({'success': False, 'message': '未找到要删除的成分。'})

@projects_bp.route('/project/batch_action', methods=['POST'])
def batch_action():
    """处理批量操作，如删除和导出。"""
    action = request.form.get('action')
    selected_ids = request.form.getlist('selected_ids')

    if not selected_ids:
        flash('请至少选择一个项目。', 'warning')
        return redirect(url_for('projects.project_list'))

    cnx = get_db_connection()
    if not cnx:
        flash("数据库连接失败！", "danger")
        return redirect(url_for('projects.project_list'))
    
    cursor = cnx.cursor(dictionary=True)

    if action == 'delete':
        placeholders = ','.join(['%s'] * len(selected_ids))
        sql = f"DELETE FROM tbl_ProjectInfo WHERE ProjectID IN ({placeholders})"
        cursor.execute(sql, tuple(selected_ids))
        cnx.commit()
        flash(f'成功删除了 {len(selected_ids)} 个项目。', 'success')
        cursor.close()
        cnx.close()
        return redirect(url_for('projects.project_list'))

    elif action == 'export_csv':
        # 导出选中的项目数据，需要从不同的测试结果表中获取数据
        all_projects_data = []
        
        for project_id in selected_ids:
            # 获取项目基本信息和类型
            cursor.execute("""
                SELECT p.*, pt.TypeName 
                FROM tbl_ProjectInfo p
                LEFT JOIN tbl_Config_ProjectTypes pt ON p.ProjectType_FK = pt.TypeID
                WHERE p.ProjectID = %s
            """, (project_id,))
            project = cursor.fetchone()
            
            if not project:
                continue
            
            # 获取配方成分
            composition_query = """
                SELECT fc.WeightPercentage, fc.AdditionMethod, fc.Remarks,
                       COALESCE(rm.TradeName, inf.TradeName) AS ComponentName,
                       CASE WHEN fc.MaterialID_FK IS NOT NULL THEN '原料'
                            WHEN fc.FillerID_FK IS NOT NULL THEN '无机材料'
                            ELSE 'N/A' END AS ComponentType
                FROM tbl_FormulaComposition fc
                LEFT JOIN tbl_RawMaterials rm ON fc.MaterialID_FK = rm.MaterialID
                LEFT JOIN tbl_InorganicFillers inf ON fc.FillerID_FK = inf.FillerID
                WHERE fc.ProjectID_FK = %s ORDER BY fc.CompositionID
            """
            cursor.execute(composition_query, (project_id,))
            compositions = cursor.fetchall()
            
            # 根据项目类型获取测试结果
            test_results = {}
            test_table = get_test_result_table(project.get('TypeName'))
            if test_table:
                cursor.execute(f"SELECT * FROM {test_table} WHERE ProjectID_FK = %s", (project_id,))
                result = cursor.fetchone()
                if result:
                    test_results = {k: v for k, v in result.items() if k not in ['ResultID', 'ProjectID_FK']}
            
            # 如果没有配方成分，至少导出一行项目数据
            if not compositions:
                row_data = {
                    '项目ID': project['ProjectID'],
                    '项目名称': project['ProjectName'],
                    '项目类型': project.get('TypeName', 'N/A'),
                    '目标基材或应用领域': project.get('SubstrateApplication'),
                    '配方设计师': project.get('FormulatorName'),
                    '设计日期': project.get('FormulationDate'),
                    '配方编码': project.get('FormulaCode'),
                    '成分名称': None,
                    '成分类型': None,
                    '重量百分比(%)': None,
                    '掺入方法': None,
                    '成分备注': None
                }
                row_data.update(test_results)
                all_projects_data.append(row_data)
            else:
                # 为每个成分创建一行
                for comp in compositions:
                    row_data = {
                        '项目ID': project['ProjectID'],
                        '项目名称': project['ProjectName'],
                        '项目类型': project.get('TypeName', 'N/A'),
                        '目标基材或应用领域': project.get('SubstrateApplication'),
                        '配方设计师': project.get('FormulatorName'),
                        '设计日期': project.get('FormulationDate'),
                        '配方编码': project.get('FormulaCode'),
                        '成分名称': comp.get('ComponentName'),
                        '成分类型': comp.get('ComponentType'),
                        '重量百分比(%)': comp.get('WeightPercentage'),
                        '掺入方法': comp.get('AdditionMethod'),
                        '成分备注': comp.get('Remarks')
                    }
                    row_data.update(test_results)
                    all_projects_data.append(row_data)
        
        if not all_projects_data:
            flash('没有找到可导出的数据。', 'info')
            cursor.close()
            cnx.close()
            return redirect(url_for('projects.project_list'))

        # 创建CSV - 收集所有可能的字段名（因为不同项目类型有不同的测试结果字段）
        all_headers = set()
        for row in all_projects_data:
            all_headers.update(row.keys())
        
        # 定义字段顺序：基本信息字段在前，测试结果字段在后
        basic_fields = ['项目ID', '项目名称', '项目类型', '目标基材或应用领域', 
                       '配方设计师', '设计日期', '配方编码', 
                       '成分名称', '成分类型', '重量百分比(%)', '掺入方法', '成分备注']
        
        # 分离基本字段和测试结果字段
        test_result_fields = sorted([h for h in all_headers if h not in basic_fields])
        
        # 组合最终的表头顺序
        ordered_headers = [h for h in basic_fields if h in all_headers] + test_result_fields
        
        # 确保每一行都有所有字段（缺失的填充为None）
        normalized_data = []
        for row in all_projects_data:
            normalized_row = {header: row.get(header, None) for header in ordered_headers}
            normalized_data.append(normalized_row)
        
        si = StringIO()
        writer = csv.DictWriter(si, fieldnames=ordered_headers)
        writer.writeheader()
        for row in normalized_data:
            writer.writerow(row)
        
        output = make_response(si.getvalue().encode('utf-8'))
        output.headers["Content-Disposition"] = "attachment; filename=projects_export.csv"
        output.headers["Content-type"] = "text/csv; charset=utf-8"
        
        cursor.close()
        cnx.close()
        return output
    
    # Fallback if action is not recognized
    cursor.close()
    cnx.close()
    return redirect(url_for('projects.project_list'))


@projects_bp.route('/project/details/<int:project_id>')
def get_project_details(project_id):
    """通过AJAX获取项目的所有详情。(最终健壮版)"""
    cnx = get_db_connection()
    if not cnx:
        return jsonify({'success': False, 'message': '数据库连接失败。'})
    
    cursor = cnx.cursor(dictionary=True)
    
    try:
        # 一次性获取所有需要的数据（包括项目类型）
        cursor.execute("""
            SELECT p.*, pt.TypeName 
            FROM tbl_ProjectInfo p
            LEFT JOIN tbl_Config_ProjectTypes pt ON p.ProjectType_FK = pt.TypeID
            WHERE p.ProjectID = %s
        """, (project_id,))
        project_info = cursor.fetchone()

        composition_query = """
            SELECT fc.WeightPercentage, fc.AdditionMethod, fc.Remarks,
                   rm.TradeName as MaterialName, inf.TradeName as FillerName
            FROM tbl_FormulaComposition fc
            LEFT JOIN tbl_RawMaterials rm ON fc.MaterialID_FK = rm.MaterialID
            LEFT JOIN tbl_InorganicFillers inf ON fc.FillerID_FK = inf.FillerID
            WHERE fc.ProjectID_FK = %s ORDER BY fc.CompositionID
        """
        cursor.execute(composition_query, (project_id,))
        composition = cursor.fetchall()

        # 根据项目类型查询对应的测试结果表
        test_results = None
        if project_info:
            test_table = get_test_result_table(project_info.get('TypeName'))
            if test_table:
                cursor.execute(f"SELECT * FROM {test_table} WHERE ProjectID_FK = %s", (project_id,))
                test_results = cursor.fetchone()

        response_data = {
            'success': True,
            'info': project_info,
            'composition': composition,
            'test_results': test_results
        }
        
        safe_data = make_json_safe(response_data)
        return jsonify(safe_data)

    except Exception as e:
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'服务器在准备数据时发生错误: {e}'}), 500
    finally:
        if cnx and cnx.is_connected():
            cursor.close()
            cnx.close()

@projects_bp.route('/test_results')
def test_results_page():
    """测试结果数据表页面 - 选择项目查看测试结果"""
    cnx = get_db_connection()
    if not cnx:
        flash("数据库连接失败！", "danger")
        return render_template('test_results.html', projects=[])
    
    cursor = cnx.cursor(dictionary=True)
    # 获取所有项目及其类型，用于下拉选择
    query = """
        SELECT p.ProjectID, p.ProjectName, p.FormulaCode, pt.TypeName
        FROM tbl_ProjectInfo p
        LEFT JOIN tbl_Config_ProjectTypes pt ON p.ProjectType_FK = pt.TypeID
        ORDER BY p.ProjectID DESC
    """
    cursor.execute(query)
    projects = cursor.fetchall()
    cursor.close()
    cnx.close()
    
    return render_template('test_results.html', projects=projects)

@projects_bp.route('/test_results/edit/<int:project_id>')
def edit_test_results(project_id):
    """测试结果编辑专用页面"""
    cnx = get_db_connection()
    if not cnx:
        flash("数据库连接失败！", "danger")
        return render_template('test_results_edit.html', project={}, test_results={})
    
    cursor = cnx.cursor(dictionary=True)
    
    try:
        # 获取项目基本信息
        cursor.execute("""
            SELECT p.*, t.TypeName 
            FROM tbl_ProjectInfo p
            LEFT JOIN tbl_Config_ProjectTypes t ON p.ProjectType_FK = t.TypeID
            WHERE p.ProjectID = %s
        """, (project_id,))
        project = cursor.fetchone()
        
        if not project:
            flash("项目不存在！", "danger")
            return render_template('test_results_edit.html', project={}, test_results={})
        
        # 根据项目类型获取测试结果
        test_results = {}
        test_table = get_test_result_table(project.get('TypeName'))
        if test_table:
            cursor.execute(f"SELECT * FROM {test_table} WHERE ProjectID_FK = %s", (project_id,))
            test_results = cursor.fetchone() or {}
        
        return render_template('test_results_edit.html', 
                             project=project, 
                             test_results=test_results)
    
    finally:
        cursor.close()
        cnx.close()