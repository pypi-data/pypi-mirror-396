#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
集成模型类

提供完整的 CRUD + 条件查询 + 批量操作功能，对齐 MyBatis-Plus
"""

from ..crud.crud_model import CRUDModel


# 为了向后兼容，保留原有名称
MyBatisModel = CRUDModel

__all__ = [
    "MyBatisModel",  # 主要入口点
    "CRUDModel",     # 实际类名
]