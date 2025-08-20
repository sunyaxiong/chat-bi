import boto3
import json
import os
from . import aws
from . import conf

_prompt_cache = dict()
_cache_timestamps = dict()  # 记录文件时间戳

# 从 S3 读取 JSON 文件
def read_conf_from_s3(s3_client, bucket, key):
    try:
        response = s3_client.get_object(Bucket=bucket, Key=key)
        file_content = response['Body'].read().decode('utf-8')
        # 将字符串解码为 JSON 对象
        json_object = json.loads(file_content)
        return json_object
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def get(file_key)->dict:
    # 检查是否需要刷新缓存
    if _should_refresh_cache():
        refresh_cache()
    
    if len(_prompt_cache) == 0:
        refresh_cache()
        
    return _prompt_cache.get(file_key, {})

def _should_refresh_cache()->bool:
    """检查是否需要刷新缓存"""
    for item in ['EXAMPLE_FILE_NAME', 'PROMPT_FILE_NAME', 'RAG_FILE_NAME']:
        key = os.environ[item]
        if os.path.exists(key):
            current_mtime = os.path.getmtime(key)
            cached_mtime = _cache_timestamps.get(item, 0)
            if current_mtime > cached_mtime:
                return True
    return False

def refresh_cache():
    """刷新缓存"""
    global _prompt_cache, _cache_timestamps
    _prompt_cache.clear()
    _cache_timestamps.clear()
    
    for item in ['EXAMPLE_FILE_NAME', 'PROMPT_FILE_NAME', 'RAG_FILE_NAME']:
        key = os.environ[item]
        
        # 优先检查本地文件
        if os.path.exists(key):
            try:
                with open(key, 'r', encoding='utf-8') as f:
                    json_data = json.load(f)
                _cache_timestamps[item] = os.path.getmtime(key)
                print(f"Refreshed {item} from local file: {key}")
            except Exception as e:
                print(f"Error reading local file {key}: {e}")
                json_data = None
        else:
            json_data = None
            
        # 本地文件不存在或读取失败时从S3读取
        if json_data is None:
            try:
                s3_client = aws.get("s3")
                bucket_name = os.environ['BUCKET_NAME']
                json_data = read_conf_from_s3(s3_client, bucket_name, key)
                print(f"Loaded {item} from S3: {key}")
            except Exception as e:
                print(f"Error reading from S3 {key}: {e}")
                json_data = {}
                
        _prompt_cache[item] = json_data

def template_fix_query_error(fmtsql:str, error_str:str):
    p = f"""
    数据库在执行下面sql\n:{fmtsql}\n报如下错误:\n{error_str}。请修改sql从而解决错误。以如下格式返回，并且保证返回的格式能够被转成json对象，不要做其他任何解释。返回的格式:\n
    {{
    "finalSQL":"修复后的SQL",
    "reason":"这样修改的原因"
    }}
    """
    return p


def _build_single_question_prompt()->str:
    p = f"""
    def find_meta(option_question:str)->dict:
        对option_question分析出查询信息集合:option_query_lst, 查询条件集合:option_query_conditions,分析条件集合的时候，需要注意，每个条件必须有一个主语，一个谓语，一个参数，同一个参数只能属于同一个主语
        result['query_count'] = len(option_query_lst)
        result['condition_count'] = len(option_query_lst)

        condition_cache = dict()
        for condition in option_query_conditions:
            对 condition 分析出主语 condition_own,谓语 oper,参数 param
            请尝试理解谓语oper含义，把谓语动词oper 翻译成sql中的条件操作符(例如:=,>,<,in,!=), 举个例子，'是'翻译成=, 但是如果后面的参数是列表，则应该把是翻译成in
            将翻译好的oper赋值给变量operator
            condition_cache[condition_own+operator]=param

        option_query_lst.sort()

        result['conditions'] = condition_cache
        result['querys'] = option_query_lst
        return result  
    """
    return "find_meta", p


def build_template_question_meta_prompt(question:str)->str:
    func_name, func = _build_single_question_prompt()
    p = f"""
    有如下伪代码编写的函数：
    {func}
    *你的任务是，执行函数 {func_name}({question}) 并返回结果,保证返回的结果可以转成json对象,并且不要做任何解释*  
    """
    return p

