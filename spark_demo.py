#!/usr/bin/env python3
"""
最小化Spark SQL查询Demo
基于您的Yarn集群和Hudi配置
"""

from pyspark.sql import SparkSession
import os

class SparkSQLDemo:
    def __init__(self):
        self.spark = self._create_spark_session()
    
    def _create_spark_session(self):
        """创建Spark会话，使用您的集群配置"""
        return SparkSession.builder \
            .appName("ChatBI-SparkSQL-Demo") \
            .master("yarn") \
            .config("spark.submit.deployMode", "client") \
            .config("spark.executor.instances", "10") \
            .config("spark.executor.cores", "2") \
            .config("spark.executor.memory", "4G") \
            .config("spark.driver.memory", "10G") \
            .config("spark.dynamicAllocation.enabled", "false") \
            .config("spark.yarn.queue", "plat") \
            .config("hoodie.metadata.enable", "false") \
            .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.hudi.catalog.HoodieCatalog") \
            .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer") \
            .config("spark.sql.extensions", "org.apache.spark.sql.hudi.HoodieSparkSessionExtension") \
            .getOrCreate()
    
    def query(self, sql):
        """执行SQL查询"""
        try:
            df = self.spark.sql(sql)
            result = df.collect()
            columns = df.columns
            
            return {
                "success": True,
                "data": [dict(zip(columns, row)) for row in result],
                "columns": columns,
                "row_count": len(result)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "data": [],
                "columns": [],
                "row_count": 0
            }
    
    def close(self):
        """关闭Spark会话"""
        if self.spark:
            self.spark.stop()

# 使用示例
if __name__ == "__main__":
    # 创建Spark连接
    spark_demo = SparkSQLDemo()
    
    try:
        # 测试查询
        print("测试Spark连接...")
        result = spark_demo.query("SELECT 1 as test_col, 'Hello Spark' as message")
        
        if result['success']:
            print("✓ 连接成功!")
            print(f"查询结果: {result['data']}")
        else:
            print(f"✗ 查询失败: {result['error']}")
        
        # 示例：查看数据库
        print("\n查看可用数据库:")
        result = spark_demo.query("SHOW DATABASES")
        if result['success']:
            for row in result['data']:
                print(f"  - {row}")
        
        # 示例：查看表（如果有的话）
        print("\n查看默认数据库的表:")
        result = spark_demo.query("SHOW TABLES")
        if result['success']:
            for row in result['data']:
                print(f"  - {row}")
                
    finally:
        # 关闭连接
        spark_demo.close()
        print("\nSpark会话已关闭")