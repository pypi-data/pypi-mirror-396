#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
基础组件模块

提供模型基类、核心抽象、全局配置等功能
"""

from .base_model import BaseModel
from .abstracts import AbstractCRUD, AbstractDatabase
from .global_config import GlobalConfig

__all__ = [
    "BaseModel",
    "AbstractCRUD", 
    "AbstractDatabase",
    "GlobalConfig",
]
