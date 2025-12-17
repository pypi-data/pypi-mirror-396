#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CRUD 模块

提供 MyBatis-Plus 风格的增删改查功能
"""

from .crud_model import CRUDModel
from .select_mixin import SelectMixin
from .insert_mixin import InsertMixin
from .update_mixin import UpdateMixin
from .delete_mixin import DeleteMixin

# 保持向后兼容
from .select_mixin import SelectMixin as MyBatisStyleCRUD
from .condition_crud import ConditionCRUD 
from .batch_crud import BatchCRUD

__all__ = [
    "CRUDModel",
    "SelectMixin",
    "InsertMixin", 
    "UpdateMixin",
    "DeleteMixin",
    # 向后兼容
    "MyBatisStyleCRUD",
    "ConditionCRUD",
    "BatchCRUD",
]