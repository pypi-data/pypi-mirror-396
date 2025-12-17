#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
普通条件构造器

支持链式条件拼接，对齐 MyBatis-Plus 的 QueryWrapper 功能
"""

from typing import Any, List, Dict, Optional, TypeVar

from ..wrapper.base_wrapper import BaseWrapper

T = TypeVar("T", bound="QueryWrapper")


class QueryWrapper(BaseWrapper[T]):
    """查询条件构造器，支持链式操作
    
    提供 MyBatis-Plus 风格的查询条件构建方式
    
    Example:
        ```python
        wrapper = QueryWrapper() \
            .eq('status', 'active') \
            .like('username', 'admin') \
            .gt('created_at', '2023-01-01') \
            .order_by('id', desc=True)
        
        users = await User.list_by_condition(wrapper)
        ```
    """

    def __init__(self):
        super().__init__()

    def build_where_clause(self, model_class) -> tuple:
        """构建 WHERE 条件 SQL

        Args:
            model_class: 模型类，用于字段名转列名

        Returns:
            tuple: (where_clause, params)
        """
        return self._build_where_clause(model_class)

    def __str__(self) -> str:
        """字符串表示"""
        conditions_str = ", ".join(
            [f"{c['field']} {c['operator']} {c['value']}" for c in self._conditions]
        )
        return f"QueryWrapper(conditions=[{conditions_str}])"


class UpdateWrapper(BaseWrapper):
    """更新条件构造器，支持链式操作
    
    提供 MyBatis-Plus 风格的更新条件构建方式
    
    Example:
        ```python
        wrapper = UpdateWrapper() \
            .eq('status', 'inactive') \
            .set('status', 'active') \
            .set('updated_at', datetime.now())
        
        success = await User.update_by_wrapper(wrapper)
        ```
    """

    def __init__(self):
        super().__init__()
        self._set_fields: List[Dict[str, Any]] = []

    # ==================== 更新字段设置 ====================

    def set(self, field: str, value: Any) -> "UpdateWrapper":
        """设置更新字段
        
        Args:
            field: 字段名
            value: 值
            
        Returns:
            UpdateWrapper: 返回自身以支持链式调用
            
        Example:
            ```python
            wrapper = UpdateWrapper() \
                .eq('age', 30) \
                .set('status', 1) \
                .set('updated_at', datetime.now())
            ```
        """
        field_name = self.parse_field(field)
        self._set_fields.append({"field": field_name, "value": value})
        return self

    def set_sql(self, field: str, sql_expression: str) -> "UpdateWrapper":
        """设置更新字段（使用 SQL 表达式）
        
        Args:
            field: 字段名
            sql_expression: SQL 表达式，如 "age + 1", "NOW()"
            
        Returns:
            UpdateWrapper: 返回自身以支持链式调用
            
        Example:
            ```python
            wrapper = UpdateWrapper() \
                .eq('status', 'active') \
                .set_sql('age', 'age + 1') \
                .set_sql('updated_at', 'NOW()')
            ```
        """
        field_name = self.parse_field(field)
        self._set_fields.append(
            {"field": field_name, "value": sql_expression, "is_sql": True}
        )
        return self

    # ==================== 辅助方法 ====================

    def last(self, sql_tail: str) -> "UpdateWrapper":
        """直接拼接到语句末尾的原始 SQL 片段（谨慎使用）

        Example:
            UpdateWrapper().eq("status", 1).last("ORDER BY create_time DESC LIMIT 5")
        """
        self._last = sql_tail.strip() if sql_tail else None
        return self

    def build_update_sql(self, model_class) -> tuple:
        """构建 UPDATE SQL

        Args:
            model_class: 模型类，用于字段名转列名

        Returns:
            tuple: (sql, params)
        """
        if not self._set_fields:
            raise ValueError("更新操作必须包含至少一个 SET 字段")

        # 构建 SET 子句
        set_clauses = []
        params = {}

        for i, set_field in enumerate(self._set_fields):
            field = set_field["field"]
            value = set_field["value"]
            is_sql = set_field.get("is_sql", False)

            column_name = model_class._get_column_name(field)

            if is_sql:
                # 直接使用 SQL 表达式
                set_clauses.append(f"{column_name} = {value}")
            else:
                # 使用参数化查询
                param_name = f"set_{field}_{i}"
                set_clauses.append(f"{column_name} = :{param_name}")
                params[param_name] = value

        # 构建 WHERE 子句
        where_clause, where_params = self._build_where_clause(model_class)

        # 组合 SQL
        sql = f"UPDATE {model_class._table_meta['table_name']} SET {', '.join(set_clauses)}"

        if where_clause:
            sql += f" WHERE {where_clause}"
            params.update(where_params)
        else:
            # 没有 WHERE 条件，拒绝更新以避免误操作
            raise ValueError("更新操作必须包含 WHERE 条件")

        if self._last:
            sql += f" {self._last}"

        return sql, params

    def __str__(self) -> str:
        """字符串表示"""
        conditions_str = ", ".join(
            [f"{c['field']} {c['operator']} {c['value']}" for c in self._conditions]
        )
        set_str = ", ".join([f"{s['field']} = {s['value']}" for s in self._set_fields])
        return f"UpdateWrapper(conditions=[{conditions_str}], sets=[{set_str}])"
