#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
分页工具

提供 MyBatis-Plus 风格的 PageHelper 功能，简化分页查询
"""

from typing import Any, List, Optional, TYPE_CHECKING
from .page import Page
from .page_result import PageResult

if TYPE_CHECKING:
    from ..base.base_model import BaseModel
    from ..wrapper.query_wrapper import QueryWrapper


class PageHelper:
    """分页工具类，类比 MyBatis-Plus 的 PageHelper
    
    提供多种分页查询的便利方法
    
    Example:
        ```python
        # 方式1：使用静态方法
        result = await PageHelper.page_query(User, Page(current=1, size=10))
        
        # 方式2：使用实例方法配合条件
        page_helper = PageHelper(User)
        result = await page_helper.query_page(Page(current=1, size=10))
        
        # 方式3：分步查询
        count_result = await page_helper.count(QueryWrapper())
        records = await page_helper.query_list(QueryWrapper(), limit=10, offset=0)
        """
    
    def __init__(self, model_class: type["BaseModel"]):
        """初始化分页工具
        
        Args:
            model_class: 模型类
        """
        self._model_class = model_class
    
    async def query_page(
        self, 
        page: Page, 
        wrapper: Optional["QueryWrapper"] = None
    ) -> PageResult:
        """分页查询
        
        Args:
            page: 分页参数
            wrapper: 位置条件构造器
            
        Returns:
            PageResult: 分页结果
        """
        # 先查询总数
        total = await self.count(wrapper)
        
        # 再查询数据
        records = await self.query_list(
            wrapper, 
            limit=page.size, 
            offset=page.offset
        )
        
        return PageResult(
            records=records,
            total=total,
            current=page.current,
            size=page.size
        )
    
    async def count(self, wrapper: Optional["QueryWrapper"] = None) -> int:
        """查询总记录数
        
        Args:
            wrapper: 查询条件构造器
            
        Returns:
            int: 总记录数
        """
        sql, params = self._model_class._build_count_sql(wrapper)
        return await self._model_class._execute_query(sql, params, sql_type="count")
    
    async def query_list(
        self, 
        wrapper: Optional["QueryWrapper"] = None,
        **kwargs
    ) -> List["BaseModel"]:
        """查询列表
        
        Args:
            wrapper: 查询条件构造器
            **kwargs: 其他查询参数（如 limit, offset, select_fields）
            
        Returns:
            List[BaseModel]: 查询结果列表
        """
        sql, params = self._model_class._build_select_sql(wrapper, **kwargs)
        result = await self._model_class._execute_query(sql, params, sql_type="query")
        return [self._model_class.from_dict(row, from_db=True) for row in result]
    
    @staticmethod
    async def page_query(
        model_class: type["BaseModel"], 
        page: Page,
        wrapper: Optional["QueryWrapper"] = None
    ) -> PageResult:
        """静态分页查询方法
        
        Args:
            model_class: 模型类
            page: 分页参数
            wrapper: 查询条件构造器
            
        Returns:
            PageResult: 分页结果
        """
        page_helper = PageHelper(model_class)
        return await page_helper.query_page(page, wrapper)
