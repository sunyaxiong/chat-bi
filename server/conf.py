import os
import json

mysql_info = dict()
spark_info = dict()
template_info = dict()

def _load_db_conf():
    # 加载MySQL配置
    if len(mysql_info) == 0:
        mysql_host = os.getenv("MYSQL_HOST")
        if mysql_host:
            hosts = mysql_host.split(",")
            ports =  os.getenv("MYSQL_PORT").split(",")
            databases = os.getenv("MYSQL_DATABASE").split(",")
            users = os.getenv("MYSQL_USER").split(",")
            pwds = os.getenv("MYSQL_PWD").split(",")
            keys = os.getenv("MYSQL_KEY").split(",")
            descs =  os.getenv("MYSQL_KEY_STR").split(",")

            for index in range(0, len(keys)):
                mysql_info[keys[index]] = {
                    "host":hosts[index],
                    "port":int(ports[index]),
                    "db":databases[index],
                    "user":users[index],
                    "pwd":pwds[index],
                    "desc":descs[index],
                    "type":"mysql"
                }
    
    # 加载Spark配置
    if len(spark_info) == 0 and os.getenv("SPARK_ENABLED", "false").lower() == "true":
        spark_host = os.getenv("SPARK_HOST")
        if spark_host:
            hosts = spark_host.split(",")
            databases = os.getenv("SPARK_DATABASE", "default").split(",")
            keys = os.getenv("SPARK_KEY").split(",")
            descs = os.getenv("SPARK_KEY_STR").split(",")
            
            for index in range(0, len(keys)):
                spark_info[keys[index]] = {
                    "host":hosts[index],
                    "port":7077,
                    "db":databases[index] if index < len(databases) else "default",
                    "user":"",
                    "pwd":"",
                    "desc":descs[index] if index < len(descs) else keys[index],
                    "type":"spark"
                }

# 定义一个函数来加载.env文件
def load_env(filename='.env'):
    # 确保.env文件存在
    if not os.path.exists(filename):
        raise FileNotFoundError(f"The specified file {filename} was not found.")

    # 读取.env文件中的每行
    with open(filename, 'r', encoding='utf-8') as file:
        for line in file:
            # 忽略注释和空行
            line = line.strip()
            if line and not line.startswith('#'):
                # 分割键和值
                key_value_pair = line.split('=', 1)
                if len(key_value_pair) == 2:
                    key, value = key_value_pair
                    # 将键值对设置为环境变量
                    os.environ[key] = value

def get_env(key:str, default_v:str):
    return os.getenv(key, default_v)

def get_mysql_conf(db_key:str='au')->dict:
    _load_db_conf()

    if db_key in mysql_info:
        return mysql_info[db_key]

    return ValueError(f"db key {db_key} not found")

def get_mysql_conf_by_question(question:str)->list:
    _load_db_conf()
    
    # 合并所有数据源
    all_datasources = {**mysql_info, **spark_info}
    
    # 根据问题关键词匹配数据源
    for key in all_datasources:
        desc_info = all_datasources[key]['desc']
        if question.find(desc_info)>=0:
            return [all_datasources[key]]
    
    # 如果没找到匹配的，优先返回MySQL数据源（向下兼容）
    if mysql_info:
        return [mysql_info[key] for key in mysql_info]
    elif spark_info:
        return [spark_info[key] for key in spark_info]
    else:
        return []


def load_sql_templates():
    sql_template_path = os.getenv("SQL_TEMPLATE_PATH")
    if sql_template_path.startswith("s3://"):
        parts = sql_template_path.split("/")
        bucket_name = parts[2]
        file_folder_kes = "/".join(parts[3:])
        pass

    else:
        result = []
        file_path = f"{os.getcwd()}/{sql_template_path}/summary.json"
        with open(file_path, mode='r', encoding='utf-8') as f:
            summary = json.load(f)

        if summary:
            for item in summary:
                new_file_path = f"{os.getcwd()}/{sql_template_path}/{item['sql']}"
                with open(new_file_path, mode='r', encoding='utf-8') as f:
                    lines = f.readlines()
                    sql = "\n".join(lines)
                    item['content'] = sql

                    template_info[item["question"]] ={
                        "params":item["params"],
                        "content":item["content"]
                    }


def get_sql_templates():
    return template_info
    
                    


    



    
