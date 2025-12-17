#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
基础 CRUD 实现

实现 MyBatis-Plus 风格的 get_by_id、save、update_by_id、remove_by_id、list_all 等方法
"""

from typing import Any, List, Optional, TYPE_CHECKING
from ..base.base_model import BaseModel
from ..base.abstracts import AbstractCRUD

if TYPE_CHECKING:
    from ..wrapper.query_wrapper import QueryWrapper


class MyBatisStyleCRUD:
    """MyBatis-Plus 风格的 CRUD 混入类"""

    @classmethod
    async def get_by_id(cls, id_value: Any) -> Optional[BaseModel]:
        """根据主键查询单条记录
        
        Args:
            id_value: 主键值
            
        Returns:
            Optional[BaseModel]: 查询结果，未找到返回 None
            
        Example:
            ```python
            user = await User.get_by_id(1)
            ```
        """
        primary_key_column = cls._get_column_name(cls._table_meta["primary_key"])
        sql = f"SELECT * FROM {cls._table_meta['table_name']} WHERE {primary_key_column} = :id"
        params = {"id": id_value}

        result = await cls._execute_query(sql, params, sql_type="query")
        if result:
            return cls.from_dict(result[0], from_db=True)
        return None

    @classmethod
    async def save(cls, entity: BaseModel) -> bool:
        """保存实体（插入到数据库）
        
        Args:
            entity: 要保存的实体对象
            
        Returns:
            bool: 保存是否成功
            
        Example:
            ```python
            user = User(username="alice", email="alice@example.com")
            success = await User.save(user)
            ```
        """
        data = entity.to_dict(exclude_none=True)

        if not data:
            return True

        columns: List[str] = []
        placeholders: List[str] = []
        params: dict = {}

        for name, value in data.items():
            col = cls._get_column_name(name)
            columns.append(col)
            placeholders.append(f":{name}")
            params[name] = value

        sql = f"INSERT INTO {cls._table_meta['table_name']} ({', '.join(columns)}) VALUES ({', '.join(placeholders)})"
        result = await cls._execute_query(sql, params, sql_type="insert")
        return (result or 0) > 0

    @classmethod
    async def update_by_id(cls, entity: BaseModel) -> bool:
        """根据主键更新记录
        
        Args:
            entity: 包含主键的实体对象
            
        Returns:
            bool: 更新是否成功
            
        Example:
            ```python
            user = await User.get_by_id(1)
            user.username = "alice_updated"
            success = await User.update_by_id(user)
            ```
        """
        # 获取主键值
        primary_key_value = getattr(entity, cls._table_meta["primary_key"], None)
        if primary_key_value is None:
            raise ValueError(f"实体对象必须包含主键 {cls._table_meta['primary_key']} 的值")

        # 获取更新字段
        update_data = entity.to_dict(exclude_none=True, exclude_unset=True)

        # 移除主键字段
        update_data.pop(cls._table_meta["primary_key"], None)

        if not update_data:
            return True

        # 构建 UPDATE SQL
        set_clauses = []
        params = {}

        for field_name, value in update_data.items():
            column_name = cls._get_column_name(field_name)
            param_name = f"update_{field_name}"
            set_clauses.append(f"{column_name} = :{param_name}")
            params[param_name] = value

        primary_key_column = cls._get_column_name(cls._table_meta["primary_key"])
        sql = f"UPDATE {cls._table_meta['table_name']} SET {', '.join(set_clauses)} WHERE {primary_key_column} = :id"
        params["id"] = primary_key_value

        result = await cls._execute_query(sql, params, sql_type="update")
        return result > 0

    @classmethod
    async def remove_by_id(cls, id_value: Any) -> bool:
        """根据主键删除记录
        
        Args:
            id_value: 主键值
            
        Returns:
            bool: 删除是否成功
            
        Example:
            ```python
            success = await User.remove_by_id(1)
            ```
        """
        primary_key_column = cls._get_column_name(cls._table_meta["primary_key"])
        sql = f"DELETE FROM {cls._table_meta['table_name']}" f" WHERE {primary_key_column} = :id"
        params = {"id": id_value}
        result = await cls._execute_query(sql, params, sql_type="delete")
        return (result or 0) > 0

    @classmethod
    async def list_all(cls) -> List[BaseModel]:
        """查询所有记录
        
        Returns:
            List[BaseModel]: 所有记录列表
            
        Example:
            ```python
            users = await User.list_all()
            ```
        """
        sql = f"SELECT * FROM {cls._table_meta['table_name']}"
        result = await cls._execute_query(sql, {}, sql_type="query")
        return [cls.from_dict(row, from_db=True) for row in result]
