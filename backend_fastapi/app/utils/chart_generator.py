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
    
    # 行业标准配置（用于雷达图）
    INDUSTRY_STANDARDS = {
        '喷墨': {
            'Ink_Viscosity': {'name': '粘度', 'min': 0, 'max': 100, 'unit': 'cP'},
            'Ink_Reactivity': {'name': '反应活性', 'min': 0, 'max': 100, 'unit': 's'},
            'Ink_ParticleSize': {'name': '粒径', 'min': 0, 'max': 500, 'unit': 'nm'},
            'Ink_SurfaceTension': {'name': '表面张力', 'min': 0, 'max': 50, 'unit': 'mN/m'},
            'Ink_ColorValue': {'name': '色度', 'min': 0, 'max': 100, 'unit': 'Lab*'},
        },
        '涂层': {
            'Coating_Adhesion': {'name': '附着力', 'min': 0, 'max': 100, 'unit': ''},
            'Coating_Transparency': {'name': '透明度', 'min': 0, 'max': 100, 'unit': '%'},
            'Coating_SurfaceHardness': {'name': '表面硬度', 'min': 0, 'max': 10, 'unit': 'H'},
            'Coating_ChemicalResistance': {'name': '耐化学性', 'min': 0, 'max': 100, 'unit': ''},
            'Coating_CostEstimate': {'name': '成本估算', 'min': 0, 'max': 100, 'unit': '€/kg'},
        },
        '3D打印': {
            'Print3D_Shrinkage': {'name': '收缩率', 'min': 0, 'max': 10, 'unit': '%'},
            'Print3D_YoungsModulus': {'name': '杨氏模量', 'min': 0, 'max': 5000, 'unit': 'MPa'},
            'Print3D_FlexuralStrength': {'name': '弯曲强度', 'min': 0, 'max': 200, 'unit': 'MPa'},
            'Print3D_ShoreHardness': {'name': '邵氏硬度', 'min': 0, 'max': 100, 'unit': 'Shore'},
            'Print3D_ImpactResistance': {'name': '抗冲击性', 'min': 0, 'max': 100, 'unit': 'kJ/m²'},
        },
        '复合材料': {
            'Composite_FlexuralStrength': {'name': '弯曲强度', 'min': 0, 'max': 200, 'unit': 'MPa'},
            'Composite_YoungsModulus': {'name': '杨氏模量', 'min': 0, 'max': 5000, 'unit': 'MPa'},
            'Composite_ImpactResistance': {'name': '抗冲击性', 'min': 0, 'max': 100, 'unit': 'kJ/m²'},
            'Composite_ConversionRate': {'name': '转化率', 'min': 0, 'max': 100, 'unit': '%'},
            'Composite_WaterAbsorption': {'name': '吸水率', 'min': 0, 'max': 10, 'unit': '%'},
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
        # 创建画布
        img_width = 800
        img_height = 350
        img = Image.new('RGB', (img_width, img_height), 'white')
        draw = ImageDraw.Draw(img)
        
        # 尝试加载字体
        try:
            title_font = ImageFont.truetype("simhei.ttf", 24)
            header_font = ImageFont.truetype("simhei.ttf", 16)
            content_font = ImageFont.truetype("simhei.ttf", 14)
        except:
            try:
                title_font = ImageFont.truetype("Arial Unicode MS", 24)
                header_font = ImageFont.truetype("Arial Unicode MS", 16)
                content_font = ImageFont.truetype("Arial Unicode MS", 14)
            except:
                title_font = ImageFont.load_default()
                header_font = ImageFont.load_default()
                content_font = ImageFont.load_default()
        
        # 标题
        title = "项目信息表"
        draw.text((img_width // 2 - 80, 20), title, fill='#333333', font=title_font)
        
        # 表格数据
        table_data = [
            ('项目ID', str(project_data.get('ProjectID', 'N/A'))),
            ('项目名称', project_data.get('ProjectName', 'N/A')),
            ('项目类型', project_data.get('TypeName', 'N/A')),
            ('配方编号', project_data.get('FormulaCode', 'N/A')),
            ('配方设计师', project_data.get('FormulatorName', 'N/A')),
            ('配方日期', str(project_data.get('FormulationDate', 'N/A'))),
            ('目标基材', project_data.get('SubstrateApplication', 'N/A')[:30] if project_data.get('SubstrateApplication') else 'N/A'),
        ]
        
        # 绘制表格
        y_offset = 80
        row_height = 35
        col1_width = 150
        col2_width = 600
        
        for i, (label, value) in enumerate(table_data):
            # 绘制边框
            draw.rectangle(
                [(50, y_offset), (50 + col1_width, y_offset + row_height)],
                outline='#cccccc',
                width=1,
                fill='#f5f5f5'
            )
            draw.rectangle(
                [(50 + col1_width, y_offset), (50 + col1_width + col2_width, y_offset + row_height)],
                outline='#cccccc',
                width=1
            )
            
            # 绘制文本
            draw.text((60, y_offset + 8), label, fill='#333333', font=header_font)
            draw.text((60 + col1_width, y_offset + 8), str(value), fill='#666666', font=content_font)
            
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
            ax.text(0.5, 0.5, '暂无配方成分数据', 
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
            ax.set_xlabel('成分名称', fontsize=12, fontweight='bold')
            ax.set_ylabel('重量百分比 (%)', fontsize=12, fontweight='bold')
            ax.set_title('配方成分组成', fontsize=14, fontweight='bold', pad=20)
            ax.set_xticks(range(len(names)))
            ax.set_xticklabels(names, rotation=45, ha='right')
            
            # 添加网格
            ax.yaxis.grid(True, linestyle='--', alpha=0.7)
            ax.set_axisbelow(True)
            
            # 添加图例
            from matplotlib.patches import Patch
            legend_elements = [
                Patch(facecolor='#5470c6', label='原料'),
                Patch(facecolor='#91cc75', label='填料')
            ]
            ax.legend(handles=legend_elements, loc='upper right')
            
            plt.tight_layout()
        
        # 保存到字节流
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
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
            ax.text(0.5, 0.5, f'暂无{project_type}测试结果数据', 
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
                ax.text(0.5, 0.5, '测试结果数据格式无效', 
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
                ax.plot(angles, values, 'o-', linewidth=2, label='实测值', color='#5470c6')
                ax.fill(angles, values, alpha=0.25, color='#5470c6')
                
                # 绘制标准参考线（假设标准值为80%）
                reference = [80] * (num_vars + 1)
                ax.plot(angles, reference, '--', linewidth=1.5, label='参考标准(80%)', color='#ee6666', alpha=0.7)
                
                # 设置标签
                ax.set_xticks(angles[:-1])
                ax.set_xticklabels(categories, fontsize=11)
                
                # 设置范围和网格
                ax.set_ylim(0, 100)
                ax.set_yticks([20, 40, 60, 80, 100])
                ax.set_yticklabels(['20', '40', '60', '80', '100'], fontsize=9)
                ax.grid(True, linestyle='--', alpha=0.7)
                
                # 标题和图例
                ax.set_title(f'{project_type} - 测试结果雷达图\n(标准化值: 0-100)', 
                           fontsize=14, fontweight='bold', pad=30)
                ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=10)
        
        # 保存到字节流
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
        plt.close(fig)
        buf.seek(0)
        return buf.getvalue()
    
    @staticmethod
    def combine_images_vertical(
        project_info_img: Image.Image,
        bar_chart_bytes: bytes,
        radar_chart_bytes: bytes
    ) -> bytes:
        """
        垂直组合三张图片
        
        Args:
            project_info_img: 项目信息表PIL Image
            bar_chart_bytes: 柱状图字节数据
            radar_chart_bytes: 雷达图字节数据
            
        Returns:
            组合后的PNG字节数据
        """
        # 加载图表图片
        bar_chart_img = Image.open(io.BytesIO(bar_chart_bytes))
        radar_chart_img = Image.open(io.BytesIO(radar_chart_bytes))
        
        # 统一宽度（使用最大宽度）
        max_width = max(project_info_img.width, bar_chart_img.width, radar_chart_img.width)
        
        # 调整图片宽度
        if project_info_img.width < max_width:
            new_height = int(project_info_img.height * max_width / project_info_img.width)
            project_info_img = project_info_img.resize((max_width, new_height), Image.Resampling.LANCZOS)
        
        if bar_chart_img.width < max_width:
            new_height = int(bar_chart_img.height * max_width / bar_chart_img.width)
            bar_chart_img = bar_chart_img.resize((max_width, new_height), Image.Resampling.LANCZOS)
        
        if radar_chart_img.width < max_width:
            new_height = int(radar_chart_img.height * max_width / radar_chart_img.width)
            radar_chart_img = radar_chart_img.resize((max_width, new_height), Image.Resampling.LANCZOS)
        
        # 计算总高度（添加间距）
        spacing = 30
        total_height = (project_info_img.height + bar_chart_img.height + 
                       radar_chart_img.height + spacing * 2)
        
        # 创建组合图片
        combined_img = Image.new('RGB', (max_width, total_height), 'white')
        
        # 粘贴图片
        y_offset = 0
        combined_img.paste(project_info_img, (0, y_offset))
        y_offset += project_info_img.height + spacing
        
        combined_img.paste(bar_chart_img, (0, y_offset))
        y_offset += bar_chart_img.height + spacing
        
        combined_img.paste(radar_chart_img, (0, y_offset))
        
        # 保存到字节流
        buf = io.BytesIO()
        combined_img.save(buf, format='PNG', quality=95)
        buf.seek(0)
        return buf.getvalue()

