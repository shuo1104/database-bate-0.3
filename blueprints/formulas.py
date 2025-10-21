from flask import Blueprint, render_template, flash
from core.utils import get_db_connection

formulas_bp = Blueprint('formulas', __name__, template_folder='templates')

@formulas_bp.route('/formulas')
def formulas():
    """一个专属页面，用于选择项目并查看其配方。"""
    cnx = get_db_connection()
    if not cnx:
        flash("数据库连接失败！", "danger")
        return render_template('formulas.html', projects=[])
    
    cursor = cnx.cursor(dictionary=True)
    # 获取所有项目以填充选择下拉菜单
    cursor.execute("SELECT ProjectID, ProjectName, FormulaCode FROM tbl_ProjectInfo ORDER BY ProjectID DESC")
    projects = cursor.fetchall()
    cursor.close()
    cnx.close()
    
    return render_template('formulas.html', projects=projects)

@formulas_bp.route('/formula/edit/<int:project_id>')
def edit_formula(project_id):
    """配方编辑专用页面"""
    cnx = get_db_connection()
    if not cnx:
        flash("数据库连接失败！", "danger")
        return render_template('formula_edit.html', project={}, composition=[], materials=[], fillers=[], total_weight=0)
    
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
            return render_template('formula_edit.html', project={}, composition=[], materials=[], fillers=[], total_weight=0)
        
        # 获取配方成分
        cursor.execute("""
            SELECT 
                fc.CompositionID,
                fc.MaterialID_FK,
                fc.FillerID_FK,
                fc.WeightPercentage,
                fc.AdditionMethod,
                fc.Remarks,
                COALESCE(m.TradeName, f.TradeName) AS ComponentName
            FROM tbl_FormulaComposition fc
            LEFT JOIN tbl_RawMaterials m ON fc.MaterialID_FK = m.MaterialID
            LEFT JOIN tbl_InorganicFillers f ON fc.FillerID_FK = f.FillerID
            WHERE fc.ProjectID_FK = %s
            ORDER BY fc.CompositionID
        """, (project_id,))
        composition = cursor.fetchall()
        
        # 计算总重量
        total_weight = sum(item['WeightPercentage'] for item in composition) if composition else 0
        
        # 获取所有原料
        cursor.execute("SELECT MaterialID, TradeName FROM tbl_RawMaterials ORDER BY TradeName")
        materials = cursor.fetchall()
        
        # 获取所有填料
        cursor.execute("SELECT FillerID, TradeName FROM tbl_InorganicFillers ORDER BY TradeName")
        fillers = cursor.fetchall()
        
        return render_template('formula_edit.html', 
                             project=project, 
                             composition=composition, 
                             materials=materials, 
                             fillers=fillers,
                             total_weight=total_weight)
    
    finally:
        cursor.close()
        cnx.close()