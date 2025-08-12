"""
数据源抽象接口和工厂类
支持MySQL和Spark-Hive多种数据源
"""

from abc import ABC, abstractmethod
from typing import Tuple, List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class DataSourceInterface(ABC):
    """数据源抽象接口"""
    
    @abstractmethod
    def execute_sql(self, sql: str) -> Tuple[List[Tuple], int]:
        """执行SQL查询"""
        pass
    
    @abstractmethod
    def close(self):
        """关闭连接"""
        pass


class MySQLDataSource(DataSourceInterface):
    """MySQL数据源实现"""
    
    def __init__(self, config: Dict[str, Any]):
        from .mysql import get_conn, fetch
        self.config = config
        self.get_conn = get_conn
        self.fetch = fetch
        self.conn = None
    
    def execute_sql(self, sql: str) -> Tuple[List[Tuple], int]:
        """执行MySQL查询"""
        if not self.conn:
            self.conn = self.get_conn(
                self.config['host'],
                self.config['port'],
                self.config['user'],
                self.config['pwd'],
                self.config['db']
            )
        
        return self.fetch(sql, self.conn)
    
    def close(self):
        """关闭MySQL连接"""
        if self.conn:
            self.conn.close()
            self.conn = None


class SparkDataSource(DataSourceInterface):
    """Spark-Hive数据源实现"""
    
    def __init__(self, config: Dict[str, Any]):
        from .spark import get_spark_conn, fetch
        self.config = config
        self.get_conn = get_spark_conn
        self.fetch = fetch
        self.conn = None
    
    def execute_sql(self, sql: str) -> Tuple[List[Tuple], int]:
        """执行Spark SQL查询"""
        if not self.conn:
            self.conn = self.get_conn(
                self.config['host'],
                self.config.get('port', 7077),
                self.config.get('user', ''),
                self.config.get('pwd', ''),
                self.config['db']
            )
        
        return self.fetch(sql, self.conn)
    
    def close(self):
        """关闭Spark连接"""
        if self.conn:
            self.conn.close()
            self.conn = None


class DataSourceFactory:
    """数据源工厂类"""
    
    @staticmethod
    def create_datasource(source_type: str, config: Dict[str, Any]) -> DataSourceInterface:
        """
        创建数据源实例
        
        Args:
            source_type: 数据源类型 ('mysql' 或 'spark')
            config: 数据源配置
            
        Returns:
            DataSourceInterface: 数据源实例
        """
        if source_type.lower() == 'mysql':
            return MySQLDataSource(config)
        elif source_type.lower() == 'spark':
            return SparkDataSource(config)
        else:
            raise ValueError(f"Unsupported data source type: {source_type}")
    
    @staticmethod
    def detect_source_type(config: Dict[str, Any]) -> str:
        """
        根据配置自动检测数据源类型
        
        Args:
            config: 数据源配置
            
        Returns:
            str: 数据源类型
        """
        # 如果配置中包含Spark相关字段，判断为Spark
        if 'spark' in config.get('desc', '').lower() or \
           'hive' in config.get('desc', '').lower() or \
           config.get('port') == 7077:
            return 'spark'
        else:
            return 'mysql'