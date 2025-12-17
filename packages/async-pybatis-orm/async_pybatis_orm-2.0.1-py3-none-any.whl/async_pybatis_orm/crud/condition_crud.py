#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
条件查询扩展

实现 list_by_condition、page_query 等方法
对齐 MyBatis-Plus 的 QueryWrapper/Page 功能
"""

from typing import Any, List, Optional, TYPE_CHECKING
from .base_crud import MyBatisStyleCRUD
from ..pagination.page import Page
from ..pagination.page_result import PageResult

if TYPE_CHECKING:
    from ..wrapper.query_wrapper import QueryWrapper
    from ..base.base_model import BaseModel


class ConditionCRUD(MyBatisStyleCRUD):
    """条件查询扩展"""

    @classmethod
    async def list_by_condition(cls, wrapper: Optional["QueryWrapper"] = None) -> List["BaseModel"]:
        """根据条件查询列表
        
        Args:
            wrapper: 查询条件构造器
            
        Returns:
            List[BaseModel]: 查询结果列表
            
        Example:
            ```python
            # 查询用户名包含 'admin' 的用户
            wrapper = QueryWrapper().like('username', 'admin')
            users = await User.list_by_condition(wrapper)
            ```
        """
        sql, params = cls._build_select_sql(wrapper)
        result = await cls._execute_query(sql, params, sql_type="query")
        return [cls.from_dict(row, from_db=True) for row in result]

    @classmethod
    async def page_query(cls, page: Page, wrapper: Optional["QueryWrapper"] = None) -> PageResult:
        """分页查询
        
        Args:
            page: 分页参数
            wrapper: 查询条件构造器
            
        Returns:
            PageResult: 分页结果
            
        Example:
            ```python
            # 分页查询前10条用户
            page = Page(current=1, size=10)
            wrapper = QueryWrapper().eq('status', 'active')
            result = await User.page_query(page, wrapper)
            
            print(f"总数: {result.total}")
            print(f"当前页: {result.current}")
            print(f"每页: {result.size}")
            print(f"数据: {result.records}")
            ```
        """
        # 先查询总数
        count_sql, count_params = cls._build_count_sql(wrapper)
        total = await cls._execute_query(count_sql, count_params, sql_type="count")

        # 再查询数据
        sql, params = cls._build_select_sql(
            wrapper, limit=page.size, offset=(page.current - 1) * page.size
        )
        result = await cls._execute_query(sql, params, sql_type="query")
        
        records = [cls.from_dict(row, from_db=True) for row in result]

        return PageResult(
            records=records, 
            total=total, 
            current=page.current, 
            size=page.size
        )

    @classmethod
    def _build_select_sql(
            cls,
            wrapper: Optional["QueryWrapper"] = None,
            select_fields: List[str] = None,
            limit: int = None,
            offset: int = None,
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
        if select_fields:
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

        return sql, params

    @classmethod
    def _build_count_sql(cls, wrapper: Optional["QueryWrapper"] = None) -> tuple:
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
