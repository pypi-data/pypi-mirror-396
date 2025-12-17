#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SQL 构建工具

提供自动 SQL 拼接功能，对齐 MyBatis-Plus 的 SQL 生成逻辑
"""

from typing import Dict, Any, List, Optional, Tuple


class SQLBuilder:
    """SQL 构建器"""
    
    @staticmethod
    def build_select_sql(
        table_name: str,
        columns: Optional[List[str]] = None,
        where_clause: str = "",
        group_by: Optional[List[str]] = None,
        having_clause: str = "",
        order_by: Optional[List[str]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> str:
        """构建 SELECT SQL
        
        Args:
            table_name: 表名
            columns: 查询列，默认 '*'
            where_clause: WHERE 条件子句
            group_by: GROUP BY 列
            having_clause: HAVING 条件子句
            order_by: ORDER BY 列
            limit: 限制记录数
            offset: 偏移量
            
        Returns:
            str: 完整的 SELECT SQL
        """
        # SELECT 子句
        if columns:
            columns_str = ", ".join(columns)
        else:
            columns_str = "*"
        
        sql = f"SELECT {columns_str} FROM {table_name}"
        
        # WHERE 子句
        if where_clause:
            sql += f" WHERE {where_clause}"
        
        # GROUP BY 子句
        if group_by:
            sql += f" GROUP BY {', '.join(group_by)}"
        
        # HAVING 子句
        if having_clause:
            sql += f" HAVING {having_clause}"
        
        # ORDER BY 子句
        if order_by:
            sql += f" ORDER BY {', '.join(order_by)}"
        
        # LIMIT 和 OFFSET 子句
        if limit is not None:
            sql += f" LIMIT {limit}"
        if offset is not None:
            sql += f" OFFSET {offset}"
        
        return sql
    
    @staticmethod
    def build_insert_sql(
        table_name: str,
        data: Dict[str, Any],
        ignore_none: bool = True
    ) -> Tuple[str, Dict[str, Any]]:
        """构建 INSERT SQL
        
        Args:
            table_name: 表名
            data: 数据字典
            ignore_none: 是否忽略 None 值
            
        Returns:
            Tuple[str, Dict[str, Any]]: (SQL, params)
        """
        if not data:
            raise ValueError("插入数据不能为空")
        
        # 选择要插入的字段
        insert_data = data.copy()
        if ignore_none:
            insert_data = {k: v for k, v in data.items() if v is not None}
        
        if not insert_data:
            raise ValueError("插入数据中没有有效值")
        
        columns = list(insert_data.keys())
        placeholders = [f":{col}" for col in columns]
        
        sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(placeholders)})"
        
        return sql, insert_data
    
    @staticmethod
    def build_batch_insert_sql(
        table_name: str,
        data_list: List[Dict[str, Any]],
        ignore_none: bool = True
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """构建批量 INSERT SQL
        
        Args:
            table_name: 表名
            data_list: 数据列表
            ignore_none: 是否忽略 None 值
            
        Returns:
            Tuple[str, List[Dict[str, Any]]]: (SQL, params_list)
        """
        if not data_list:
            raise ValueError("批量插入数据不能为空")
        
        # 获取所有字段
        all_fields = set()
        processed_data_list = []
        
        for data in data_list:
            processed_data = data.copy()
            if ignore_none:
                processed_data = {k: v for k, v in data.items() if v is not None}
            
            all_fields.update(processed_data.keys())
            processed_data_list.append(processed_data)
        
        if not all_fields:
            raise ValueError("批量插入数据中没有有效值")
        
        # 构建字段顺序
        field_order = list(all_fields)
        columns = field_order
        placeholders = [f":{col}" for col in columns]
        
        sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(placeholders)})"
        
        # 构建参数列表
        params_list = []
        for processed_data in processed_data_list:
            params = {field: processed_data.get(field) for field in field_order}
            params_list.append(params)
        
        return sql, params_list
    
    @staticmethod
    def build_update_sql(
        table_name: str,
        data: Dict[str, Any],
        where_clause: str = "",
        ignore_none: bool = True
    ) -> Tuple[str, Dict[str, Any]]:
        """构建 UPDATE SQL
        
        Args:
            table_name: 表名
            data: 更新数据
            where_clause: WHERE 条件子句
            ignore_none: 是否忽略 None 值
            
        Returns:
            Tuple[str, Dict[str, Any]]: (SQL, params)
        """
        # 选择要更新的字段
        update_data = data.copy()
        if ignore_none:
            update_data = {k: v for k, v in data.items() if v is not None}
        
        if not update_data:
            raise ValueError("更新数据中没有有效值")
        
        # 构建 SET 子句
        set_clauses = []
        params = {}
        
        for i, (column, value) in enumerate(update_data.items()):
            param_name = f"update_{i}"
            set_clauses.append(f"{column} = :{param_name}")
            params[param_name] = value
        
        sql = f"UPDATE {table_name} SET {', '.join(set_clauses)}"
        
        # 添加 WHERE 子句
        if where_clause:
            sql += f" WHERE {where_clause}"
        
        return sql, params
    
    @staticmethod
    def build_delete_sql(
        table_name: str,
        where_clause: str = ""
    ) -> str:
        """构建 DELETE SQL
        
        Args:
            table_name: 表名
            where_clause: WHERE 条件子句
            
        Returns:
            str: DELETE SQL
        """
        sql = f"DELETE FROM {table_name}"
        
        if where_clause:
            sql += f" WHERE {where_clause}"
        
        return sql
    
    @staticmethod
    def build_count_sql(
        table_name: str,
        where_clause: str = "",
    ) -> str:
        """构建 COUNT SQL
        
        Args:
            table_name: 表名
            where_clause: WHERE 条件子句
            
        Returns:
            str: COUNT SQL
        """
        sql = f"SELECT COUNT(*) FROM {table_name}"
        
        if where_clause:
            sql += f" WHERE {where_clause}"
        
        return sql
