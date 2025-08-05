def format_md(md_sql: str | None) -> str:
    if md_sql and md_sql.startswith('""') and md_sql[2:4] == '""':
        md_sql = md_sql[4:]  # 从第五个字符开始切片
        md_sql = md_sql[:-3]  # 去掉最后三个字符

    # 使用 str.replace() 方法替换字符串
    md_sql = (md_sql.replace('```sql', '')
              .replace('```', '')
              .replace('\n', ' ')
              .replace('"""SELECT', 'SELECT')
              .replace(';"""', ';')
              .strip())  # 使用 strip() 方法去除首尾空白字符

    return md_sql

def format_md2(md_sql: str | None) -> str:
    # 检查 md_sql 是否存在且以双引号开头和结尾
    if md_sql and md_sql.startswith('"""'):
        # 去除开头的三个双引号和结尾的三个双引号
        md_sql = md_sql[3:-3]

    # 定义一个替换规则的字典
    replacements = {
        '```sql': '',  # 替换掉 ```sql
        '```': '',     # 替换掉单独的 ```
        '\n': ' ',      # 替换掉换行符
        '"""SELECT': 'SELECT',  # 替换掉开头的 """SELECT
        ';"""': ';'   # 替换掉结尾的 ;"""
    }

    # 按照字典中的规则进行替换
    for old, new in replacements.items():
        md_sql = md_sql.replace(old, new)

    # 去除首尾空白字符并返回结果
    return md_sql.strip() if md_sql else ""

def format(raw_sql: str) -> str:
    # 定义一个字典，将中文字符映射为英文字符
    char_mapping = {
        '“': '"',  # 中文左双引号
        '”': '"',   # 中文右双引号
        '‘': "'",  # 中文左单引号
        '’': "'",   # 中文右单引号
        '，': ',',  # 中文逗号
    }
    
    # 使用字典推导式和 join() 方法替换所有匹配的字符
    sanitized_sql = ''.join(char_mapping.get(char, char) for char in raw_sql)
    
    return sanitized_sql

def detect_large_in_condition(sql: str) -> dict:
    """检测SQL中是否包含大量IN条件"""
    import re
    import os
    
    max_in_conditions = int(os.getenv("MAX_IN_CONDITIONS", "1000"))
    
    # 查找 IN 条件的正则表达式
    in_pattern = r'\bIN\s*\(([^)]+)\)'
    matches = re.findall(in_pattern, sql, re.IGNORECASE)
    
    for match in matches:
        # 计算逗号数量来估算值的数量
        comma_count = match.count(',')
        value_count = comma_count + 1
        
        if value_count > max_in_conditions:
            return {
                "has_large_in": True,
                "in_values": match.strip(),
                "value_count": value_count
            }
    
    return {"has_large_in": False}

def extract_in_values(in_values_str: str) -> list:
    """从 IN 条件字符串中提取值列表"""
    import re
    
    # 移除引号并按逗号分割
    values = []
    for value in in_values_str.split(','):
        clean_value = value.strip().strip('"').strip("'")
        if clean_value:
            values.append(clean_value)
    
    return values

def build_batched_sql(sql_template: str, values: list, batch_size: int = 500) -> list:
    """将大量IN条件分批构建SQL语句"""
    batched_sqls = []
    
    for i in range(0, len(values), batch_size):
        batch_values = values[i:i + batch_size]
        # 构建 IN 条件字符串
        in_condition = "('" + "', '".join(batch_values) + "')"
        # 替换占位符
        batch_sql = sql_template.replace('{IN_VALUES}', in_condition)
        batched_sqls.append(batch_sql)
    
    return batched_sqls
