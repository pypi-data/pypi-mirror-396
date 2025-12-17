#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
数据库连接管理器

基于 contextvars 和 databases 的事务上下文处理
支持连接池管理和事务隔离
"""

import contextvars
from typing import Optional, Dict, Any, List
from databases import Database
from .abstracts import AbstractDatabase
from .global_config import GlobalConfig


class DatabaseAdapter(AbstractDatabase):
    """Database 适配器，包装 databases.Database"""
    
    def __init__(self, database: Database):
        self._database = database
    
    async def execute(self, sql: str, params: Dict[str, Any] = None) -> Any:
        """执行 SQL 语句"""
        return await self._database.execute(sql, values=params)

    async def execute_many(self, sql: str, params: List[Dict[str, Any]] = None) -> Any:
        """执行 SQL 语句"""
        return await self._database.execute_many(sql, values=params)
    
    async def fetch_all(self, sql: str, params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """查询所有结果"""
        return await self._database.fetch_all(sql, values=params)
    
    async def fetch_one(self, sql: str, params: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """查询单条结果"""
        return await self._database.fetch_one(sql, values=params)
    
    async def fetch_val(self, sql: str, params: Dict[str, Any] = None) -> Any:
        """查询标量值"""
        return await self._database.fetch_val(sql, values=params)
    
    async def transaction(self):
        """事务上下文管理器"""
        return self._database.transaction()


class DatabaseManager:
    """数据库连接管理器"""
    
    _instance: Optional['DatabaseManager'] = None
    _database: Optional[DatabaseAdapter] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @classmethod 
    async def initialize(cls):
        """初始化数据库连接"""
        if not GlobalConfig.is_configured():
            raise RuntimeError("数据库配置未初始化，请先调用 GlobalConfig.configure_database()")
        
        config = GlobalConfig.get_database_config()
        
        # 创建 Database 实例
        database = Database(
            config.url,
            min_size=config.min_size,
            max_size=config.max_size,
            command_timeout=config.command_timeout,
            pool_timeout=config.pool_timeout,
            connection_timeout=config.connection_timeout,
        )
        
        # 创建适配器
        cls._database = DatabaseAdapter(database)
        
        # 连接数据库
        await database.connect()
    
    @classmethod
    def get_database(cls) -> DatabaseAdapter:
        """获取数据库连接"""
        if cls._database is None:
            raise RuntimeError("数据库连接未初始化，请先调用 initialize()")
        return cls._database
    
    @classmethod
    async def close(cls):
        """关闭数据库连接"""
        if cls._database and cls._database._database:
            await cls._database._database.disconnect()
            cls._database = None
