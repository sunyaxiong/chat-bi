"""
Spark-Hive数据源连接器
支持通过PySpark连接Hive MetaStore进行大数据查询
"""

import os
import logging
from typing import Tuple, List, Any

logger = logging.getLogger(__name__)

class HiveSparkConnector:
    """Spark-Hive连接器"""
    
    def __init__(self):
        self.spark = None
        self._init_spark_session()
    
    def _init_spark_session(self):
        """初始化Spark会话"""
        try:
            from pyspark.sql import SparkSession
            from pyspark.conf import SparkConf
            
            conf = SparkConf()
            conf.set("spark.sql.warehouse.dir", os.getenv("SPARK_WAREHOUSE_DIR", ""))
            conf.set("hive.metastore.uris", os.getenv("HIVE_METASTORE_URI", ""))
            conf.set("spark.sql.adaptive.enabled", "true")
            conf.set("spark.sql.adaptive.coalescePartitions.enabled", "true")
            conf.set("spark.executor.memory", os.getenv("SPARK_EXECUTOR_MEMORY", "4g"))
            conf.set("spark.executor.cores", os.getenv("SPARK_EXECUTOR_CORES", "2"))
            conf.set("spark.driver.maxResultSize", os.getenv("SPARK_MAX_RESULT_SIZE", "2g"))
            
            self.spark = SparkSession.builder \
                .appName(os.getenv("SPARK_APP_NAME", "ChatBI-Hive-Spark")) \
                .master(os.getenv("SPARK_MASTER", "local[*]")) \
                .config(conf=conf) \
                .enableHiveSupport() \
                .getOrCreate()
                
            logger.info("Spark session initialized successfully")
            
        except ImportError:
            logger.error("PySpark not installed. Please install: pip install pyspark")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize Spark session: {e}")
            raise
    
    def execute_sql(self, sql: str) -> Tuple[List[Tuple], int]:
        """
        执行Spark SQL查询
        
        Args:
            sql: SQL查询语句
            
        Returns:
            Tuple[List[Tuple], int]: (查询结果行列表, 行数)
        """
        if not self.spark:
            raise RuntimeError("Spark session not initialized")
        
        try:
            # 优化大数据查询
            optimized_sql = self._optimize_query(sql)
            logger.info(f"Executing Spark SQL: {optimized_sql}")
            
            # 执行查询
            df = self.spark.sql(optimized_sql)
            
            # 检查结果集大小并处理
            row_count = df.count()
            logger.info(f"Query returned {row_count} rows")
            
            # 限制结果集大小防止内存溢出
            max_rows = int(os.getenv("MAX_ROW_COUNT_RETURN", "10"))
            if row_count > max_rows * 10:  # 如果结果集很大，只取样本
                df = df.limit(max_rows * 10)
                logger.warning(f"Large result set detected, limited to {max_rows * 10} rows")
            
            # 转换为Python对象
            rows = df.collect()
            result_rows = [tuple(row) for row in rows]
            
            return result_rows, len(result_rows)
            
        except Exception as e:
            logger.error(f"Spark SQL execution failed: {e}")
            raise
    
    def _optimize_query(self, sql: str) -> str:
        """优化大数据查询"""
        sql_upper = sql.upper()
        
        # 如果没有LIMIT，添加默认限制
        if "LIMIT" not in sql_upper:
            max_rows = int(os.getenv("MAX_ROW_COUNT_RETURN", "10")) * 1000
            sql += f" LIMIT {max_rows}"
        
        # 可以添加更多优化逻辑，如分区过滤等
        return sql
    
    def get_tables(self, database: str = None) -> List[str]:
        """获取数据库表列表"""
        try:
            if database:
                df = self.spark.sql(f"SHOW TABLES IN {database}")
            else:
                df = self.spark.sql("SHOW TABLES")
            
            tables = [row.tableName for row in df.collect()]
            return tables
        except Exception as e:
            logger.error(f"Failed to get tables: {e}")
            return []
    
    def get_table_schema(self, table_name: str, database: str = None) -> List[dict]:
        """获取表结构信息"""
        try:
            full_table_name = f"{database}.{table_name}" if database else table_name
            df = self.spark.sql(f"DESCRIBE {full_table_name}")
            
            schema = []
            for row in df.collect():
                schema.append({
                    "column_name": row.col_name,
                    "data_type": row.data_type,
                    "comment": row.comment if hasattr(row, 'comment') else ""
                })
            return schema
        except Exception as e:
            logger.error(f"Failed to get table schema: {e}")
            return []
    
    def close(self):
        """关闭Spark会话"""
        if self.spark:
            self.spark.stop()
            logger.info("Spark session closed")


def get_spark_conn(host: str, port: int, user: str, pwd: str, database: str):
    """
    获取Spark连接（兼容MySQL接口）
    
    Args:
        host: Spark master地址
        port: 端口（Spark中不使用）
        user: 用户名（Spark中不使用）
        pwd: 密码（Spark中不使用）
        database: 数据库名
        
    Returns:
        HiveSparkConnector: Spark连接器实例
    """
    connector = HiveSparkConnector()
    
    # 如果指定了数据库，切换到该数据库
    if database and database != "default":
        try:
            connector.spark.sql(f"USE {database}")
            logger.info(f"Switched to database: {database}")
        except Exception as e:
            logger.warning(f"Failed to switch to database {database}: {e}")
    
    return connector


def fetch(sql: str, conn: HiveSparkConnector) -> Tuple[List[Tuple], int]:
    """
    执行SQL查询（兼容MySQL接口）
    
    Args:
        sql: SQL查询语句
        conn: Spark连接器
        
    Returns:
        Tuple[List[Tuple], int]: (查询结果, 行数)
    """
    return conn.execute_sql(sql)