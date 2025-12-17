#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
字段定义模块

提供 MyBatis-Plus 风格的字段类型和约束
"""

from enum import Enum
from typing import Any, Optional, Dict


class FieldType(Enum):
    """字段类型枚举"""
    PRIMARY_KEY = "primary_key"
    FIELD = "field"


class PyBatisField:
    """扩展的 Field 信息，对齐 MyBatis-Plus 的字段定义"""

    def __init__(
        self,
        default: Any = ...,
        *,
        alias: Optional[str] = None,
        title: Optional[str] = None,
        description: Optional[str] = None,
        gt: Optional[float] = None,
        ge: Optional[float] = None,
        lt: Optional[float] = None,
        le: Optional[float] = None,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
        regex: Optional[str] = None,
        example: Any = ...,
        examples: Optional[Dict[str, Any]] = None,
        deprecated: Optional[bool] = None,
        json_schema_extra: Optional[Dict[str, Any]] = None,
        # PyBatis 扩展属性
        field_type: Optional[FieldType] = None,
        column_name: Optional[str] = None,
        auto_increment: bool = False,
        nullable: bool = True,
        default_value: Any = None,
        auto_update: bool = False,  # 是否在更新时自动刷新（忽略用户值）
        **extra: Any,
    ):
        # Pydantic 兼容属性
        self.default = default
        self.alias = alias
        self.title = title
        self.description = description
        self.gt = gt
        self.ge = ge
        self.lt = lt
        self.le = le
        self.min_length = min_length
        self.max_length = max_length
        self.regex = regex
        self.example = example
        self.examples = examples
        self.deprecated = deprecated
        self.json_schema_extra = json_schema_extra

        # PyBatis 扩展属性
        self.field_type = field_type
        self.column_name = column_name
        self.auto_increment = auto_increment
        self.nullable = nullable
        self.default_value = default_value
        self.auto_update = auto_update

        # 处理额外参数
        for key, value in extra.items():
            setattr(self, key, value)


def PrimaryKey(
    default: Any = None,
    auto_increment: bool = False,
    column_name: Optional[str] = None,
    **kwargs,
) -> Any:
    """主键字段
    
    Args:
        default: 默认值
        auto_increment: 是否自动递增
        column_name: 数据库列名
        **kwargs: 其他字段属性
        
    Returns:
        PyBatisField: 主键字段对象
        
    Example:
        ```python
        class User(BaseModel):
            id: int = PrimaryKey(auto_increment=True)
            
        __table_meta__ = {"table_name": "user", "primary_key": "id"}
        ```
    """
    return PyBatisField(
        default=default,
        field_type=FieldType.PRIMARY_KEY,
        column_name=column_name,
        auto_increment=auto_increment,
        **kwargs,
    )


def Field(
    default: Any = None, 
    column_name: Optional[str] = None, 
    nullable: bool = True,
    auto_update: bool = False,
    **kwargs
) -> Any:
    """普通字段
    
    Args:
        default: 默认值
        column_name: 数据库列名
        nullable: 是否可空
        auto_update: 是否在更新时自动刷新（忽略用户提供的值）
        **kwargs: 其他字段属性
        
    Returns:
        PyBatisField: 字段对象
        
        Example:
            ```python
            from datetime import datetime
            
            class User(BaseModel):
                id: int = PrimaryKey(auto_increment=True)
                username: str = Field(column_name="user_name", max_length=50)
                email: Optional[str] = Field(nullable=True)
                created_at: datetime = Field(default=datetime.now)
                updated_at: datetime = Field(default=datetime.now, auto_update=True)
                
            __table_meta__ = {"table_name": "user", "primary_key": "id"}
            
            # auto_update=True 的字段在每次更新时都会自动刷新为 default 值
            # 即使用户手动设置了 updated_at，更新时也会被覆盖为当前时间
            ```
    """
    return PyBatisField(
        default=default, 
        field_type=FieldType.FIELD, 
        column_name=column_name,
        nullable=nullable,
        auto_update=auto_update,
        **kwargs
    )


# 常用字段类型的便捷定义
String = lambda **kwargs: Field(**kwargs)
Integer = lambda **kwargs: Field(**kwargs) 
Boolean = lambda **kwargs: Field(**kwargs)
DateTime = lambda **kwargs: Field(**kwargs)
Float = lambda **kwargs: Field(**kwargs)
