#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
查询操作 Mixin

提供 MyBatis-Plus 风格的 select、get、list 等方法
对齐 Java MyBatis-Plus 的 IService 接口
"""

from typing import Any, Optional, List, TYPE_CHECKING, TypeVar
from ..base.base_model import BaseModel
from ..wrapper.query_wrapper import QueryWrapper
from ..pagination.page import Page
from ..pagination.page_result import PageResult

if TYPE_CHECKING:
    pass

T = TypeVar("T", bound=BaseModel)

class SelectMixin:
    """SELECT 操作相关的 Mixin 类
    
    提供 MyBatis-Plus 风格的查询方法：
    - select_by_id: 根据主键查询
    - select_one: 查询单个对象
    - select_list: 查询列表
    - select_count: 查询总数
    - select_page: 分页查询
    """

    # ==================== 基础查询方法 ====================

    @classmethod
    async def select_by_id(cls: type[T], id_value: Any) -> Optional[T]:
        """根据主键查询单条记录
        
        对应 MyBatis-Plus 的 getById(id)
        
        Args:
            id_value: 主键值
            
        Returns:
            Optional[BaseModel]: 查询结果，未找到返回 None
            
        Example:
            ```python
            user = await User.select_by_id(1)
            ```
        """
        pk_column = cls._get_column_name(cls._table_meta["primary_key"])
        sql = f"SELECT * FROM {cls._table_meta['table_name']} WHERE {pk_column} = :id"
        params = {"id": id_value}

        result = await cls._fetch_all(sql, params)
        if result:
            return cls.from_dict(result[0], from_db=True)  # type: ignore[return-value]
        return None

    @classmethod
    async def select_one(cls: type[T], wrapper: Optional[QueryWrapper] = None) -> Optional[T]:
        """查询单个对象
        
        对应 MyBatis-Plus 的 getOne(wrapper)
        
        Args:
            wrapper: 查询条件构造器
            
        Returns:
            Optional[BaseModel]: 查询结果，未找到返回 None
            
        Example:
            ```python
            wrapper = QueryWrapper().eq('username', 'alice')
            user = await User.select_one(wrapper)
            ```
        """
        sql, params = cls._build_select_sql(wrapper, limit=1)

        result = await cls._fetch_all(sql, params)
        if result:
            return cls.from_dict(result[0], from_db=True)  # type: ignore[return-value]
        return None

    @classmethod
    async def select_list(cls: type[T], wrapper: Optional[QueryWrapper] = None) -> List[T]:
        """查询列表
        
        对应 MyBatis-Plus 的 list(wrapper)
        
        Args:
            wrapper: 查询条件构造器
            
        Returns:
             List[BaseModel]: 查询结果列表
            
        Example:
            ```python
            wrapper = QueryWrapper().eq('status', 'active')
            users = await User.select_list(wrapper)
            ```
        """
        sql, params = cls._build_select_sql(wrapper)

        result = await cls._fetch_all(sql, params)
        return [cls.from_dict(row, from_db=True) for row in result]  # type: ignore[list-item]

    @classmethod
    async def select_count(cls: type[T], wrapper: Optional[QueryWrapper] = None) -> int:
        """查询总记录数
        
        对应 MyBatis-Plus 的 count(wrapper)
        
        Args:
            wrapper: 查询条件构造器
            
        Returns:
            int: 总记录数
            
        Example:
            ```python
            wrapper = QueryWrapper().gt('score', 80)
            count = await User.select_count(wrapper)
            ```
        """
        sql, params = cls._build_count_sql(wrapper)
        # 通过查询来获取 count 值，避免单独的 count 通道
        rows = await cls._fetch_all(sql, params)
        if not rows:
            return 0
        # 兼容不同驱动返回的列名
        first_row = rows[0]
        if isinstance(first_row, dict):
            return int(list(first_row.values())[0])
        return int(first_row[0])

    @classmethod
    async def select_page(cls: type[T], page: Page, wrapper: Optional[QueryWrapper] = None) -> PageResult[T]:
        """分页查询
        
        对应 MyBatis-Plus 的 page(page, wrapper)
        
        Args:
            page: 分页参数
            wrapper: 查询条件构造器
            
        Returns:
            PageResult: 分页结果
            
        Example:
            ```python
            page = Page(current=1, size=10)
            wrapper = QueryWrapper().eq('status', 'active')
            result = await User.select_page(page, wrapper)
            ```
        """
        # 先查询总数
        count_sql, count_params = cls._build_count_sql(wrapper)
        count_rows = await cls._fetch_all(count_sql, count_params)
        if count_rows:
            first_row = count_rows[0]
            if isinstance(first_row, dict):
                total = int(list(first_row.values())[0])
            else:
                total = int(first_row[0])
        else:
            total = 0

        # 再查询数据
        sql, params = cls._build_select_sql(
            wrapper, limit=page.size, offset=(page.current - 1) * page.size
        )
        result = await cls._fetch_all(sql, params)
        
        records = [cls.from_dict(row, from_db=True) for row in result]  # type: ignore[list-item]

        return PageResult(
            records=records, 
            total=total, 
            current=page.current, 
            size=page.size
        )

    # ==================== MyBatis-Plus 风格别名 ====================

    @classmethod
    async def get_by_id(cls: type[T], id_value: Any) -> Optional[T]:
        """根据主键查询（别名方法）
        
        等同于 select_by_id，对齐 MyBatis-Plus 的 getById
        """
        return await cls.select_by_id(id_value)

    @classmethod
    async def get_one(cls: type[T], wrapper: Optional[QueryWrapper] = None) -> Optional[T]:
        """查询单个对象（别名方法）
        
        等同于 select_one，对齐 MyBatis-Plus 的 getOne
        """
        return await cls.select_one(wrapper)

    @classmethod
    async def list_all(cls: type[T]) -> List[T]:
        """查询所有记录
        
        对应 MyBatis-Plus 的 list()
        """
        return await cls.select_list(None)

    @classmethod
    async def list_by_condition(cls: type[T], wrapper: Optional[QueryWrapper] = None) -> List[T]:
        """根据条件查询列表
        
        等同于 select_list，对齐 MyBatis-Plus 的 list(wrapper)
        """
        return await cls.select_list(wrapper)

    @classmethod
    async def count_by_condition(cls: type[T], wrapper: Optional[QueryWrapper] = None) -> int:
        """根据条件查询总数
        
        等同于 select_count，对齐 MyBatis-Plus 的 count(wrapper)
        """
        return await cls.select_count(wrapper)

    @classmethod
    async def page_query(cls: type[T], page: Page, wrapper: Optional[QueryWrapper] = None) -> PageResult[T]:
        """分页查询（别名方法）
        
        等同于 select_page，对齐 MyBatis-Plus 的 page()
        """
        return await cls.select_page(page, wrapper)

    # ==================== SQL 构建方法 ====================

    @classmethod
    def _build_select_sql(
            cls: type[T],
            wrapper: Optional[QueryWrapper] = None,
            select_fields: Optional[List[str]] = None,
            limit: Optional[int] = None,
            offset: Optional[int] = None,
    ) -> tuple:
        """构建 SELECT SQL
        
        Args:
            wrapper: 查询条件构造器
            select_fields: 指定查询的字段列表
            limit: 限制记录数
            offset: 偏移量
            
        Returns:
            tuple: (sql, params)
        """
        # 选择字段
        # 优先使用 wrapper 中指定的选择字段；否则使用入参；都未指定则使用所有模型字段
        if wrapper and getattr(wrapper, "_select_fields", None):
            columns = [cls._get_column_name(field) for field in wrapper._select_fields]
        elif select_fields:
            columns = [cls._get_column_name(field) for field in select_fields]
        else:
            columns = [
                cls._get_column_name(field)
                for field in cls._get_model_fields()
            ]

        sql = f"SELECT {', '.join(columns)} FROM {cls._table_meta['table_name']}"
        params = {}

        # 添加 WHERE 条件
        if wrapper:
            where_sql, where_params = cls._build_where_sql(wrapper)
            if where_sql:
                sql += f" WHERE {where_sql}"
                params.update(where_params)

        # 添加 ORDER BY
        if wrapper and wrapper._order_by:
            sql += f" ORDER BY {', '.join(wrapper._order_by)}"

        # 添加 LIMIT 和 OFFSET
        if limit is not None:
            sql += f" LIMIT {limit}"
        if offset is not None:
            sql += f" OFFSET {offset}"

        # 追加 wrapper.last 原始 SQL 片段（如果存在）
        if wrapper and getattr(wrapper, "_last", None):
            sql += f" {wrapper._last}"

        return sql, params

    @classmethod
    def _build_count_sql(cls: type[T], wrapper: Optional[QueryWrapper] = None) -> tuple:
        """构建 COUNT SQL
        
        Args:
            wrapper: 查询条件构造器
            
        Returns:
            tuple: (sql, params)
        """
        sql = f"SELECT COUNT(*) FROM {cls._table_meta['table_name']}"
        params = {}

        if wrapper:
            where_sql, where_params = cls._build_where_sql(wrapper)
            if where_sql:
                sql += f" WHERE {where_sql}"
                params.update(where_params)

        return sql, params
