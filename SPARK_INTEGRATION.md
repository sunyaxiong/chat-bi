# Spark集成指南

## 功能概述

ChatBI现已支持Spark-Hive数据源，可以处理十亿级大数据查询。系统同时支持MySQL和Spark两种数据源，根据问题内容自动选择合适的数据源。

## 配置说明

### 1. 环境变量配置

在`.env`文件中添加以下Spark配置：

```bash
# 启用Spark支持
SPARK_ENABLED=true

# Spark集群配置
SPARK_MASTER=spark://spark-master:7077
HIVE_METASTORE_URI=thrift://hive-metastore:9083
SPARK_WAREHOUSE_DIR=hdfs://namenode:9000/warehouse

# Spark性能配置
SPARK_EXECUTOR_MEMORY=4g
SPARK_EXECUTOR_CORES=2
SPARK_MAX_RESULT_SIZE=2g
SPARK_APP_NAME=ChatBI-Hive-Spark

# Spark数据源配置
SPARK_HOST=spark-master:7077,spark-master:7077
SPARK_DATABASE=warehouse,analytics
SPARK_KEY=warehouse,analytics
SPARK_KEY_STR=数据仓库,分析库
```

### 2. 依赖安装

```bash
# 安装Spark相关依赖
pip install -r requirements_spark.txt

# 或者单独安装
pip install pyspark==3.5.0 py4j==0.10.9.7
```

## 使用方式

### 1. 自动数据源选择

系统会根据问题中的关键词自动选择数据源：

```python
# 包含"数据仓库"关键词，自动选择Spark数据源
"查询数据仓库中的用户行为数据"

# 包含"澳洲"关键词，自动选择MySQL数据源  
"查询澳洲地区的电站信息"

# 没有特定关键词，优先使用MySQL（向下兼容）
"查询所有电站的基本信息"
```

### 2. 支持的SQL语法

Spark数据源完全支持Spark SQL语法：

```sql
-- 复杂查询
SELECT 
    user_id,
    COUNT(*) as event_count,
    MAX(event_time) as last_event
FROM user_events 
WHERE date_partition >= '2024-01-01'
    AND event_type IN ('click', 'view')
GROUP BY user_id
HAVING COUNT(*) > 100
ORDER BY event_count DESC
LIMIT 1000
```

### 3. 大数据优化

系统自动进行以下优化：

- **自动限制结果集**：防止内存溢出
- **分区过滤**：自动添加分区条件（如果检测到分区表）
- **自适应查询**：启用Spark的自适应查询执行
- **结果缓存**：热数据自动缓存

## 架构说明

### 1. 数据源抽象

```
DataSourceInterface (抽象接口)
├── MySQLDataSource (MySQL实现)
└── SparkDataSource (Spark实现)
```

### 2. 连接管理

- **MySQL**: 使用传统的数据库连接池
- **Spark**: 使用SparkSession，支持连接复用

### 3. 查询执行

```python
# 统一的查询接口
def query_db(db_info, sql, user_id, trace_id):
    source_type = db_info.get('type', 'mysql')
    if source_type == 'spark':
        # 使用Spark执行
        return execute_spark_sql(sql)
    else:
        # 使用MySQL执行
        return execute_mysql_sql(sql)
```

## 性能优化

### 1. Spark配置优化

```bash
# 针对大数据场景的推荐配置
SPARK_EXECUTOR_MEMORY=8g
SPARK_EXECUTOR_CORES=4
SPARK_MAX_RESULT_SIZE=4g
SPARK_SQL_ADAPTIVE_ENABLED=true
SPARK_SQL_ADAPTIVE_COALESCE_PARTITIONS_ENABLED=true
```

### 2. 查询优化

- **自动LIMIT**：大查询自动添加LIMIT子句
- **分区裁剪**：自动识别分区表并添加分区过滤
- **列裁剪**：只查询需要的列

### 3. 内存管理

- **结果集限制**：超大结果集自动分页
- **连接复用**：SparkSession复用减少初始化开销
- **垃圾回收**：及时释放不用的资源

## 故障排除

### 1. 常见错误

**PySpark未安装**
```
ImportError: No module named 'pyspark'
解决：pip install pyspark==3.5.0
```

**Hive MetaStore连接失败**
```
Exception: Could not connect to meta store
解决：检查HIVE_METASTORE_URI配置是否正确
```

**内存溢出**
```
OutOfMemoryError: Java heap space
解决：增加SPARK_EXECUTOR_MEMORY和SPARK_MAX_RESULT_SIZE
```

### 2. 调试命令

```bash
# 测试Spark连接
python -c "
from server.db.spark import HiveSparkConnector
conn = HiveSparkConnector()
print('Spark connection successful')
conn.close()
"

# 测试查询
python -c "
from server.db.spark import get_spark_conn, fetch
conn = get_spark_conn('spark-master', 7077, '', '', 'default')
result = fetch('SHOW TABLES', conn)
print(f'Tables: {result}')
"
```

## 兼容性说明

- **向下兼容**：现有MySQL查询完全不受影响
- **配置兼容**：可以只启用MySQL或只启用Spark
- **API兼容**：查询接口保持一致
- **结果兼容**：返回格式统一

## 最佳实践

1. **数据源选择**：大数据分析使用Spark，实时查询使用MySQL
2. **查询优化**：合理使用LIMIT和WHERE条件
3. **资源管理**：根据集群资源调整Spark配置
4. **监控告警**：监控查询性能和资源使用情况