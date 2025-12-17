#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
条件构造器模块

提供 MyBatis-Plus 风格的 QueryWrapper/LambdaQueryWrapper 功能
"""

from .query_wrapper import QueryWrapper, UpdateWrapper

__all__ = [
    "QueryWrapper",
    "UpdateWrapper",
]
