# -*- coding: utf-8 -*-
"""
数据导出辅助工具
"""

import csv
import io
from typing import List, Dict, Any
from datetime import datetime


class ExportHelper:
    """数据导出辅助类"""
    
    @staticmethod
    def export_to_csv(
        data: List[Dict[str, Any]],
        columns: List[str],
        filename: str = None
    ) -> tuple[bytes, str]:
        """
        导出数据为CSV格式
        
        Args:
            data: 要导出的数据列表
            columns: 要导出的列名列表
            filename: 文件名（可选）
            
        Returns:
            (csv_content, filename): CSV内容的字节和文件名
        """
        if filename is None:
            filename = f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        # 创建字符串IO对象
        output = io.StringIO()
        
        # 创建CSV写入器
        writer = csv.DictWriter(
            output,
            fieldnames=columns,
            extrasaction='ignore'
        )
        
        # 写入表头
        writer.writeheader()
        
        # 写入数据行
        for row in data:
            # 只保留指定的列
            filtered_row = {k: v for k, v in row.items() if k in columns}
            writer.writerow(filtered_row)
        
        # 获取CSV内容
        csv_content = output.getvalue()
        output.close()
        
        # 转换为字节（使用UTF-8 BOM以便Excel正确识别中文）
        csv_bytes = '\ufeff'.encode('utf-8') + csv_content.encode('utf-8')
        
        return csv_bytes, filename
    
    @staticmethod
    def export_to_txt(
        data: List[Dict[str, Any]],
        columns: List[str],
        filename: str = None,
        separator: str = '\t'
    ) -> tuple[bytes, str]:
        """
        导出数据为TXT格式（制表符分隔）
        
        Args:
            data: 要导出的数据列表
            columns: 要导出的列名列表
            filename: 文件名（可选）
            separator: 分隔符，默认为制表符
            
        Returns:
            (txt_content, filename): TXT内容的字节和文件名
        """
        if filename is None:
            filename = f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        # 创建字符串IO对象
        output = io.StringIO()
        
        # 写入表头
        output.write(separator.join(columns) + '\n')
        
        # 写入数据行
        for row in data:
            values = []
            for col in columns:
                value = row.get(col, '')
                # 转换为字符串
                if value is None:
                    value = ''
                values.append(str(value))
            output.write(separator.join(values) + '\n')
        
        # 获取TXT内容
        txt_content = output.getvalue()
        output.close()
        
        # 转换为字节（使用UTF-8 BOM）
        txt_bytes = '\ufeff'.encode('utf-8') + txt_content.encode('utf-8')
        
        return txt_bytes, filename
    
    @staticmethod
    def export(
        data: List[Dict[str, Any]],
        columns: List[str],
        format: str = 'csv',
        filename: str = None
    ) -> tuple[bytes, str]:
        """
        导出数据（统一接口）
        
        Args:
            data: 要导出的数据列表
            columns: 要导出的列名列表
            format: 导出格式 ('csv' 或 'txt')
            filename: 文件名（可选）
            
        Returns:
            (content, filename): 内容的字节和文件名
        """
        if format.lower() == 'txt':
            return ExportHelper.export_to_txt(data, columns, filename)
        else:
            return ExportHelper.export_to_csv(data, columns, filename)
    
    @staticmethod
    def prepare_export_data(
        items: List[Any],
        column_mapping: Dict[str, str] = None
    ) -> List[Dict[str, Any]]:
        """
        准备导出数据
        
        Args:
            items: 模型对象列表
            column_mapping: 列名映射字典 {model_field: export_column_name}
            
        Returns:
            准备好的数据字典列表
        """
        result = []
        
        for item in items:
            # 将模型转换为字典
            if hasattr(item, 'model_dump'):
                # Pydantic模型
                item_dict = item.model_dump(mode='json')
            elif hasattr(item, '__dict__'):
                # SQLAlchemy模型或普通对象
                item_dict = {
                    k: v for k, v in item.__dict__.items()
                    if not k.startswith('_')
                }
            else:
                item_dict = dict(item)
            
            # 应用列名映射
            if column_mapping:
                mapped_dict = {}
                for model_field, export_name in column_mapping.items():
                    if model_field in item_dict:
                        value = item_dict[model_field]
                        # 处理None值
                        if value is None:
                            value = ''
                        # 处理日期时间
                        elif isinstance(value, datetime):
                            value = value.strftime('%Y-%m-%d %H:%M:%S')
                        mapped_dict[export_name] = value
                result.append(mapped_dict)
            else:
                result.append(item_dict)
        
        return result

