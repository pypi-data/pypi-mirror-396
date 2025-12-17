#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
插入操作 Mixin

提供 MyBatis-Plus 风格的 save、insert 等方法
对齐 Java MyBatis-Plus 的 IService 接口
"""

from typing import Any, Dict, List, TYPE_CHECKING, TypeVar
from ..base.base_model import BaseModel

if TYPE_CHECKING:
    pass

T = TypeVar("T", bound=BaseModel)


class InsertMixin:
    """INSERT 操作相关的 Mixin 类

    提供 MyBatis-Plus 风格的插入方法：
    - save: 保存实体（通用方法）
    - insert: 插入实体
    - insert_batch: 批量插入
    """

    # ==================== INSERT 相关方法 ====================

    @classmethod
    async def save(cls: type[T], entity: T) -> bool:
        """保存实体（通用方法）

        对应 MyBatis-Plus 的 save(entity)
        根据实体是否有主键值决定是插入还是更新

        Args:
            entity: 实体对象

        Returns:
            bool: 保存是否成功

        Example:
            ```python
            user = User(username="alice", email="alice@example.com")
            success = await User.save(user)
            ```
        """
        # 获取主键值
        primary_key_value = getattr(entity, cls._table_meta["primary_key"], None)

        if primary_key_value is None:
            # 没有主键值，执行插入
            primary_key_value = await cls.insert(entity)
            setattr(entity, cls._table_meta["primary_key"], primary_key_value)
            return primary_key_value is not None
        else:
            # 有主键值，先检查是否存在，选择插入或更新
            existing = await cls.select_by_id(primary_key_value)
            if existing:
                # 存在则更新
                return await cls.update_by_id(entity)
            else:
                # 不存在则插入
                return await cls.insert(entity)

    @classmethod
    async def insert(cls: type[T], entity: T) -> bool:
        """插入一条记录

        对应 MyBatis-Plus 的 insert(entity)

        Args:
            entity: 实体对象

        Returns:
            bool: 插入是否成功

        Example:
            ```python
            user = User(username="alice", email="alice@example.com")
            success = await User.insert(user)
            ```
        """
        data = entity.to_dict(exclude_none=True)

        if not data:
            # 无可插入字段，直接返回成功
            return True

        columns: List[str] = []
        placeholders: List[str] = []
        params: Dict[str, Any] = {}

        for name, value in data.items():
            col = cls._get_column_name(name)
            columns.append(col)
            placeholders.append(f":{name}")
            params[name] = value

        sql = f"INSERT INTO {cls._table_meta['table_name']} ({', '.join(columns)}) VALUES ({', '.join(placeholders)})"
        result = await cls._execute(sql, params)
        return result

    @classmethod
    async def insert_batch(
        cls: type[T], entities: List[T], batch_size: int = 1000
    ) -> bool:
        """批量插入

        对应 MyBatis-Plus 的 saveBatch(list)

        Args:
            entities: 实体对象列表
            batch_size: 批次大小，默认1000

        Returns:
            bool: 批量插入是否成功

        Example:
            ```python
            users = [
                User(username="alice", email="alice@example.com"),
                User(username="bob", email="bob@example.com"),
            ]
            success = await User.insert_batch(users)
            ```
        """
        if not entities:
            return True

        # 分批处理
        for i in range(0, len(entities), batch_size):
            batch = entities[i : i + batch_size]
            if not await cls._insert_batch_internal(batch):
                return False
        return True

    @classmethod
    async def _insert_batch_internal(cls: type[T], entities: List[T]) -> bool:
        """内部批量插入实现，使用单条 SQL + 参数数组执行"""
        if not entities:
            return True

        # 统一可插入字段集合：合并所有实体非 None 字段
        all_fields: set = set()

        for entity in entities:
            data = entity.to_dict(exclude_none=True)
            all_fields.update(data.keys())

        if not all_fields:
            return True

        # 列顺序与占位符（列名用于 SQL，参数名使用字段名）
        field_order = list(all_fields)
        columns = [cls._get_column_name(f) for f in field_order]
        placeholders = [f":{f}" for f in field_order]

        sql = (
            f"INSERT INTO {cls._table_meta['table_name']} "
            f"({', '.join(columns)}) VALUES ({', '.join(placeholders)})"
        )

        # 构建参数数组：缺失字段补 None
        values_list: List[Dict[str, Any]] = []
        for entity in entities:
            data = entity.to_dict(exclude_none=True)
            item = {fname: data.get(fname, None) for fname in field_order}
            values_list.append(item)

        # 交由统一执行函数：params 为数组 -> execute_many
        result = await cls._execute(sql, values_list)
        return (result or 0) > 0

    # ==================== MyBatis-Plus 风格别名 ====================

    @classmethod
    async def batch_save(
        cls: type[T], entities: List[T], batch_size: int = 1000
    ) -> bool:
        """批量保存（别名方法）

        等同于 insert_batch，对齐 MyBatis-Plus 的 saveBatch
        """
        return await cls.insert_batch(entities, batch_size)
