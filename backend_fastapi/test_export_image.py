#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试图片导出功能
"""
import asyncio
import sys
sys.path.insert(0, '.')

from app.core.database import AsyncSessionLocal
from app.api.v1.modules.projects.crud import ProjectCRUD
from app.utils.chart_generator import ChartGenerator
from app.api.v1.modules.test_results.service import TestResultService


async def test_export_image(project_id: int = 2017):
    """测试图片导出"""
    print(f"开始测试项目 {project_id} 的图片导出...")
    
    async with AsyncSessionLocal() as db:
        try:
            # 1. 获取项目
            print("1. 获取项目详情...")
            project = await ProjectCRUD.get_by_id(db, project_id)
            if not project:
                print(f"错误：项目 {project_id} 不存在")
                return
            
            print(f"   项目名称: {project.ProjectName}")
            print(f"   项目类型: {project.project_type.TypeName if project.project_type else 'N/A'}")
            
            # 2. 准备项目数据
            print("\n2. 准备项目数据...")
            project_data = {
                'ProjectID': project.ProjectID,
                'ProjectName': project.ProjectName,
                'TypeName': project.project_type.TypeName if project.project_type else 'N/A',
                'FormulaCode': project.FormulaCode,
                'FormulatorName': project.FormulatorName,
                'FormulationDate': project.FormulationDate,
                'SubstrateApplication': project.SubstrateApplication,
            }
            print(f"   项目数据: {project_data}")
            
            # 3. 获取配方成分
            print("\n3. 获取配方成分...")
            compositions = []
            if project.compositions:
                for comp in project.compositions:
                    comp_data = {
                        'WeightPercentage': float(comp.WeightPercentage),
                        'MaterialName': comp.material.TradeName if comp.material else None,
                        'FillerName': comp.filler.TradeName if comp.filler else None,
                    }
                    compositions.append(comp_data)
                print(f"   配方成分数量: {len(compositions)}")
            else:
                print("   无配方成分")
            
            # 4. 获取测试结果
            print("\n4. 获取测试结果...")
            test_results = {}
            project_type_name = project_data['TypeName']
            if project_type_name and project_type_name != 'N/A':
                try:
                    test_result = await TestResultService.get_test_result_by_project_id(
                        db, project_id, project_type_name
                    )
                    if test_result:
                        test_results = {k: v for k, v in test_result.__dict__.items() 
                                      if not k.startswith('_') and k not in ['ResultID', 'ProjectID_FK', 'TestDate', 'Notes']}
                        print(f"   测试结果: {list(test_results.keys())}")
                    else:
                        print("   无测试结果")
                except Exception as e:
                    print(f"   获取测试结果失败: {e}")
            
            # 5. 生成图片
            print("\n5. 生成图片...")
            try:
                print("   5.1 创建项目信息表...")
                info_img = ChartGenerator.create_project_info_table(project_data)
                print(f"      项目信息表大小: {info_img.size}")
                
                print("   5.2 创建配方成分柱状图...")
                bar_chart_bytes = ChartGenerator.create_composition_bar_chart(compositions)
                print(f"      柱状图大小: {len(bar_chart_bytes)} bytes")
                
                print("   5.3 创建测试结果雷达图...")
                radar_chart_bytes = ChartGenerator.create_test_result_radar_chart(
                    test_results, project_type_name
                )
                print(f"      雷达图大小: {len(radar_chart_bytes)} bytes")
                
                print("   5.4 组合图片...")
                combined_image_bytes = ChartGenerator.combine_images_vertical(
                    info_img, bar_chart_bytes, radar_chart_bytes
                )
                print(f"      组合图片大小: {len(combined_image_bytes)} bytes")
                
                # 保存到文件
                output_file = f"test_project_{project_id}.png"
                with open(output_file, 'wb') as f:
                    f.write(combined_image_bytes)
                print(f"\n✅ 成功！图片已保存到: {output_file}")
                
            except Exception as e:
                print(f"\n❌ 生成图片失败: {e}")
                import traceback
                traceback.print_exc()
                
        except Exception as e:
            print(f"\n❌ 测试失败: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_export_image())

