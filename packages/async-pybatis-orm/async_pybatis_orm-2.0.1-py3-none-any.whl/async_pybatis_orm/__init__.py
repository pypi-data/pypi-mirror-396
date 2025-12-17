#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
async-pybatis-orm

一个基于 MySQL 异步场景，对齐 MyBatis-Plus 语法风格的 Python ORM 框架。
专注于易用性与可扩展性，为从 Java MyBatis-Plus 转过来的开发者提供熟悉的API。
"""

__version__ = "1.0.0"

# 核心基础层
from .base.base_model import BaseModel

# CRUD 功能层（Mixin 方式）
from .crud.crud_model import CRUDModel
from .base.common_model import CommonModel

# 条件构造器层
from .wrapper.query_wrapper import QueryWrapper
from .base.connection import DatabaseManager

# MyBatis-Plus 风格的快捷导出，方便用户导入
__all__ = [
    # 版本
    "__version__",
    # 基础模型
    "BaseModel",
    "CRUDModel",
    "CommonModel",
    # 条件构造器
    "QueryWrapper",
    "DatabaseManager",
]
