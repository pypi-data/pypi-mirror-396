#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
删除操作 Mixin

提供 MyBatis-Plus 风格的 remove、removeById 等方法
对齐 Java MyBatis-Plus 的 IService 接口
"""

from typing import Any, Dict, List, Optional, TYPE_CHECKING, TypeVar
from ..base.base_model import BaseModel
from ..wrapper.query_wrapper import QueryWrapper

if TYPE_CHECKING:
    pass

T = TypeVar("T", bound=BaseModel)


class DeleteMixin:
    """DELETE 操作相关的 Mixin 类

    提供 MyBatis-Plus 风格的删除方法：
    - remove_by_id: 根据主键删除
    - remove_by_ids: 根据主键批量删除
    - remove_by_wrapper: 根据条件删除
    - truncate: 清空表（删除所有数据）
    """

    # ==================== DELETE 相关方法 ====================

    @classmethod
    async def remove_by_id(cls: type[T], id_value: Any) -> bool:
        """根据主键删除记录

        对应 MyBatis-Plus 的 removeById(id)

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
        sql = f"DELETE FROM {cls._table_meta['table_name']} WHERE {primary_key_column} = :id"
        params = {"id": id_value}
        result = await cls._execute(sql, params)
        return (result or 0) > 0

    @classmethod
    async def remove_by_ids(cls: type[T], id_list: List[Any]) -> bool:
        """根据主键批量删除记录

        对应 MyBatis-Plus 的 removeByIds(list)

        Args:
            id_list: 主键值列表

        Returns:
            bool: 删除是否成功

        Example:
            ```python
            success = await User.remove_by_ids([1, 2, 3])
            ```
        """
        if not id_list:
            return True

        primary_key_column = cls._get_column_name(cls._table_meta["primary_key"])
        placeholders = [f":id_{i}" for i in range(len(id_list))]
        sql = f"DELETE FROM {cls._table_meta['table_name']} WHERE {primary_key_column} IN ({', '.join(placeholders)})"

        params = {f"id_{i}": id_value for i, id_value in enumerate(id_list)}
        result = await cls._execute(sql, params)
        return (result or 0) > 0

    @classmethod
    async def remove_by_wrapper(
        cls: type[T], wrapper: Optional[QueryWrapper] = None
    ) -> bool:
        """根据条件删除记录

        对应 MyBatis-Plus 的 remove(wrapper)

        Args:
            wrapper: 删除条件构造器

        Returns:
            bool: 删除是否成功

        Example:
            ```python
            wrapper = QueryWrapper().eq('status', 'inactive')
            success = await User.remove_by_wrapper(wrapper)
            ```
        """
        sql = f"DELETE FROM {cls._table_meta['table_name']}"
        params: Dict[str, Any] = {}

        if wrapper:
            where_sql, where_params = cls._build_where_sql(wrapper)
            if where_sql:
                sql += f" WHERE {where_sql}"
                params.update(where_params)
        else:
            # 没有 wrapper，拒绝删除以避免误操作
            raise ValueError("删除操作必须提供删除条件")

        result = await cls._execute(sql, params)
        return (result or 0) > 0

    @classmethod
    async def truncate(cls: type[T]) -> bool:
        """清空表（删除所有数据）

        TRUNCATE TABLE 会快速删除表中的所有数据，并重置自增计数器。
        注意：此操作不可回滚，请谨慎使用。

        Args:
            无参数

        Returns:
            bool: 操作是否成功

        Example:
            ```python
            success = await User.truncate()
            ```
        """
        sql = f"TRUNCATE TABLE {cls._table_meta['table_name']}"
        result = await cls._execute(sql, {})
        return result is not None

    @classmethod
    async def remove_all(cls: type[T]) -> bool:
        """删除所有数据

        Args:
            无参数

        Returns:
            bool: 操作是否成功
        """
        sql = f"DELETE FROM {cls._table_meta['table_name']}"
        result = await cls._execute(sql, {})
        return result is not None
