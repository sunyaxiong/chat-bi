#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
字段映射配置生成脚本
读取Excel文件中的测点映射关系，生成field_mapping.json配置文件
"""

import pandas as pd
import json
import os
from pathlib import Path

def read_mapping_excel(excel_path):
    """
    读取Excel文件中的映射关系
    
    Args:
        excel_path: Excel文件路径
        
    Returns:
        dict: 映射关系字典
    """
    try:
        # 读取Excel文件的所有sheet
        excel_file = pd.ExcelFile(excel_path)
        mapping_data = {}
        
        for sheet_name in excel_file.sheet_names:
            print(f"处理sheet: {sheet_name}")
            df = pd.read_excel(excel_path, sheet_name=sheet_name)
            
            # Excel格式：测点中文 | 测点 | 上传存储单位
            for _, row in df.iterrows():
                if pd.isna(row.iloc[0]) or pd.isna(row.iloc[1]):  # 跳过空行
                    continue
                    
                point_name = str(row.iloc[0]).strip()  # 测点中文
                point_code = str(row.iloc[1]).strip()  # 测点编码
                unit = str(row.iloc[2]).strip() if len(row) > 2 and not pd.isna(row.iloc[2]) else ""  # 上传存储单位
                
                # 生成别名（将中文名称转换为英文别名）
                alias = generate_alias(point_name, point_code)
                
                # 使用sheet名称作为设备类型分组
                device_type = sheet_name
                if device_type not in mapping_data:
                    mapping_data[device_type] = {}
                
                mapping_data[device_type][point_code] = {
                    "name": point_name,
                    "alias": alias,
                    "unit": unit,
                    "data_type": "double",  # 默认为double类型
                    "description": point_name,
                    "sheetname": sheet_name  # 添加sheet名称字段
                }
        
        return mapping_data
        
    except Exception as e:
        print(f"读取Excel文件失败: {e}")
        import traceback
        traceback.print_exc()
        return {}

def generate_alias(point_name, point_code):
    """
    根据测点名称生成英文别名
    
    Args:
        point_name: 中文测点名称
        point_code: 测点编码
        
    Returns:
        str: 英文别名
    """
    # 简单的中英文映射规则
    name_mapping = {
        "日馈网电量": "daily_grid_power",
        "总馈网电量": "total_grid_power",
        "日发电量": "daily_generation",
        "总发电量": "total_generation",
        "总视在功率": "total_apparent_power",
        "理论发电小时数": "theoretical_generation_hours",
        "日理论发电量": "daily_theoretical_generation",
        "功率": "power",
        "电压": "voltage",
        "电流": "current",
        "温度": "temperature",
        "湿度": "humidity",
        "状态": "status",
        "小时数": "hours",
        "视在功率": "apparent_power"
    }
    
    # 尝试匹配已知映射
    for chinese, english in name_mapping.items():
        if chinese in point_name:
            return english
    
    # 如果没有匹配，使用编码生成别名
    return f"p{point_code}"

def generate_field_mapping_json(mapping_data, output_path):
    """
    生成field_mapping.json配置文件
    
    Args:
        mapping_data: 映射数据
        output_path: 输出文件路径
    """
    # 构建简化的K-V映射
    simple_mapping = {}
    
    for sheet_name, points in mapping_data.items():
        for code, point_info in points.items():
            simple_mapping[code] = point_info["name"]
        print(f"Sheet '{sheet_name}': {len(points)} 个测点")
    
    # 写入简化的JSON文件
    try:
        print(f"写入简化JSON文件到: {output_path}")
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(simple_mapping, f, ensure_ascii=False, indent=2)
        print(f"✓ 成功生成简化映射文件: {output_path}")
        print(f"✓ 共处理 {len(simple_mapping)} 个测点映射")
        
    except Exception as e:
        print(f"✗ 写入映射文件失败: {e}")
        import traceback
        traceback.print_exc()

def generate_simple_mapping_json(mapping_data, output_path):
    """
    生成简化版field_mapping.json - 仅包含编码到名称的映射
    
    Args:
        mapping_data: 映射数据
        output_path: 输出文件路径
    """
    # 构建简化的K-V映射
    simple_mapping = {}
    
    for sheet_name, points in mapping_data.items():
        for code, point_info in points.items():
            simple_mapping[code] = point_info["name"]
    
    # 生成简化版文件路径
    simple_output_path = output_path.parent / "field_mapping_simple.json"
    
    try:
        print(f"写入简化JSON文件到: {simple_output_path}")
        with open(simple_output_path, 'w', encoding='utf-8') as f:
            json.dump(simple_mapping, f, ensure_ascii=False, indent=2)
        print(f"✓ 成功生成简化映射文件: {simple_output_path}")
        print(f"✓ 简化版包含 {len(simple_mapping)} 个测点映射")
        
    except Exception as e:
        print(f"✗ 写入简化映射文件失败: {e}")
        import traceback
        traceback.print_exc()

def main():
    """主函数"""
    # 设置路径
    base_dir = Path(__file__).parent
    mapping_source_dir = base_dir / "prompt" / "mapping-source"
    excel_path = mapping_source_dir / "不同设备类型的测点及测点名称映射关系样例.xlsx"
    output_path = mapping_source_dir / "field_mapping.json"  # 与Excel同目录
    
    print("开始处理字段映射...")
    print(f"Excel文件路径: {excel_path}")
    print(f"输出文件路径: {output_path}")
    print(f"当前工作目录: {Path.cwd()}")
    print(f"脚本所在目录: {base_dir}")
    
    # 检查Excel文件是否存在
    if not excel_path.exists():
        print(f"错误: Excel文件不存在 - {excel_path}")
        print(f"检查目录内容:")
        if mapping_source_dir.exists():
            for file in mapping_source_dir.iterdir():
                print(f"  - {file.name}")
        else:
            print(f"  mapping-source 目录不存在")
        return
    
    # 确保输出目录存在
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 读取Excel映射数据
    print("开始读取Excel文件...")
    mapping_data = read_mapping_excel(excel_path)
    
    if not mapping_data:
        print("未读取到任何映射数据")
        return
    
    # 生成JSON配置文件
    print("开始生成JSON文件...")
    generate_field_mapping_json(mapping_data, output_path)
    
    # 生成简化版JSON文件
    print("开始生成简化版JSON文件...")
    generate_simple_mapping_json(mapping_data, output_path)
    
    # 验证文件是否生成成功
    if output_path.exists():
        file_size = output_path.stat().st_size
        print(f"✓ JSON文件生成成功，文件大小: {file_size} 字节")
    else:
        print("✗ JSON文件生成失败")
    
    print("字段映射处理完成!")

if __name__ == "__main__":
    main()