def build_template_questions_meta_prompt(o_question:list)->str:
    func1_name, func1 = _build_single_question_prompt()
    p = f"""
    有如下两个伪代码编写的函数：
    {func1}
    def find_multiple_meta(option_questions:list)->list:
        result = dict()
        for option_question_item in option_questions:
            option_question = option_question_item['question'] 
            option_params = option_question_item['params'] 
            meta = {func1_name}(option_question)
            result[option_question] = meta
        return result
            
    
    *你的任务是，执行函数 find_multiple_meta({o_question}) 并返回结果,保证返回的结果可以转成json对象,并且不要做任何解释*  
    """
    return p

def build_template_options_question():
    questions = list()
    
    templates = conf.get_sql_templates()
    for key in templates:
        item = templates[key]
        params = item['params']
        questions.append({
            "question":key,
            "params":params
        })

    p = build_template_questions_meta_prompt(questions)
    return p


def template_question(question:str):
    questions = list()
    
    templates = conf.get_sql_templates()
    for key in templates:
        item = templates[key]
        params = item['params']
        questions.append({
            "question":key,
            "params":params
        })

    p = f"""
    备选问题信息集合是如下：
    {questions}
    请注意*每个备选问题包括问题及参数,每个备选问题的参数都是占位符，是一种变量，可以被其他相同类型的数据类型替换*
    用户的问题是：<user_questions>{question}</user_questions>

    有如下伪代码编写的函数：
    def find(user_question, option_questions):
        分析出user_question中要查询的信息集合，赋予变量 query_lst。 查询条件集合赋予变量query_conditions
        for option_question_item in option_questions:
            option_question = option_question_item['question']
            option_question_params =option_question_item['params']
            对option_question分析出查询信息集合 option_query_lst, option_query_conditions
            if len(query_conditions) != len(option_query_conditions):
                continue
            if 对于用户问题的每一个查询条件，当前备选问题的查询条件中，没有任何一个条件的主语和谓语和用户问题的查询条件主语谓语相同(参数可以不同):
                continue

            # 将列表转换为集合
            query_set = set(query_lst)
            option_set = set(option_query_lst)

            if not (query_set 与 option_set 完全相等)
                continue

            if len(query_set) != len(option_set):
                continue
          
            return  {{
            "question":option_question,
            "params":["您从用户的问题中，参考备选问题及它的参数列表，找到的查询参数列表"],
            "reason":"变量query_conditions,option_query_conditions,query_set,option_set的值,以及query_set,option_set是否完全相等",
            "result: True if query_set 完全相等 option_set else False
            }}

        return  {{
            "error":"未能找到匹配的问题",
            "reason":"",
            "result: False
        }}

    *已知<condition>user_query={question}</condition><condition>options={questions}<condition>, 你的任务是请返回 find(user_query, options)的执行结果。 请不要做任何解释，不要修改函数的逻辑,并且保证返回结果能够被转成json对象*
    """
    return p

def template_sql_columns(sql:str,raw_question:str):
 
    p = f"""
    问题:
    {raw_question}对应SQL如下:
    {sql}
    上述sql在数据库中执行后，请分析数据库将返回的数据列,并且根据用户问题和SQL分析这些返回的列是维度还是度量，并以如下格式返回列信息和列对应的维度，度量信息:
    {{
        "columns":["您从sql中发现的需要查询的数据列"],
        "columns_type":["每个列是维度还是度量"]
    }}
    如果sql有语法错误，请返回如下格式的信息：
    {{
        "error":"sql执行错误"
    }}
    注意：请不要返回其他任何信息。
    """
    return p


def template_sql(question:str):
    templates = conf.get_sql_templates()
    if question in templates:
        return templates[question]["content"]

    return ''

def build_large_in_condition_prompt(question: str) -> str:
    """构建处理大量IN条件的提示词"""
    p = f"""
    用户问题：{question}
    
    当需要查询大量SN或ID时，请使用以下方式处理：
    1. 如果检测到需要使用IN条件且数量超过50个，请使用占位符 {{IN_VALUES}}
    2. 在SQL中使用如：WHERE sn IN {{IN_VALUES}}
    3. 在返回结果中添加一个字段 "in_values": [提取的值列表]
    
    请按照正常格式返回，但在SQL中使用占位符处理大量IN条件。
    """
    return p
    