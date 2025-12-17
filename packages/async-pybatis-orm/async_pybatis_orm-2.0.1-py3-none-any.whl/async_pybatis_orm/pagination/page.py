#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
分页模型

定义 MyBatis-Plus 风格的 Page 类
"""

from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class Page:
    """MyBatis-Plus 风格的分页参数
    
    Attributes:
        current: 当前页号（从1开始）
        size: 页大小
        total: 总记录数（可选，通常由查询时设置）
        
    Example:
        ```python
        # 分页查询第1页，每页10条
        page = Page(current=1, size=10)
        
        # 分页查询第2页，每页20条
        page = Page(current=2, size=20)
        ```
    """
    current: int = 1
    size: int = 10
    total: Optional[int] = None
    
    def __post_init__(self):
        """初始化后验证参数"""
        if self.current < 1:
            self.current = 1
        if self.size < 1:
            self.size = 10
    
    @property 
    def offset(self) -> int:
        """计算偏移量"""
        return (self.current - 1) * self.size
    
    @property
    def pages(self) -> Optional[int]:
        """总页数"""
        if self.total is None:
            return None
        return (self.total + self.size - 1) // self.size
    
    @property
    def has_next(self) -> bool:
        """是否有下一页"""
        if self.total is None:
            return True
        return self.current < self.pages
    
    @property 
    def has_prev(self) -> bool:
        """是否有上一页"""
        return self.current > 1
    
    def next_page(self) -> "Page":
        """获取下一页"""
        return Page(current=self.current + 1, size=self.size, total=self.total)
    
    def prev_page(self) -> "Page":
        """获取上一页"""
        if self.current > 1:
            return Page(current=self.current - 1, size=self.size, total=self.total)
        return self
    
    def first_page(self) -> "Page":
        """获取第一页"""
        return Page(current=1, size=self.size, total=self.total)
    
    def last_page(self) -> Optional["Page"]:
        """获取最后一页"""
        if self.pages is None:
            return None
        return Page(current=self.pages, size=self.size, total=self.total)
    
    def __str__(self) -> str:
        """字符串表示"""
        return f"Page(current={self.current}, size={self.size}, total={self.total})"
