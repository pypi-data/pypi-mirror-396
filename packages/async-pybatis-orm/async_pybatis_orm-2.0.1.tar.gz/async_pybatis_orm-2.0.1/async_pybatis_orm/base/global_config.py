#!/usr/bin/env python3  
# -*- coding: utf-8 -*-

"""
全局配置文件

管理数据库连接池参数、MySQL编码配置等全局设置
"""

from typing import Optional, Dict, Any
from dataclasses import dataclass

@dataclass
class DatabaseConfig:
    """数据库连接配置"""
    url: str
    min_size: int = 5
    max_size: int = 20
    command_timeout: Optional[int] = None
    pool_timeout: Optional[int] = None
    connection_timeout: Optional[int] = None
    
    # MySQL 特定配置
    charset: str = "utf8mb4"
    sql_mode: str = "TRADITIONAL"
    autocommit: bool = True
    connect_timeout: int = 60
    read_timeout: int = 30
    write_timeout: int = 30

class GlobalConfig:
    """全局配置管理"""
    
    _instance: Optional['GlobalConfig'] = None
    _database_config: Optional[DatabaseConfig] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @classmethod
    def configure_database(cls, **kwargs) -> DatabaseConfig:
        """配置数据库连接参数
        
        Args:
            **kwargs: 数据库配置参数
            
        Returns:
            DatabaseConfig: 数据库配置对象
        """
        cls._database_config = DatabaseConfig(**kwargs)
        return cls._database_config
    
    @classmethod
    def get_database_config(cls) -> Optional[DatabaseConfig]:
        """获取数据库配置"""
        return cls._database_config
    
    @classmethod 
    def is_configured(cls) -> bool:
        """检查是否已配置数据库"""
        return cls._database_config is not None
