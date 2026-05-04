"""
数据库服务工厂模块
"""

from typing import Optional

from src.ntchat_bot.settings import DATABASE_TYPE


class DatabaseServiceFactory:
    """数据库服务工厂"""
    
    _instance = None
    
    @staticmethod
    def get_service(db_type: Optional[str] = None):
        """
        获取数据库服务实例
        
        Args:
            db_type: 数据库类型 ('sqlite' 或 'mysql')，默认从配置读取
        
        Returns:
            数据库服务实例
        """
        if db_type is None:
            db_type = DATABASE_TYPE
        
        if db_type == 'mysql':
            from .mysql_service import MySQLService
            return MySQLService()
        else:
            from .sqlite_service import SQLiteService
            return SQLiteService()