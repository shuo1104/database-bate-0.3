# -*- coding: utf-8 -*-
"""
图表生成工具
使用 matplotlib 生成项目报告图表
"""

import io
import matplotlib
matplotlib.use('Agg')  # 使用非交互式后端
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.patches import Rectangle
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from typing import List, Dict, Any, Optional
from datetime import date


# 设置中文字体支持
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans', 'Arial Unicode MS', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题


class ChartGenerator:
    """图表生成器"""
    
    # 行业标准配置（用于雷达图）- 支持中英文项目类型
    INDUSTRY_STANDARDS = {
        '喷墨': {
            'Ink_Viscosity': {'name': 'Viscosity', 'min': 0, 'max': 100, 'unit': 'cP'},
            'Ink_Reactivity': {'name': 'Reactivity', 'min': 0, 'max': 100, 'unit': 's'},
            'Ink_ParticleSize': {'name': 'Particle Size', 'min': 0, 'max': 500, 'unit': 'nm'},
            'Ink_SurfaceTension': {'name': 'Surface Tension', 'min': 0, 'max': 50, 'unit': 'mN/m'},
            'Ink_ColorValue': {'name': 'Colorimetry', 'min': 0, 'max': 100, 'unit': 'Lab*'},
        },
        'Inkjet': {
            'Ink_Viscosity': {'name': 'Viscosity', 'min': 0, 'max': 100, 'unit': 'cP'},
            'Ink_Reactivity': {'name': 'Reactivity', 'min': 0, 'max': 100, 'unit': 's'},
            'Ink_ParticleSize': {'name': 'Particle Size', 'min': 0, 'max': 500, 'unit': 'nm'},
            'Ink_SurfaceTension': {'name': 'Surface Tension', 'min': 0, 'max': 50, 'unit': 'mN/m'},
            'Ink_ColorValue': {'name': 'Colorimetry', 'min': 0, 'max': 100, 'unit': 'Lab*'},
        },
        '涂层': {
            'Coating_Adhesion': {'name': 'Adhesion', 'min': 0, 'max': 100, 'unit': ''},
            'Coating_Transparency': {'name': 'Transparency', 'min': 0, 'max': 100, 'unit': '%'},
            'Coating_SurfaceHardness': {'name': 'Surface Hardness', 'min': 0, 'max': 10, 'unit': 'H'},
            'Coating_ChemicalResistance': {'name': 'Chemical Resistance', 'min': 0, 'max': 100, 'unit': ''},
            'Coating_CostEstimate': {'name': 'Cost Estimate', 'min': 0, 'max': 100, 'unit': 'EUR/kg'},
        },
        'Coating': {
            'Coating_Adhesion': {'name': 'Adhesion', 'min': 0, 'max': 100, 'unit': ''},
            'Coating_Transparency': {'name': 'Transparency', 'min': 0, 'max': 100, 'unit': '%'},
            'Coating_SurfaceHardness': {'name': 'Surface Hardness', 'min': 0, 'max': 10, 'unit': 'H'},
            'Coating_ChemicalResistance': {'name': 'Chemical Resistance', 'min': 0, 'max': 100, 'unit': ''},
            'Coating_CostEstimate': {'name': 'Cost Estimate', 'min': 0, 'max': 100, 'unit': 'EUR/kg'},
        },
        '3D打印': {
            'Print3D_Shrinkage': {'name': 'Shrinkage', 'min': 0, 'max': 10, 'unit': '%'},
            'Print3D_YoungsModulus': {'name': "Young's Modulus", 'min': 0, 'max': 5000, 'unit': 'MPa'},
            'Print3D_FlexuralStrength': {'name': 'Flexural Strength', 'min': 0, 'max': 200, 'unit': 'MPa'},
            'Print3D_ShoreHardness': {'name': 'Shore Hardness', 'min': 0, 'max': 100, 'unit': 'Shore'},
            'Print3D_ImpactResistance': {'name': 'Impact Resistance', 'min': 0, 'max': 100, 'unit': 'kJ/m^2'},
        },
        '3D Printing': {
            'Print3D_Shrinkage': {'name': 'Shrinkage', 'min': 0, 'max': 10, 'unit': '%'},
            'Print3D_YoungsModulus': {'name': "Young's Modulus", 'min': 0, 'max': 5000, 'unit': 'MPa'},
            'Print3D_FlexuralStrength': {'name': 'Flexural Strength', 'min': 0, 'max': 200, 'unit': 'MPa'},
            'Print3D_ShoreHardness': {'name': 'Shore Hardness', 'min': 0, 'max': 100, 'unit': 'Shore'},
            'Print3D_ImpactResistance': {'name': 'Impact Resistance', 'min': 0, 'max': 100, 'unit': 'kJ/m^2'},
        },
        '复合材料': {
            'Composite_FlexuralStrength': {'name': 'Flexural Strength', 'min': 0, 'max': 200, 'unit': 'MPa'},
            'Composite_YoungsModulus': {'name': "Young's Modulus", 'min': 0, 'max': 5000, 'unit': 'MPa'},
            'Composite_ImpactResistance': {'name': 'Impact Resistance', 'min': 0, 'max': 100, 'unit': 'kJ/m^2'},
            'Composite_ConversionRate': {'name': 'Degree of Conversion', 'min': 0, 'max': 100, 'unit': '%'},
            'Composite_WaterAbsorption': {'name': 'Water Absorption', 'min': 0, 'max': 10, 'unit': '%'},
        },
        'Composite': {
            'Composite_FlexuralStrength': {'name': 'Flexural Strength', 'min': 0, 'max': 200, 'unit': 'MPa'},
            'Composite_YoungsModulus': {'name': "Young's Modulus", 'min': 0, 'max': 5000, 'unit': 'MPa'},
            'Composite_ImpactResistance': {'name': 'Impact Resistance', 'min': 0, 'max': 100, 'unit': 'kJ/m^2'},
            'Composite_ConversionRate': {'name': 'Degree of Conversion', 'min': 0, 'max': 100, 'unit': '%'},
            'Composite_WaterAbsorption': {'name': 'Water Absorption', 'min': 0, 'max': 10, 'unit': '%'},
        }
    }
    
    @staticmethod
    def create_project_info_table(project_data: Dict[str, Any]) -> Image.Image:
        """
        创建项目信息表格图片
        
        Args:
            project_data: 项目数据字典
            
        Returns:
            PIL Image对象
        """
        # 创建画布（更高分辨率）
        img_width = 1600
        img_height = 700
        img = Image.new('RGB', (img_width, img_height), 'white')
        draw = ImageDraw.Draw(img)
        
        # 尝试加载字体（更大的字号）
        try:
            title_font = ImageFont.truetype("simhei.ttf", 48)
            header_font = ImageFont.truetype("simhei.ttf", 32)
            content_font = ImageFont.truetype("simhei.ttf", 28)
        except:
            try:
                title_font = ImageFont.truetype("Arial Unicode MS", 48)
                header_font = ImageFont.truetype("Arial Unicode MS", 32)
                content_font = ImageFont.truetype("Arial Unicode MS", 28)
            except:
                title_font = ImageFont.load_default()
                header_font = ImageFont.load_default()
                content_font = ImageFont.load_default()
        
        # 标题（居中）
        title = "Project Information"
        title_bbox = draw.textbbox((0, 0), title, font=title_font)
        title_width = title_bbox[2] - title_bbox[0]
        draw.text(((img_width - title_width) // 2, 40), title, fill='#333333', font=title_font)
        
        # 表格数据
        table_data = [
            ('Project ID', str(project_data.get('ProjectID', 'N/A'))),
            ('Project Name', project_data.get('ProjectName', 'N/A')),
            ('Project Type', project_data.get('TypeName', 'N/A')),
            ('Formula Code', project_data.get('FormulaCode', 'N/A')),
            ('Formulator', project_data.get('FormulatorName', 'N/A')),
            ('Formulation Date', str(project_data.get('FormulationDate', 'N/A'))),
            ('Substrate/Application', project_data.get('SubstrateApplication', 'N/A')[:30] if project_data.get('SubstrateApplication') else 'N/A'),
        ]
        
        # 绘制表格（居中）
        y_offset = 160
        row_height = 70
        col1_width = 300
        col2_width = 900
        table_width = col1_width + col2_width
        x_start = (img_width - table_width) // 2  # 居中起始位置
        
        for i, (label, value) in enumerate(table_data):
            # 绘制边框
            draw.rectangle(
                [(x_start, y_offset), (x_start + col1_width, y_offset + row_height)],
                outline='#cccccc',
                width=2,
                fill='#f5f5f5'
            )
            draw.rectangle(
                [(x_start + col1_width, y_offset), (x_start + col1_width + col2_width, y_offset + row_height)],
                outline='#cccccc',
                width=2
            )
            
            # 绘制文本
            draw.text((x_start + 20, y_offset + 16), label, fill='#333333', font=header_font)
            draw.text((x_start + col1_width + 20, y_offset + 16), str(value), fill='#666666', font=content_font)
            
            y_offset += row_height
        
        return img
    
    @staticmethod
    def create_composition_bar_chart(compositions: List[Dict[str, Any]]) -> bytes:
        """
        创建配方成分柱状图
        
        Args:
            compositions: 配方成分列表
            
        Returns:
            PNG图片字节数据
        """
        if not compositions:
            # 创建空图表
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.text(0.5, 0.5, 'No composition data available', 
                   ha='center', va='center', fontsize=16, color='gray')
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')
        else:
            # 准备数据
            names = []
            percentages = []
            colors_list = []
            
            for comp in compositions:
                # 获取成分名称
                name = comp.get('MaterialName') or comp.get('FillerName') or '未知成分'
                if len(name) > 15:
                    name = name[:15] + '...'
                names.append(name)
                
                # 获取百分比
                percentage = float(comp.get('WeightPercentage', 0))
                percentages.append(percentage)
                
                # 根据类型设置颜色
                if comp.get('MaterialName'):
                    colors_list.append('#5470c6')  # 蓝色 - 原料
                else:
                    colors_list.append('#91cc75')  # 绿色 - 填料
            
            # 创建图表
            fig, ax = plt.subplots(figsize=(12, 6))
            bars = ax.bar(range(len(names)), percentages, color=colors_list, alpha=0.8, edgecolor='black')
            
            # 在柱子上显示数值
            for i, (bar, percentage) in enumerate(zip(bars, percentages)):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{percentage:.2f}%',
                       ha='center', va='bottom', fontsize=10, fontweight='bold')
            
            # 设置标签和标题
            ax.set_xlabel('Component Name', fontsize=12, fontweight='bold')
            ax.set_ylabel('Weight Percentage (%)', fontsize=12, fontweight='bold')
            ax.set_title('Formula Composition', fontsize=14, fontweight='bold', pad=20)
            ax.set_xticks(range(len(names)))
            ax.set_xticklabels(names, rotation=45, ha='right')
            
            # 添加网格
            ax.yaxis.grid(True, linestyle='--', alpha=0.7)
            ax.set_axisbelow(True)
            
            # 添加图例
            from matplotlib.patches import Patch
            legend_elements = [
                Patch(facecolor='#5470c6', label='Material'),
                Patch(facecolor='#91cc75', label='Filler')
            ]
            ax.legend(handles=legend_elements, loc='upper right')
            
            plt.tight_layout()
        
        # 保存到字节流（提高DPI）
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=300, bbox_inches='tight')
        plt.close(fig)
        buf.seek(0)
        return buf.getvalue()
    
    @staticmethod
    def create_test_result_radar_chart(
        test_results: Dict[str, Any],
        project_type: str
    ) -> bytes:
        """
        创建测试结果雷达图
        
        Args:
            test_results: 测试结果数据
            project_type: 项目类型
            
        Returns:
            PNG图片字节数据
        """
        # 获取该项目类型的行业标准
        standards = ChartGenerator.INDUSTRY_STANDARDS.get(project_type, {})
        
        if not standards or not test_results:
            # 创建空图表
            fig, ax = plt.subplots(figsize=(8, 8))
            ax.text(0.5, 0.5, f'No test data available for {project_type}', 
                   ha='center', va='center', fontsize=16, color='gray')
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')
        else:
            # 准备数据
            categories = []
            values = []
            
            for field, standard in standards.items():
                value_str = test_results.get(field)
                if value_str:
                    try:
                        # 尝试从字符串中提取数值
                        import re
                        numbers = re.findall(r'-?\d+\.?\d*', str(value_str))
                        if numbers:
                            value = float(numbers[0])
                            # 标准化到0-100范围
                            max_val = standard['max']
                            min_val = standard['min']
                            normalized_value = ((value - min_val) / (max_val - min_val)) * 100
                            normalized_value = max(0, min(100, normalized_value))  # 限制在0-100
                            
                            categories.append(standard['name'])
                            values.append(normalized_value)
                    except:
                        pass
            
            if not categories:
                # 没有有效数据
                fig, ax = plt.subplots(figsize=(8, 8))
                ax.text(0.5, 0.5, 'Invalid test result data format', 
                       ha='center', va='center', fontsize=16, color='gray')
                ax.set_xlim(0, 1)
                ax.set_ylim(0, 1)
                ax.axis('off')
            else:
                # 创建雷达图
                num_vars = len(categories)
                angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
                values += values[:1]  # 闭合图形
                angles += angles[:1]
                
                fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
                
                # 绘制数据
                ax.plot(angles, values, 'o-', linewidth=2, label='Measured', color='#5470c6')
                ax.fill(angles, values, alpha=0.25, color='#5470c6')
                
                # 绘制标准参考线（假设标准值为80%）
                reference = [80] * (num_vars + 1)
                ax.plot(angles, reference, '--', linewidth=1.5, label='Reference (80%)', color='#ee6666', alpha=0.7)
                
                # 设置标签
                ax.set_xticks(angles[:-1])
                ax.set_xticklabels(categories, fontsize=11)
                
                # 设置范围和网格
                ax.set_ylim(0, 100)
                ax.set_yticks([20, 40, 60, 80, 100])
                ax.set_yticklabels(['20', '40', '60', '80', '100'], fontsize=9)
                ax.grid(True, linestyle='--', alpha=0.7)
                
                # 标题和图例
                ax.set_title(f'{project_type} - Test Results Radar Chart\n(Normalized: 0-100)', 
                           fontsize=14, fontweight='bold', pad=30)
                ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=10)
        
        # 保存到字节流（提高DPI）
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=300, bbox_inches='tight')
        plt.close(fig)
        buf.seek(0)
        return buf.getvalue()
    
    @staticmethod
    def create_composition_table(compositions: List[Dict[str, Any]]) -> Image.Image:
        """
        创建配料信息表格图片
        
        Args:
            compositions: 配料成分列表
            
        Returns:
            PIL Image对象
        """
        # 创建画布 - 根据行数动态调整高度（更高分辨率）
        img_width = 1600
        row_height = 70
        header_height = 160
        num_rows = len(compositions) if compositions else 1
        img_height = header_height + row_height * (num_rows + 1) + 60  # 标题 + 表头 + 数据行 + 底部边距
        
        img = Image.new('RGB', (img_width, img_height), 'white')
        draw = ImageDraw.Draw(img)
        
        # 尝试加载字体（更大的字号）
        try:
            title_font = ImageFont.truetype("simhei.ttf", 48)
            header_font = ImageFont.truetype("simhei.ttf", 28)
            content_font = ImageFont.truetype("simhei.ttf", 24)
        except:
            try:
                title_font = ImageFont.truetype("Arial Unicode MS", 48)
                header_font = ImageFont.truetype("Arial Unicode MS", 28)
                content_font = ImageFont.truetype("Arial Unicode MS", 24)
            except:
                title_font = ImageFont.load_default()
                header_font = ImageFont.load_default()
                content_font = ImageFont.load_default()
        
        # 标题（居中）
        title = "Composition Information"
        title_bbox = draw.textbbox((0, 0), title, font=title_font)
        title_width = title_bbox[2] - title_bbox[0]
        draw.text(((img_width - title_width) // 2, 40), title, fill='#333333', font=title_font)
        
        # 表格列宽
        col_widths = [120, 600, 280, 400]  # 序号、成分名称、类型、百分比
        col_names = ['No.', 'Component', 'Type', 'Weight%']  # 使用英文列名避免乱码
        table_width = sum(col_widths)
        x_start = (img_width - table_width) // 2  # 居中起始位置
        
        # 绘制表头
        y_offset = header_height
        x_offset = x_start
        for i, (col_name, col_width) in enumerate(zip(col_names, col_widths)):
            draw.rectangle(
                [(x_offset, y_offset), (x_offset + col_width, y_offset + row_height)],
                outline='#cccccc',
                width=2,
                fill='#f5f5f5'
            )
            draw.text((x_offset + 20, y_offset + 16), col_name, fill='#333333', font=header_font)
            x_offset += col_width
        
        # 绘制数据行
        y_offset += row_height
        if compositions:
            for idx, comp in enumerate(compositions, 1):
                x_offset = x_start
                # 序号
                draw.rectangle(
                    [(x_offset, y_offset), (x_offset + col_widths[0], y_offset + row_height)],
                    outline='#cccccc',
                    width=2
                )
                draw.text((x_offset + 40, y_offset + 16), str(idx), fill='#666666', font=content_font)
                x_offset += col_widths[0]
                
                # 成分名称
                name = comp.get('MaterialName') or comp.get('FillerName') or '未知'
                if len(name) > 20:
                    name = name[:20] + '...'
                draw.rectangle(
                    [(x_offset, y_offset), (x_offset + col_widths[1], y_offset + row_height)],
                    outline='#cccccc',
                    width=2
                )
                draw.text((x_offset + 20, y_offset + 16), name, fill='#666666', font=content_font)
                x_offset += col_widths[1]
                
                # 类型（使用英文避免乱码）
                comp_type = 'Material' if comp.get('MaterialName') else 'Filler'
                draw.rectangle(
                    [(x_offset, y_offset), (x_offset + col_widths[2], y_offset + row_height)],
                    outline='#cccccc',
                    width=2
                )
                draw.text((x_offset + 70, y_offset + 16), comp_type, fill='#666666', font=content_font)
                x_offset += col_widths[2]
                
                # 重量百分比
                percentage = f"{float(comp.get('WeightPercentage', 0)):.2f}%"
                draw.rectangle(
                    [(x_offset, y_offset), (x_offset + col_widths[3], y_offset + row_height)],
                    outline='#cccccc',
                    width=2
                )
                draw.text((x_offset + 150, y_offset + 16), percentage, fill='#666666', font=content_font)
                x_offset += col_widths[3]
                
                y_offset += row_height
        else:
            # 无数据提示
            x_offset = x_start
            total_width = sum(col_widths)
            draw.rectangle(
                [(x_offset, y_offset), (x_offset + total_width, y_offset + row_height)],
                outline='#cccccc',
                width=2
            )
            # 居中显示提示文本
            hint_text = "No composition data available"  # 使用英文避免字体问题
            try:
                hint_bbox = draw.textbbox((0, 0), hint_text, font=content_font)
                hint_width = hint_bbox[2] - hint_bbox[0]
                draw.text((x_offset + (total_width - hint_width) // 2, y_offset + 16), 
                         hint_text, fill='#999999', font=content_font)
            except:
                # 如果textbbox失败，使用估算位置
                draw.text((x_offset + 500, y_offset + 16), hint_text, fill='#999999', font=content_font)
        
        return img
    
    @staticmethod
    def create_test_result_table(test_results: Dict[str, Any], project_type: str) -> Image.Image:
        """
        创建测试结果表格图片
        
        Args:
            test_results: 测试结果数据
            project_type: 项目类型
            
        Returns:
            PIL Image对象
        """
        # 获取该项目类型的行业标准
        standards = ChartGenerator.INDUSTRY_STANDARDS.get(project_type, {})
        
        # 创建画布 - 根据行数动态调整高度（更高分辨率）
        img_width = 1600
        row_height = 70
        header_height = 160
        num_rows = len(standards) if standards else 1
        img_height = header_height + row_height * (num_rows + 1) + 60
        
        img = Image.new('RGB', (img_width, img_height), 'white')
        draw = ImageDraw.Draw(img)
        
        # 尝试加载字体（更大的字号）
        try:
            title_font = ImageFont.truetype("simhei.ttf", 48)
            header_font = ImageFont.truetype("simhei.ttf", 28)
            content_font = ImageFont.truetype("simhei.ttf", 24)
        except:
            try:
                title_font = ImageFont.truetype("Arial Unicode MS", 48)
                header_font = ImageFont.truetype("Arial Unicode MS", 28)
                content_font = ImageFont.truetype("Arial Unicode MS", 24)
            except:
                title_font = ImageFont.load_default()
                header_font = ImageFont.load_default()
                content_font = ImageFont.load_default()
        
        # 标题（居中）
        title = "Test Results"
        title_bbox = draw.textbbox((0, 0), title, font=title_font)
        title_width = title_bbox[2] - title_bbox[0]
        draw.text(((img_width - title_width) // 2, 40), title, fill='#333333', font=title_font)
        
        # 表格列宽
        col_widths = [120, 480, 500, 400]  # 序号、指标名称、测试值、单位
        col_names = ['No.', 'Index', 'Value', 'Unit']  # 使用英文列名避免乱码
        table_width = sum(col_widths)
        x_start = (img_width - table_width) // 2  # 居中起始位置
        
        # 绘制表头
        y_offset = header_height
        x_offset = x_start
        for col_name, col_width in zip(col_names, col_widths):
            draw.rectangle(
                [(x_offset, y_offset), (x_offset + col_width, y_offset + row_height)],
                outline='#cccccc',
                width=2,
                fill='#f5f5f5'
            )
            draw.text((x_offset + 20, y_offset + 16), col_name, fill='#333333', font=header_font)
            x_offset += col_width
        
        # 绘制数据行
        y_offset += row_height
        if standards and test_results:
            idx = 1
            for field, standard in standards.items():
                value_str = test_results.get(field, '-')
                
                x_offset = x_start
                # 序号
                draw.rectangle(
                    [(x_offset, y_offset), (x_offset + col_widths[0], y_offset + row_height)],
                    outline='#cccccc',
                    width=2
                )
                draw.text((x_offset + 40, y_offset + 16), str(idx), fill='#666666', font=content_font)
                x_offset += col_widths[0]
                
                # 指标名称（也处理特殊字符）
                index_name = standard['name']
                # 替换指标名称中可能包含的特殊字符
                name_replacements = {
                    '²': '^2',
                    '³': '^3',
                    '°': 'deg',
                    '℃': 'C',
                    'μ': 'u',
                    '·': '.',
                    '～': '~',
                    '—': '-'
                }
                for old_char, new_char in name_replacements.items():
                    index_name = index_name.replace(old_char, new_char)
                
                draw.rectangle(
                    [(x_offset, y_offset), (x_offset + col_widths[1], y_offset + row_height)],
                    outline='#cccccc',
                    width=2
                )
                draw.text((x_offset + 20, y_offset + 16), index_name, fill='#666666', font=content_font)
                x_offset += col_widths[1]
                
                # 测试值（也处理特殊字符）
                value_display = str(value_str)[:35]
                # 替换测试值中可能包含的特殊字符
                value_replacements = {
                    '²': '^2',
                    '³': '^3',
                    '°': 'deg',
                    '℃': 'C',
                    'μ': 'u',
                    '·': '.',
                    '～': '~',
                    '—': '-'
                }
                for old_char, new_char in value_replacements.items():
                    value_display = value_display.replace(old_char, new_char)
                
                draw.rectangle(
                    [(x_offset, y_offset), (x_offset + col_widths[2], y_offset + row_height)],
                    outline='#cccccc',
                    width=2
                )
                draw.text((x_offset + 20, y_offset + 16), value_display, fill='#666666', font=content_font)
                x_offset += col_widths[2]
                
                # 单位（处理特殊字符，使用ASCII安全字符）
                unit_text = standard['unit']
                # 替换所有可能导致乱码的特殊字符为ASCII安全字符
                unit_replacements = {
                    '²': '^2',
                    '³': '^3',
                    '°': 'deg',
                    '℃': 'C',
                    'μ': 'u',
                    '·': '.',
                    '～': '~',
                    '—': '-'
                }
                for old_char, new_char in unit_replacements.items():
                    unit_text = unit_text.replace(old_char, new_char)
                
                draw.rectangle(
                    [(x_offset, y_offset), (x_offset + col_widths[3], y_offset + row_height)],
                    outline='#cccccc',
                    width=2
                )
                draw.text((x_offset + 150, y_offset + 16), unit_text, fill='#666666', font=content_font)
                x_offset += col_widths[3]
                
                y_offset += row_height
                idx += 1
        else:
            # 无数据提示
            x_offset = x_start
            total_width = sum(col_widths)
            draw.rectangle(
                [(x_offset, y_offset), (x_offset + total_width, y_offset + row_height)],
                outline='#cccccc',
                width=2
            )
            # 居中显示提示文本
            hint_text = "No test data available"  # 使用英文避免字体问题
            try:
                hint_bbox = draw.textbbox((0, 0), hint_text, font=content_font)
                hint_width = hint_bbox[2] - hint_bbox[0]
                draw.text((x_offset + (total_width - hint_width) // 2, y_offset + 16), 
                         hint_text, fill='#999999', font=content_font)
            except:
                # 如果textbbox失败，使用估算位置
                draw.text((x_offset + 500, y_offset + 16), hint_text, fill='#999999', font=content_font)
        
        return img
    
    @staticmethod
    def combine_images_vertical(
        project_info_img: Image.Image,
        composition_table_img: Image.Image,
        bar_chart_bytes: bytes,
        test_result_table_img: Image.Image,
        radar_chart_bytes: bytes
    ) -> bytes:
        """
        垂直组合五张图片
        
        Args:
            project_info_img: 项目信息表PIL Image
            composition_table_img: 配料信息表PIL Image
            bar_chart_bytes: 柱状图字节数据
            test_result_table_img: 测试结果表PIL Image
            radar_chart_bytes: 雷达图字节数据
            
        Returns:
            组合后的PNG字节数据
        """
        # 加载图表图片
        bar_chart_img = Image.open(io.BytesIO(bar_chart_bytes))
        radar_chart_img = Image.open(io.BytesIO(radar_chart_bytes))
        
        # 统一宽度（使用最大宽度）
        max_width = max(
            project_info_img.width,
            composition_table_img.width,
            bar_chart_img.width,
            test_result_table_img.width,
            radar_chart_img.width
        )
        
        # 调整所有图片宽度
        images = [
            project_info_img,
            composition_table_img,
            bar_chart_img,
            test_result_table_img,
            radar_chart_img
        ]
        
        resized_images = []
        for img in images:
            if img.width < max_width:
                new_height = int(img.height * max_width / img.width)
                img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
            resized_images.append(img)
        
        # 计算总高度（添加间距）
        spacing = 30
        total_height = sum(img.height for img in resized_images) + spacing * (len(resized_images) - 1)
        
        # 创建组合图片
        combined_img = Image.new('RGB', (max_width, total_height), 'white')
        
        # 粘贴图片
        y_offset = 0
        for img in resized_images:
            combined_img.paste(img, (0, y_offset))
            y_offset += img.height + spacing
        
        # 保存到字节流
        buf = io.BytesIO()
        combined_img.save(buf, format='PNG', quality=95)
        buf.seek(0)
        return buf.getvalue()

