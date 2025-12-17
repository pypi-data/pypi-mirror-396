#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
分页结果模型

定义 MyBatis-Plus 风格的 PageResult 类
"""

from typing import Any, List, Optional, TypeVar, Generic
from .page import Page

T = TypeVar("T")

class PageResult(Generic[T]):
    """MyBatis-Plus 风格的分页结果
    
    Attributes:
        records: 当前页的数据列表
        total: 总记录数
        current: 当前页号
        size: 页大小
        
    Example:
        ```python
        result = PageResult(
            records=[user1, user2, user3],
            total=100,
            current=1, 
            size=10
        )
        
        print(f"总共 {result.total} 条记录")
        print(f"当前第 {result.current} 页")
        print(f"每页 {result.size} 条")
        print(f"总共 {result.pages} 页")
        print(f"是否还有下一页: {result.has_next}")
        print(f"是否还有上一页: {result.has_prev}")
        ```
    """

    def __init__(
        self, 
        records: List[T], 
        total: int, 
        current: int, 
        size: int
    ):
        self.records = records
        self.total = total
        self.current = current
        self.size = size

    @property
    def pages(self) -> int:
        """总页数"""
        return (self.total + self.size - 1) // self.size

    @property
    def has_next(self) -> bool:
        """是否有下一页"""
        return self.current < self.pages

    @property
    def has_prev(self) -> bool:
        """是否有上一页"""
        return self.current > 1

    @property
    def next_page_num(self) -> Optional[int]:
        """下一页页码"""
        if self.has_next:
            return self.current + 1
        return None

    @property
    def prev_page_num(self) -> Optional[int]:
        """上一页页码"""
        if self.has_prev:
            return self.current - 1
        return None

    def to_page(self) -> Page:
        """转换为 Page 对象"""
        return Page(current=self.current, size=self.size, total=self.total)

    def get_view_data(self) -> dict:
        """获取前端常用的分页数据"""
        return {
            "records": self.records,
            "total": self.total,
            "current": self.current,
            "size": self.size,
            "pages": self.pages,
            "has_next": self.has_next,
            "has_prev": self.has_prev,
            "next_page": self.next_page_num,
            "prev_page": self.prev_page_num,
        }

    def __str__(self) -> str:
        """字符串表示"""
        return f"PageResult(records={len(self.records)}, total={self.total}, current={self.current}, size={self.size})"

    def __repr__(self) -> str:
        """详细字符串表示"""
        return f"PageResult(records={len(self.records)} items, total={self.total}, current={self.current}/{self.pages}, size={self.size})"
