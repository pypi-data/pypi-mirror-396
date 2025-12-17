#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
基础条件构造器

提供通用的条件构建功能，QueryWrapper 和 UpdateWrapper 继承此类
"""

from typing import Any, List, Dict, Optional, TypeVar, Generic

T = TypeVar("T", bound="BaseWrapper")


class BaseWrapper(Generic[T]):
    """基础条件构造器，提供通用的条件构建功能"""

    def __init__(self):
        self._conditions: List[Dict[str, Any]] = []
        self._order_by: List[str] = []
        self._group_by: List[str] = []
        self._having: List[Dict[str, Any]] = []
        self._select_fields: List[str] = []
        self._last: Optional[str] = None

    def parse_field(self, field: Any) -> str:
        from async_pybatis_orm.fields import PyBatisField

        if type(field) == PyBatisField:
            return field.column_name
        return field

    # ==================== 比较条件 ====================

    def eq(self, field: Any, value: Any) -> T:
        """等于条件"""
        field_name = self.parse_field(field)
        self._conditions.append({"field": field_name, "operator": "=", "value": value})
        return self

    def ne(self, field: str, value: Any) -> T:
        """不等于条件"""
        field_name = self.parse_field(field)
        self._conditions.append({"field": field_name, "operator": "!=", "value": value})
        return self

    def gt(self, field: str, value: Any) -> T:
        """大于条件"""
        field_name = self.parse_field(field)
        self._conditions.append({"field": field_name, "operator": ">", "value": value})
        return self

    def ge(self, field: str, value: Any) -> T:
        field_name = self.parse_field(field)
        """大于等于条件"""
        self._conditions.append({"field": field_name, "operator": ">=", "value": value})
        return self

    def lt(self, field: str, value: Any) -> T:
        """小于条件"""
        field_name = self.parse_field(field)
        self._conditions.append({"field": field_name, "operator": "<", "value": value})
        return self

    def le(self, field: str, value: Any) -> T:
        """小于等于条件"""
        field_name = self.parse_field(field)
        self._conditions.append({"field": field_name, "operator": "<=", "value": value})
        return self

    # ==================== 模糊和范围条件 ====================

    def like(self, field: str, value: str) -> T:
        """模糊查询（包含）"""
        field_name = self.parse_field(field)
        self._conditions.append(
            {"field": field_name, "operator": "LIKE", "value": f"%{value}%"}
        )
        return self

    def not_like(self, field: str, value: str) -> T:
        """不包含模糊查询"""
        field_name = self.parse_field(field)
        self._conditions.append(
            {"field": field_name, "operator": "NOT LIKE", "value": f"%{value}%"}
        )
        return self

    def like_left(self, field: str, value: str) -> T:
        """左模糊查询（%值）"""
        field_name = self.parse_field(field)
        self._conditions.append(
            {"field": field_name, "operator": "LIKE", "value": f"%{value}"}
        )
        return self

    def like_right(self, field: str, value: str) -> T:
        """右模糊查询（值%）"""
        field_name = self.parse_field(field)
        self._conditions.append(
            {"field": field_name, "operator": "LIKE", "value": f"{value}%"}
        )
        return self

    def in_list(self, field: str, values: List[Any]) -> T:
        """IN 条件"""
        field_name = self.parse_field(field)
        self._conditions.append(
            {"field": field_name, "operator": "IN", "value": values}
        )
        return self

    def not_in(self, field: str, values: List[Any]) -> T:
        """NOT IN 条件"""
        field_name = self.parse_field(field)
        self._conditions.append(
            {"field": field_name, "operator": "NOT IN", "value": values}
        )
        return self

    def between(self, field: str, start: Any, end: Any) -> T:
        """BETWEEN 条件"""
        field_name = self.parse_field(field)
        self._conditions.append(
            {"field": field_name, "operator": "BETWEEN", "value": [start, end]}
        )
        return self

    def not_between(self, field: str, start: Any, end: Any) -> T:
        """NOT BETWEEN 条件"""
        field_name = self.parse_field(field)
        self._conditions.append(
            {"field": field_name, "operator": "NOT BETWEEN", "value": [start, end]}
        )
        return self

    # ==================== NULL 条件 ====================

    def is_null(self, field: str) -> T:
        """IS NULL 条件"""
        field_name = self.parse_field(field)
        self._conditions.append(
            {"field": field_name, "operator": "IS NULL", "value": None}
        )
        return self

    def is_not_null(self, field: str) -> T:
        """IS NOT NULL 条件"""
        field_name = self.parse_field(field)
        self._conditions.append(
            {"field": field_name, "operator": "IS NOT NULL", "value": None}
        )
        return self

    # ==================== 辅助方法 ====================

    def last(self, sql_tail: str) -> T:
        """直接拼接到语句末尾的原始 SQL 片段（谨慎使用）"""
        self._last = sql_tail.strip() if sql_tail else None
        return self

    # ==================== 排序和分组 ====================

    def order_by(self, field: str, desc: bool = False) -> T:
        """排序

        Args:
            field: 字段名
            desc: 是否降序

        Returns:
            T: 返回自身以支持链式调用
        """
        direction = "DESC" if desc else "ASC"
        field_name = self.parse_field(field)
        self._order_by.append(f"{field_name} {direction}")
        return self

    def group_by(self, field: str) -> T:
        """分组"""
        field_name = self.parse_field(field)
        self._group_by.append(field_name)

    def select(self, *fields: str) -> T:
        """指定查询字段（可多次调用，追加字段）

        Example:
            QueryWrapper().select("id", "name").eq("age", 18)
        """
        for f in fields:
            if f and f not in self._select_fields:
                self._select_fields.append(f)
        return self

    def _build_where_clause(self, model_class) -> tuple:
        """构建 WHERE 条件 SQL"""
        if not self._conditions:
            return "", {}

        conditions = []
        params = {}

        for i, condition in enumerate(self._conditions):
            field = condition["field"]
            operator = condition["operator"]
            value = condition["value"]

            column_name = model_class._get_column_name(field)
            param_name = f"where_{column_name}_{i}"

            if operator == "IN":
                # 处理 IN 条件
                placeholders = [f":{param_name}_{j}" for j in range(len(value))]
                conditions.append(f"{column_name} IN ({', '.join(placeholders)})")
                for j, v in enumerate(value):
                    params[f"{param_name}_{j}"] = v
            elif operator == "NOT IN":
                # 处理 NOT IN 条件
                placeholders = [f":{param_name}_{j}" for j in range(len(value))]
                conditions.append(f"{column_name} NOT IN ({', '.join(placeholders)})")
                for j, v in enumerate(value):
                    params[f"{param_name}_{j}"] = v
            elif operator == "BETWEEN":
                # 处理 BETWEEN 条件
                conditions.append(
                    f"{column_name} BETWEEN :{param_name}_start AND :{param_name}_end"
                )
                params[f"{param_name}_start"] = value[0]
                params[f"{param_name}_end"] = value[1]
            elif operator == "NOT BETWEEN":
                # 处理 NOT BETWEEN 条件
                conditions.append(
                    f"{column_name} NOT BETWEEN :{param_name}_start AND :{param_name}_end"
                )
                params[f"{param_name}_start"] = value[0]
                params[f"{param_name}_end"] = value[1]
            elif operator in ["IS NULL", "IS NOT NULL"]:
                # 处理 NULL 条件
                conditions.append(f"{column_name} {operator}")
            else:
                # 处理其他条件
                conditions.append(f"{column_name} {operator} :{param_name}")
                params[param_name] = value

        return " AND ".join(conditions), params
