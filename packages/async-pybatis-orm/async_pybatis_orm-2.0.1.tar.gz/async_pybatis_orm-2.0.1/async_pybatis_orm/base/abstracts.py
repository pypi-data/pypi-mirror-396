#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Dict, Any, List, Optional

T = TypeVar("T", bound="BaseModel")

class AbstractDatabase(ABC):
    """数据库操作抽象接口"""
    
    @abstractmethod
    async def execute(self, sql: str, params: Dict[str, Any] = None) -> Any:
        """执行 SQL 语句"""
        pass

    @abstractmethod
    async def execute_many(self, sql: str, params: List[Dict[str, Any]] = None) -> Any:
        """执行 SQL 语句"""
        pass
    
    @abstractmethod
    async def fetch_all(self, sql: str, params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """查询所有结果"""
        pass
    
    @abstractmethod
    async def fetch_one(self, sql: str, params: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """查询单条结果"""
        pass
    
    @abstractmethod
    async def fetch_val(self, sql: str, params: Dict[str, Any] = None) -> Any:
        """查询标量值"""
        pass
    
    @abstractmethod
    async def transaction(self):
        """事务上下文管理器"""
        pass

class AbstractCRUD(ABC):
    """CRUD 操作抽象接口"""
    
    @abstractmethod
    async def get_by_id(self, id_value: Any) -> Optional[T]:
        """根据主键查询"""
        pass
    
    @abstractmethod  
    async def save(self, entity: T) -> bool:
        """保存实体"""
        pass
    
    @abstractmethod
    async def update_by_id(self, entity: T) -> bool:
        """根据主键更新"""
        pass
    
    @abstractmethod
    async def remove_by_id(self, id_value: Any) -> bool:
        """根据主键删除"""
        pass
    
    @abstractmethod
    async def list_all(self) -> List[T]:
        """查询所有记录"""
        pass
