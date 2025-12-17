#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
批量操作扩展

实现 batch_save、batch_update、batch_remove 等方法
对齐 MyBatis-Plus 的批量操作功能
"""

from typing import Any, List, Optional, TYPE_CHECKING
from .base_crud import MyBatisStyleCRUD

if TYPE_CHECKING:
    from ..base.base_model import BaseModel


class BatchCRUD(MyBatisStyleCRUD):
    """批量操作扩展"""

    @classmethod
    async def batch_save(cls, entities: List["BaseModel"], batch_size: int = 1000) -> bool:
        """批量保存实体
        
        Args:
            entities: 实体对象列表
            batch_size: 批次大小，默认1000
            
        Returns:
            bool: 批量保存是否成功
            
        Example:
            ```python
            users = [
                User(username="alice", email="alice@example.com"),
                User(username="bob", email="bob@example.com"),
                User(username="charlie", email="charlie@example.com"),
            ]
            success = await User.batch_save(users)
            ```
        """
        if not entities:
            return True
        
        try:
            # 分批处理
            for i in range(0, len(entities), batch_size):
                batch = entities[i:i + batch_size]
                if not await cls._batch_save_internal(batch):
                    return False
            return True
        except Exception as e:
            print(f"批量保存失败: {e}")
            return False

    @classmethod
    async def _batch_save_internal(cls, entities: List["BaseModel"]) -> bool:
        """内部批量保存实现"""
        if not entities:
            return True

        # 获取第一个实体的字段作为模板
        first_entity = entities[0]
        data_template = first_entity.to_dict(exclude_none=True)

        if not data_template:
            return True

        # 检查所有实体的字段一致性
        all_fields = set(data_template.keys())
        for entity in entities[1:]:
            entity_data = entity.to_dict(exclude_none=True)
            all_fields.update(entity_data.keys())

        # 构建批量插入SQL
        field_order = list(all_fields)
        columns = [cls._get_column_name(field) for field in field_order]
        placeholders = [f":{field}" for field in field_order]

        sql = f"INSERT INTO {cls._table_meta['table_name']} ({', '.join(columns)}) VALUES ({', '.join(placeholders)})"

        # 构建参数数组
        values_list = []
        for entity in entities:
            entity_data = entity.to_dict(exclude_none=True)
            item = {field_name: entity_data.get(field_name) for field_name in field_order}
            values_list.append(item)

        result = await cls._execute_query(sql, values_list, sql_type="insert")
        return (result or 0) > 0

    @classmethod
    async def batch_update(cls, entities: List["BaseModel"], batch_size: int = 1000) -> bool:
        """批量更新实体
        
        Args:
            entities: 实体对象列表（必须包含主键）
            batch_size: 批次大小，默认1000
            
        Returns:
            bool: 批量更新是否成功
            
        Example:
            ```python
            # 查询多个用户并批量更新
            users = await User.list_by_condition(QueryWrapper().in_list('id', [1, 2, 3]))
            for user in users:
                user.status = 'active'
            success = await User.batch_update(users)
            ```
        """
        if not entities:
            return True

        try:
            # 分批处理
            for i in range(0, len(entities), batch_size):
                batch = entities[i:i + batch_size]
                if not await cls._batch_update_internal(batch):
                    return False
            return True
        except Exception as e:
            print(f"批量更新失败: {e}")
            return False

    @classmethod
    async def _batch_update_internal(cls, entities: List["BaseModel"]) -> bool:
        """内部批量更新实现"""
        if not entities:
            return True

        # 获取第一个实体的更新字段作为模板
        first_entity = entities[0]
        update_fields = first_entity.to_dict(exclude_none=True, exclude_unset=True)
        
        # 移除主键字段
        update_fields.pop(cls._table_meta["primary_key"], None)

        if not update_fields:
            return True

        # 检查所有实体的字段一致性
        field_names = set(update_fields.keys())
        
        # 构建批量更新的 CASE WHEN SQL
        primary_key_column = cls._get_column_name(cls._table_meta["primary_key"])
        
        set_clauses = []
        for field_name in field_names:
            column_name = cls._get_column_name(field_name)
            case_statements = []
            
            for i, entity in enumerate(entities):
                entity_data = entity.to_dict(exclude_none=True, exclude_unset=True)
                entity_data.pop(cls._table_meta["primary_key"], None)
                
                if field_name in entity_data:
                    pk_value = getattr(entity, cls._table_meta["primary_key"])
                    param_name = f"{field_name}_{i}"
                    case_statements.append(f"WHEN :pk_{i} THEN :{param_name}")
            
            if case_statements:
                set_clauses.append(f"{column_name} = CASE {primary_key_column} {' '.join(case_statements)} ELSE {column_name} END")

        if not set_clauses:
            return True

        # 构建参数
        params = {}
        
        # 添加CASE WHEN参数
        for i, entity in enumerate(entities):
            params[f"pk_{i}"] = getattr(entity, cls._table_meta["primary_key"])
            
            entity_data = entity.to_dict(exclude_none=True, exclude_unset=True)
            entity_data.pop(cls._table_meta["primary_key"], None)
            
            for field_name in field_names:
                if field_name in entity_data:
                    params[f"{field_name}_{i}"] = entity_data[field_name]

        # 获取所有需要更新的主键值
        pk_values = [getattr(entity, cls._table_meta["primary_key"]) for entity in entities]

        # 构建IN条件
        pk_placeholders = [f":pk_list_{i}" for i in range(len(pk_values))]
        for i, pk_value in enumerate(pk_values):
            params[f"pk_list_{i}"] = pk_value

        sql = f"UPDATE {cls._table_meta['table_name']} SET {', '.join(set_clauses)} WHERE {primary_key_column} IN ({', '.join(pk_placeholders)})"

        result = await cls._execute_query(sql, params, sql_type="update")
        return result > 0

    @classmethod
    async def batch_remove(cls, id_values: List[Any], batch_size: int = 1000) -> bool:
        """批量删除（根据主键）
        
        Args:
            id_values: 主键值列表
            batch_size: 批次大小，默认1000
            
        Returns:
            bool: 批量删除是否成功
            
        Example:
            ```python
            # 批量删除ID为 1, 2, 3 的用户
            success = await User.batch_remove([1, 2, 3])
            ```
        """
        if not id_values:
            return True

        try:
            # 分批处理
            for i in range(0, len(id_values), batch_size):
                batch = id_values[i:i + batch_size]
                if not await cls._batch_remove_internal(batch):
                    return False
            return True
        except Exception as e:
            print(f"批量删除失败: {e}")
            return False

    @classmethod
    async def _batch_remove_internal(cls, id_values: List[Any]) -> bool:
        """内部批量删除实现"""
        if not id_values:
            return True

        primary_key_column = cls._get_column_name(cls._table_meta["primary_key"])
        placeholders = [f":id_{i}" for i in range(len(id_values))]
        
        sql = f"DELETE FROM {cls._table_meta['table_name']} WHERE {primary_key_column} IN ({', '.join(placeholders)})"
        
        params = {f"id_{i}": id_value for i, id_value in enumerate(id_values)}
        
        result = await cls._execute_query(sql, params, sql_type="delete")
        return (result or 0) > 0
