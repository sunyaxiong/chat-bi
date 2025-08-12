#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import os
import random
from datetime import datetime, timedelta
import json

def parse_excel_to_schema(excel_path):
    """解析Excel文件生成表结构"""
    xls = pd.ExcelFile(excel_path)
    sheet_names = xls.sheet_names
    
    # 读取summary信息
    df_summary = pd.read_excel(excel_path, sheet_name=0, header=None)
    scenario_name = df_summary.iloc[0, 1]
    scenario_desc = df_summary.iloc[1, 1]
    
    tables = {}
    
    for sheet_name in sheet_names[1:]:  # 跳过summary sheet
        df = pd.read_excel(excel_path, sheet_name=sheet_name, header=None)
        
        table_name = df.iloc[0, 1]
        table_desc = df.iloc[1, 1]
        
        columns = []
        for i in range(4, len(df)):  # 从第5行开始是字段信息
            if pd.isna(df.iloc[i, 0]) or df.iloc[i, 0] == "":
                break
                
            field_name = df.iloc[i, 0]
            field_type = df.iloc[i, 1]
            data_logic = df.iloc[i, 2]
            is_keep = df.iloc[i, 3]
            field_desc = df.iloc[i, 4]
            
            if is_keep != "True":
                continue
                
            columns.append({
                'name': field_name,
                'type': field_type,
                'logic': data_logic,
                'desc': field_desc
            })
        
        tables[table_name] = {
            'desc': table_desc,
            'columns': columns
        }
    
    return scenario_name, tables

def mysql_type_mapping(field_type):
    """将字段类型映射为MySQL类型"""
    type_map = {
        'int': 'INT',
        'bigint': 'BIGINT',
        'varchar': 'VARCHAR(255)',
        'text': 'TEXT',
        'datetime': 'DATETIME',
        'date': 'DATE',
        'decimal': 'DECIMAL(10,2)',
        'float': 'FLOAT',
        'double': 'DOUBLE',
        'tinyint': 'TINYINT',
        'timestamp': 'TIMESTAMP'
    }
    
    field_type_lower = field_type.lower()
    for key, value in type_map.items():
        if key in field_type_lower:
            return value
    
    return 'VARCHAR(255)'  # 默认类型

def generate_sample_data(column_info, num_rows=20):
    """根据字段信息生成样例数据"""
    data = []
    
    for i in range(num_rows):
        row = {}
        for col in column_info:
            field_name = col['name']
            field_type = col['type'].lower()
            field_desc = col['desc']
            
            # 根据字段类型和描述生成数据
            if 'id' in field_name.lower() and 'int' in field_type:
                row[field_name] = i + 1
            elif 'date' in field_type or 'time' in field_type:
                base_date = datetime.now() - timedelta(days=random.randint(0, 365))
                row[field_name] = base_date.strftime('%Y-%m-%d %H:%M:%S')
            elif 'int' in field_type or 'bigint' in field_type:
                row[field_name] = random.randint(1, 1000)
            elif 'decimal' in field_type or 'float' in field_type or 'double' in field_type:
                row[field_name] = round(random.uniform(1.0, 1000.0), 2)
            elif 'varchar' in field_type or 'text' in field_type:
                if '名称' in field_desc or 'name' in field_name.lower():
                    row[field_name] = f"测试{field_name}{i+1}"
                elif '状态' in field_desc:
                    row[field_name] = random.choice(['正常', '异常', '维护'])
                elif '类型' in field_desc:
                    row[field_name] = random.choice(['类型A', '类型B', '类型C'])
                else:
                    row[field_name] = f"数据{i+1}"
            else:
                row[field_name] = f"值{i+1}"
        
        data.append(row)
    
    return data

def generate_sql_files(scenario_name, tables):
    """生成SQL文件"""
    output_dir = f"test_data_{scenario_name}"
    os.makedirs(output_dir, exist_ok=True)
    
    # 生成建表SQL
    create_sql = []
    insert_sql = []
    
    for table_name, table_info in tables.items():
        # 建表语句
        create_sql.append(f"-- 创建表: {table_name}")
        create_sql.append(f"-- 描述: {table_info['desc']}")
        create_sql.append(f"DROP TABLE IF EXISTS `{table_name}`;")
        create_sql.append(f"CREATE TABLE `{table_name}` (")
        
        column_defs = []
        for col in table_info['columns']:
            mysql_type = mysql_type_mapping(col['type'])
            comment = col['desc'].replace("'", "\\'")
            column_def = f"  `{col['name']}` {mysql_type} COMMENT '{comment}'"
            column_defs.append(column_def)
        
        create_sql.append(",\n".join(column_defs))
        create_sql.append(f") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='{table_info['desc']}';")
        create_sql.append("")
        
        # 生成样例数据
        sample_data = generate_sample_data(table_info['columns'])
        
        # 插入语句
        insert_sql.append(f"-- 插入样例数据: {table_name}")
        for row in sample_data:
            columns = list(row.keys())
            values = [f"'{v}'" if isinstance(v, str) else str(v) for v in row.values()]
            insert_stmt = f"INSERT INTO `{table_name}` (`{'`, `'.join(columns)}`) VALUES ({', '.join(values)});"
            insert_sql.append(insert_stmt)
        insert_sql.append("")
    
    # 写入文件
    with open(f"{output_dir}/create_tables.sql", 'w', encoding='utf-8') as f:
        f.write("\n".join(create_sql))
    
    with open(f"{output_dir}/insert_data.sql", 'w', encoding='utf-8') as f:
        f.write("\n".join(insert_sql))
    
    # 生成JSON格式的样例数据
    json_data = {}
    for table_name, table_info in tables.items():
        sample_data = generate_sample_data(table_info['columns'])
        json_data[table_name] = sample_data
    
    with open(f"{output_dir}/sample_data.json", 'w', encoding='utf-8') as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)
    
    print(f"生成的文件保存在目录: {output_dir}/")
    print(f"- create_tables.sql: 建表语句")
    print(f"- insert_data.sql: 插入数据语句")
    print(f"- sample_data.json: JSON格式样例数据")

def main():
    data_dir = "prompt/data"
    
    if not os.path.exists(data_dir):
        print(f"目录 {data_dir} 不存在")
        return
    
    excel_files = [f for f in os.listdir(data_dir) if f.endswith('.xlsx')]
    
    if not excel_files:
        print(f"在 {data_dir} 目录下没有找到Excel文件")
        return
    
    print("找到以下Excel文件:")
    for i, file in enumerate(excel_files):
        print(f"{i+1}. {file}")
    
    # 直接处理所有文件
    files_to_process = excel_files
    
    for excel_file in files_to_process:
        excel_path = os.path.join(data_dir, excel_file)
        print(f"\n处理文件: {excel_file}")
        
        try:
            scenario_name, tables = parse_excel_to_schema(excel_path)
            generate_sql_files(scenario_name, tables)
        except Exception as e:
            print(f"处理文件 {excel_file} 时出错: {e}")

if __name__ == "__main__":
    main()