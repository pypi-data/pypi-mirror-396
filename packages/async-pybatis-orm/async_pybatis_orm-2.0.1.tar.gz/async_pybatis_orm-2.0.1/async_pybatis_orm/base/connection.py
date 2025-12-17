"""数据库连接管理"""

import os
from databases import Database
from .database_manager import DatabaseAdapter


class DatabaseManager:
    """数据库管理器"""

    _adapter: DatabaseAdapter = None
    _database: Database = None

    @classmethod
    async def initialize(cls, database_url: str = None):
        """
        初始化数据库连接

        Args:
            database_url: 数据库连接URL，如果为None则使用配置中的URL
        """
        if cls._adapter is not None:
            return cls._adapter

        # 从环境变量中获取数据库连接URL
        db_url = database_url or os.getenv("DATABASE_URL")
        if not db_url:
            raise ValueError("数据库连接URL未配置")

        # 创建数据库连接
        cls._database = Database(db_url)
        await cls._database.connect()

        # 创建数据库适配器
        cls._adapter = DatabaseAdapter(cls._database)

        return cls._adapter

    @classmethod
    async def close(cls):
        """关闭数据库连接"""
        if cls._database is not None:
            await cls._database.disconnect()
            cls._database = None
            cls._adapter = None

    @classmethod
    def get_adapter(cls) -> DatabaseAdapter:
        """获取数据库适配器"""
        if cls._adapter is None:
            raise RuntimeError("数据库连接未初始化，请先调用 initialize()")
        return cls._adapter
